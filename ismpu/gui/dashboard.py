"""Unified local dashboard for the three airborne and five ground PIDs."""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from ismpu.runtime.run_reader import RunReader
from ismpu.runtime.run_recorder import (
    controller_pids,
    gains_snapshot,
    pid_operating_points,
)


@dataclass(frozen=True)
class ViewSpec:
    key: str
    label: str
    pid_key: str
    phase: str


@dataclass(frozen=True)
class GainUpdateRequest:
    request_id: int
    revision: int
    pid_key: str
    gains: dict[str, float]
    created_monotonic: float


VIEW_SPECS = (
    ViewSpec("roll", "Roll", "roll", "approach"),
    ViewSpec("pitch", "Pitch", "pitch", "approach"),
    ViewSpec("flare", "Flare", "pitch", "flare"),
    ViewSpec("air_speed", "Air Speed", "air_speed", "approach"),
    ViewSpec("steer", "Steer", "steer", "ground"),
    ViewSpec("brake_l", "Brake L", "brake_l", "ground"),
    ViewSpec("brake_r", "Brake R", "brake_r", "ground"),
    ViewSpec("reverse_l", "Reverse L", "reverse_l", "ground"),
    ViewSpec("reverse_r", "Reverse R", "reverse_r", "ground"),
)
GROUND_PID_KEYS = frozenset(
    {"steer", "brake_l", "brake_r", "reverse_l", "reverse_r"}
)


def _finite_or_none(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _jsonable(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {
            (key.value if isinstance(key, Enum) else str(key)): _jsonable(item)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    return getattr(value, "value", str(value))


class DashboardState:
    """Thread-safe live state or an immutable CSV replay."""

    def __init__(
        self,
        controller=None,
        *,
        sim=None,
        scenario=None,
        recorder=None,
        tune_enabled: bool = False,
        npgs_active: bool = False,
        max_points: int = 2400,
        export_root: str | Path = "runs/dashboard-exports",
        tuning_queue_size: int = 64,
    ) -> None:
        self.controller = controller
        self.sim = sim
        self.scenario = scenario
        self.recorder = recorder
        self.tune_enabled = bool(tune_enabled)
        self.npgs_active = bool(npgs_active)
        self.export_root = Path(export_root)
        self.started_monotonic = time.monotonic()
        self.points = {
            spec.key: deque(maxlen=max_points) for spec in VIEW_SPECS
        }
        self.timeline = deque(maxlen=512)
        self._last_segment = None
        self._lock = threading.RLock()
        self._tuning_queue: deque[GainUpdateRequest] = deque()
        self._tuning_queue_size = max(1, int(tuning_queue_size))
        self._next_request_id = 1
        self._revision = 0
        self._accept_tuning = True
        self.replay_source = None
        self.replay_summary = None

    @property
    def view_names(self) -> tuple[str, ...]:
        return tuple(spec.label for spec in VIEW_SPECS)

    def capture(self, *, elapsed_s: float | None = None) -> None:
        if self.controller is None:
            return
        elapsed_s = (
            time.monotonic() - self.started_monotonic
            if elapsed_s is None else elapsed_s
        )
        pids = controller_pids(self.controller)
        operating = pid_operating_points(self.controller)
        segment = self.controller.segment.value
        with self._lock:
            if segment != self._last_segment:
                self.timeline.append({
                    "time_s": elapsed_s,
                    "event": "segment",
                    "value": segment,
                })
                self._last_segment = segment
            for spec in VIEW_SPECS:
                pid = pids[spec.pid_key]
                point = {
                    "time_s": elapsed_s,
                    "segment": segment,
                    "value": operating[spec.pid_key]["value"],
                    "setpoint": operating[spec.pid_key]["setpoint"],
                    "error": pid.last_error,
                    "output": pid.last_output,
                    "p": pid.last_p_term,
                    "i": pid.last_i_term,
                    "d": pid.last_d_term,
                    "saturated": bool(
                        pid.last_unconstrained < pid.min_out
                        or pid.last_unconstrained > pid.max_out
                    ),
                    "kp": pid.kp,
                    "ki": pid.ki,
                    "kd": pid.kd,
                }
                self.points[spec.key].append(_jsonable(point))

    def update_gains(self, pid_key: str, gains: dict) -> dict:
        if self.controller is None:
            raise RuntimeError("replay is read-only")
        if not self.tune_enabled:
            raise PermissionError("live tuning is disabled; use --dashboard-tune")
        if self.npgs_active and pid_key in GROUND_PID_KEYS:
            raise PermissionError("NPGS overwrites ground gains every tick")
        pids = controller_pids(self.controller)
        if pid_key not in pids:
            raise KeyError(pid_key)
        clean = {}
        for name in ("kp", "ki", "kd"):
            if name not in gains:
                continue
            value = _finite_or_none(gains[name])
            if value is None:
                raise ValueError(f"{name} must be finite")
            clean[name] = value
        if not clean:
            raise ValueError("at least one of kp, ki, kd is required")
        with self._lock:
            pid = pids[pid_key]
            previous = {name: getattr(pid, name) for name in ("kp", "ki", "kd")}
            for name, value in clean.items():
                setattr(pid, name, value)
            self.controller.config_revision += 1
            self.timeline.append({
                "time_s": time.monotonic() - self.started_monotonic,
                "event": "gains",
                "value": {"pid": pid_key, **clean},
            })
            if self.recorder is not None:
                self.recorder.record_event(
                    "gains",
                    data={"pid": pid_key, "previous": previous,
                          "value": {name: getattr(pid, name) for name in ("kp", "ki", "kd")},
                          "config_revision": self.controller.config_revision},
                    tick_id=self.controller.tick_id,
                    segment=self.controller.segment.value,
                )
            return {"pid": pid_key, "kp": pid.kp, "ki": pid.ki, "kd": pid.kd}

    def enqueue_gain_update(self, pid_key: str, gains: dict) -> dict:
        """Валидировать HTTP-запрос и передать запись control-потоку."""
        if self.controller is None:
            raise RuntimeError("replay is read-only")
        if not self.tune_enabled:
            raise PermissionError("live tuning is disabled; use --dashboard-tune")
        if self.npgs_active and pid_key in GROUND_PID_KEYS:
            raise PermissionError("NPGS overwrites ground gains every tick")
        pids = controller_pids(self.controller)
        if pid_key not in pids:
            raise KeyError(pid_key)
        current = pids[pid_key]
        complete = {"kp": current.kp, "ki": current.ki, "kd": current.kd}
        for name, raw in gains.items():
            if name not in complete:
                continue
            value = _finite_or_none(raw)
            if value is None:
                raise ValueError(f"{name} must be finite")
            complete[name] = value
        if not any(name in gains for name in complete):
            raise ValueError("at least one of kp, ki, kd is required")
        with self._lock:
            if not self._accept_tuning:
                raise RuntimeError("dashboard is shutting down")
            if len(self._tuning_queue) >= self._tuning_queue_size:
                raise OverflowError("tuning queue is full")
            request = GainUpdateRequest(
                request_id=self._next_request_id,
                revision=self._revision + len(self._tuning_queue) + 1,
                pid_key=pid_key,
                gains=complete,
                created_monotonic=time.monotonic(),
            )
            self._next_request_id += 1
            self._tuning_queue.append(request)
            return {
                "status": "pending",
                "request_id": request.request_id,
                "revision": request.revision,
                "pid": pid_key,
            }

    def apply_pending_gain_updates(self) -> list[dict]:
        """Применяется только control-потоком в начале такта."""
        applied: list[dict] = []
        while True:
            with self._lock:
                if not self._tuning_queue:
                    break
                request = self._tuning_queue.popleft()
            try:
                result = self.update_gains(request.pid_key, request.gains)
                with self._lock:
                    self._revision = max(self._revision, request.revision)
                    event = {
                        "status": "applied",
                        "request_id": request.request_id,
                        "revision": request.revision,
                        **result,
                    }
                    self.timeline.append({
                        "time_s": time.monotonic() - self.started_monotonic,
                        "event": "tuning_applied",
                        "value": event,
                    })
                applied.append(event)
            except Exception as exc:
                event = {
                    "status": "rejected",
                    "request_id": request.request_id,
                    "revision": request.revision,
                    "reason": str(exc),
                }
                with self._lock:
                    self.timeline.append({
                        "time_s": time.monotonic() - self.started_monotonic,
                        "event": "tuning_rejected",
                        "value": event,
                    })
                applied.append(event)
        return applied

    def cancel_pending_gain_updates(self) -> None:
        with self._lock:
            self._accept_tuning = False
            while self._tuning_queue:
                request = self._tuning_queue.popleft()
                self.timeline.append({
                    "time_s": time.monotonic() - self.started_monotonic,
                    "event": "tuning_cancelled",
                    "value": {
                        "request_id": request.request_id,
                        "revision": request.revision,
                    },
                })

    def export_gains(self, *, label: str = "dashboard") -> Path:
        if self.controller is None:
            raise RuntimeError("replay does not have live gains to export")
        if self.recorder is not None:
            return self.recorder.export_gains(self.controller, label=label)
        self.export_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        payload = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "backend": getattr(self.sim, "backend_name", "unknown"),
            "aircraft_profile": getattr(
                self.sim, "aircraft_profile_name", "unknown"
            ),
            "scenario": getattr(self.scenario, "scenario_id", None),
            "scenario_definition": (
                self.scenario.to_dict() if self.scenario is not None else None
            ),
            "label": label,
            "gains": gains_snapshot(self.controller),
        }
        path = self.export_root / f"gains-{stamp}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return path

    def payload(self) -> dict:
        with self._lock:
            views = []
            for spec in VIEW_SPECS:
                data = list(self.points[spec.key])
                locked = (
                    self.controller is None
                    or not self.tune_enabled
                    or (self.npgs_active and spec.pid_key in GROUND_PID_KEYS)
                )
                views.append({
                    **asdict(spec),
                    "locked": locked,
                    "latest": data[-1] if data else None,
                    "points": data,
                })
            return {
                "header": self._header(),
                "views": views,
                "timeline": list(self.timeline),
                "replay": {
                    "source": self.replay_source,
                    "summary": self.replay_summary,
                } if self.replay_source else None,
            }

    def _header(self) -> dict:
        telemetry = getattr(self.controller, "last_telemetry", None)
        approach = getattr(getattr(self.controller, "approach_channel", None),
                           "result", None)
        tolerance = getattr(self.controller, "tolerance_report", None)
        scenario_id = getattr(self.scenario, "scenario_id", None)
        return {
            "backend": getattr(self.sim, "backend_name", "replay"),
            "aircraft_profile": getattr(
                self.sim, "aircraft_profile_name", "recorded"
            ),
            "scenario": scenario_id,
            "segment_sources": _jsonable(
                getattr(self.scenario, "provenance", None)),
            "segment_conditions": _jsonable(
                getattr(self.scenario, "conditions", None)),
            "conditions_valid": getattr(self.sim, "conditions_valid", True),
            "condition_matches": _jsonable(
                getattr(self.sim, "condition_matches", ())),
            "segment": getattr(
                getattr(self.controller, "segment", None), "value", None
            ),
            "ils_valid": getattr(telemetry, "ils_valid", None),
            "loc_deviation": getattr(
                getattr(telemetry, "approach_inputs", None),
                "LocDeviation", None,
            ),
            "gs_deviation": getattr(
                getattr(telemetry, "approach_inputs", None),
                "GSDeviation", None,
            ),
            "tolerances": _jsonable(tolerance),
            "approach_criteria_a11": _jsonable(
                self.controller.approach_criteria.verdict()
                if self.controller is not None else None
            ),
            "go_around": getattr(self.controller, "go_around_reason", None),
            "envelope_warnings": _jsonable(
                getattr(approach, "envelope_warnings", ())
            ),
            "tune_enabled": self.tune_enabled,
            "npgs_active": self.npgs_active,
            "recording_failed": bool(getattr(self.recorder, "recording_failed", False)),
            "recording_error": getattr(self.recorder, "recording_error", None),
        }

    @classmethod
    def from_csv(cls, path: str | Path, *, max_points: int = 2400):
        reader = RunReader(path)
        state = cls(max_points=max_points)
        state.replay_source = str(reader.path.resolve())
        count = 0
        first_time = last_time = 0.0
        last_segment = None

        def consume(rows):
            nonlocal count, first_time, last_time, last_segment
            for raw in rows:
                count += 1
                row = {key: _finite_or_none(value) if key != "segment" else value
                       for key, value in raw.items()}
                time_s = row.get("time_s") or 0.0
                if count == 1:
                    first_time = time_s
                last_time = time_s
                segment = raw.get("segment") or "unknown"
                if segment != last_segment:
                    state.timeline.append({
                        "time_s": time_s, "event": "segment", "value": segment})
                    last_segment = segment
                for spec in VIEW_SPECS:
                    prefix = f"pid_{spec.pid_key}_"
                    point = {
                        "time_s": time_s,
                        "segment": segment,
                        "value": row.get(prefix + "value"),
                        "setpoint": row.get(prefix + "setpoint"),
                        "error": row.get(prefix + "error"),
                        "output": row.get(prefix + "output"),
                        "p": row.get(prefix + "p"),
                        "i": row.get(prefix + "i"),
                        "d": row.get(prefix + "d"),
                        "saturated": bool(row.get(prefix + "saturated") or False),
                        "kp": row.get(prefix + "kp"),
                        "ki": row.get(prefix + "ki"),
                        "kd": row.get(prefix + "kd"),
                    }
                    if spec.key == "roll" and point["value"] is None:
                        point["value"] = row.get("roll_deg")
                    elif spec.key in {"pitch", "flare"} and point["value"] is None:
                        point["value"] = row.get("pitch_deg")
                    elif spec.key == "air_speed" and point["value"] is None:
                        point["value"] = row.get("ias_ms")
                    state.points[spec.key].append(point)

        consume(reader.rows())

        state.replay_summary = {
            "rows": count,
            "duration_s": last_time - first_time if count else 0.0,
        }
        return state


class DashboardServer:
    def __init__(
        self,
        state: DashboardState,
        *,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("PID dashboard may bind only to a loopback address")
        self.state = state
        self.httpd = ThreadingHTTPServer((host, port), _handler_factory(state))
        self.thread = None

    @property
    def address(self) -> tuple[str, int]:
        return self.httpd.server_address[:2]

    def start(self) -> "DashboardServer":
        if self.thread is None:
            self.thread = threading.Thread(
                target=self.httpd.serve_forever,
                name="ismpu-pid-dashboard",
                daemon=True,
            )
            self.thread.start()
        return self

    def __enter__(self) -> "DashboardServer":
        return self.start()

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.stop()
        return False

    def stop(self) -> None:
        self.state.cancel_pending_gain_updates()
        if self.thread is not None:
            self.httpd.shutdown()
            self.thread.join(timeout=2.0)
            self.thread = None
        self.httpd.server_close()


def _handler_factory(state: DashboardState):
    html_path = Path(__file__).with_name("dashboard.html")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def _json(self, status: int, payload) -> None:
            body = json.dumps(
                _jsonable(payload), ensure_ascii=False, allow_nan=False
            ).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in {"/", "/dashboard.html"}:
                body = html_path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/state":
                self._json(HTTPStatus.OK, state.payload())
            elif path == "/api/views":
                self._json(HTTPStatus.OK, [asdict(spec) for spec in VIEW_SPECS])
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self):
            path = urlparse(self.path).path
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
                if path.startswith("/api/gains/"):
                    pid_key = unquote(path.rsplit("/", 1)[-1])
                    result = state.enqueue_gain_update(pid_key, payload)
                    self._json(HTTPStatus.ACCEPTED, result)
                elif path == "/api/export":
                    result = state.export_gains(
                        label=str(payload.get("label", "dashboard"))
                    )
                    self._json(HTTPStatus.CREATED, {"path": str(result.resolve())})
                else:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            except PermissionError as exc:
                self._json(HTTPStatus.FORBIDDEN, {"error": str(exc)})
            except KeyError as exc:
                self._json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except RuntimeError as exc:
                self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
            except OverflowError as exc:
                self._json(HTTPStatus.TOO_MANY_REQUESTS, {"error": str(exc)})

    return Handler


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="ИСМПУ PID dashboard")
    parser.add_argument("--replay", required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    state = DashboardState.from_csv(args.replay)
    server = DashboardServer(state, port=args.port).start()
    print(f"Replay dashboard: http://{server.address[0]}:{server.address[1]}")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
