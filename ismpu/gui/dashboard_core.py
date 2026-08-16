"""Один локальный dashboard для live RunRecorder и read-only replay."""

from __future__ import annotations

import argparse
import copy
import json
import math
import threading
import time
from collections import deque
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from ismpu.agent.gain_space import gain_space_for
from ismpu.config.segments import FlightSegment
from ismpu.io.ics_connector import ICSInputs
from ismpu.runtime.run_reader import RunReader
from ismpu.runtime.run_recorder import RunEvent, RunSample, controller_pids


@dataclass(frozen=True)
class ViewSpec:
    key: str
    label: str
    pid_key: str
    phase: str


@dataclass(frozen=True)
class GainChange:
    request_id: int
    old_revision: int
    segment: str
    changes: Mapping[str, Mapping[str, float]]
    action: str
    created_monotonic: float


@dataclass(frozen=True)
class DashboardSnapshot:
    run_id: str
    last_sequence: int
    reset: bool
    frames: tuple[dict, ...]
    events: tuple[dict, ...]
    metadata: dict | None = None
    latest: dict | None = None

    def as_dict(self) -> dict:
        result = {
            "run_id": self.run_id,
            "last_sequence": self.last_sequence,
            "reset": self.reset,
            "frames": list(self.frames),
            "events": list(self.events),
        }
        if self.metadata is not None:
            result["metadata"] = self.metadata
        if self.latest is not None:
            result["latest"] = self.latest
        return result


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
AIR_PID_KEYS = frozenset({"roll", "pitch", "air_speed"})
GROUND_PID_KEYS = frozenset({"steer", "brake_l", "brake_r", "reverse_l", "reverse_r"})
ALL_PID_KEYS = AIR_PID_KEYS | GROUND_PID_KEYS
CONTROL_MODES = frozenset({"classical", "sft-shadow", "sft-active"})

_CONFIG_FIELD = {
    "roll": "roll_pid", "pitch": "pitch_pid", "air_speed": "speed_pid",
    "steer": "runway_center", "brake_l": "brake_l", "brake_r": "brake_r",
    "reverse_l": "rev_l", "reverse_r": "rev_r",
}
_GROUND_REGULATOR = {
    "steer": "runway_center_pid", "brake_l": "pid_brake_l",
    "brake_r": "pid_brake_r", "reverse_l": "pid_rev_l", "reverse_r": "pid_rev_r",
}
_APPLIED_FIELD = {
    "roll": "cmd_aileron_deg", "pitch": "cmd_elevator_g",
    "air_speed": "cmd_throttle_norm", "steer": "allocator_steering_applied",
    "brake_l": "allocator_limited_brake_left",
    "brake_r": "allocator_limited_brake_right",
    "reverse_l": "allocator_limited_reverse_left",
    "reverse_r": "allocator_limited_reverse_right",
}
_AIR_RANGES = {
    "roll": {"kp": (-10.0, 0.0, 0.025), "ki": (-0.5, 0.5, 0.001),
             "kd": (-1.0, 0.5, 0.005)},
    "pitch": {"kp": (0.0, 0.2, 0.0025), "ki": (0.0, 0.02, 0.0005),
              "kd": (0.0, 0.2, 0.0025)},
    "air_speed": {"kp": (0.0, 0.02, 0.00025), "ki": (0.0, 0.005, 0.00005),
                  "kd": (0.0, 0.02, 0.00025)},
}
_MODE_NAMES = {0: "Off", 1: "Approach", 2: "Landing", 3: "Rollout", 4: "Taxi", 5: "ManualTest"}


def _finite(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("gain must be a number") from exc
    if not math.isfinite(number):
        raise ValueError("gain must be finite")
    return number


def _jsonable(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(getattr(key, "value", key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    return str(value)


class DashboardState:
    """HTTP читает только immutable recorder objects; controller меняет control-thread."""

    def __init__(
        self,
        controller=None,
        *,
        sim=None,
        scenario=None,
        recorder=None,
        tune_enabled: bool = False,
        control_mode: str = "classical",
        npgs_active: bool = False,
        tuning_queue_size: int = 64,
        **_legacy_options,
    ) -> None:
        if controller is not None and recorder is None:
            raise ValueError("live dashboard requires the run's RunRecorder")
        if npgs_active:
            control_mode = "sft-active"
        if control_mode not in CONTROL_MODES:
            raise ValueError(f"unknown control mode: {control_mode}")
        self.controller = controller
        self.sim = sim
        self.scenario = scenario
        self.recorder = recorder
        self.tune_enabled = bool(tune_enabled)
        self.control_mode = control_mode
        self.npgs_active = control_mode == "sft-active"
        self._live = recorder is not None
        self._run_id = recorder.execution_id if recorder is not None else "replay"
        self._manifest = recorder.manifest if recorder is not None else {}
        self._report: dict = {}
        self.replay_source: str | None = None
        self.replay_summary: dict | None = None
        self._replay_updates: tuple[tuple[int, RunSample | RunEvent], ...] | None = None
        self._lock = threading.RLock()
        self._queue: deque[GainChange] = deque()
        self._queue_size = max(1, int(tuning_queue_size))
        self._next_request_id = 1
        self._accept_tuning = True
        self._last_applied_revision = -1
        self._initial_gains = _gains_from_manifest(self._manifest)
        self._effective_gains = copy.deepcopy(self._initial_gains)
        profile = str(self._manifest.get("aircraft_profile") or "mc21")
        self._ranges = _gain_ranges(profile, self._initial_gains)

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def view_names(self) -> tuple[str, ...]:
        return tuple(spec.label for spec in VIEW_SPECS)

    def snapshot(self, since_sequence: int = -1, run_id: str | None = None) -> DashboardSnapshot:
        run_changed = run_id not in (None, "", self._run_id)
        cursor = -1 if run_changed else since_sequence
        last, reset, updates = self._updates(cursor)
        reset = reset or run_changed
        frames: list[dict] = []
        events: list[dict] = []
        newest_sample = None
        for sequence, item in updates:
            if isinstance(item, RunSample):
                frames.append(self._frame(sequence, item))
                newest_sample = item
            else:
                events.append(self._event(sequence, item))
        include_metadata = cursor < 0 or reset
        return DashboardSnapshot(
            run_id=self._run_id, last_sequence=last, reset=reset,
            frames=tuple(frames), events=tuple(events),
            metadata=self._metadata(newest_sample) if include_metadata else None,
            latest=self._panels(newest_sample) if newest_sample is not None else None,
        )

    def payload(self, since_sequence: int = -1, run_id: str | None = None) -> dict:
        return self.snapshot(since_sequence, run_id).as_dict()

    def _updates(self, since: int):
        if self._replay_updates is not None:
            last = len(self._replay_updates) - 1
            return last, False, tuple(item for item in self._replay_updates if item[0] > since)
        if self.recorder is None:
            return -1, False, ()
        return self.recorder.dashboard_updates(since)

    def enqueue_gain_update(
        self, pid_key: str, gains: Mapping[str, object], *,
        revision: int | None = None, segment: str | None = None,
    ) -> dict:
        if pid_key not in ALL_PID_KEYS:
            raise KeyError(pid_key)
        active_segment, current_revision = self._live_position()
        segment = segment or active_segment
        revision = current_revision if revision is None else int(revision)
        self._ensure_editable(pid_key, active_segment)
        if segment != active_segment:
            raise PermissionError(f"active segment is {active_segment}, not {segment}")
        current = self._current_gains(segment, pid_key)
        complete = dict(current)
        supplied = False
        for name in ("kp", "ki", "kd"):
            if name in gains:
                complete[name] = _finite(gains[name])
                supplied = True
        if not supplied:
            raise ValueError("at least one of kp, ki, kd is required")
        self._validate_ranges(pid_key, complete)
        return self._enqueue(revision, segment, {pid_key: complete}, "apply")

    def enqueue_revert(
        self, *, revision: int | None = None, segment: str | None = None,
    ) -> dict:
        active_segment, current_revision = self._live_position()
        segment = segment or active_segment
        revision = current_revision if revision is None else int(revision)
        keys = AIR_PID_KEYS if segment == FlightSegment.APPROACH.value else GROUND_PID_KEYS
        for key in keys:
            self._ensure_editable(key, active_segment)
        try:
            changes = copy.deepcopy(self._initial_gains[segment])
        except KeyError as exc:
            raise RuntimeError(f"no run-start gains for {segment}") from exc
        return self._enqueue(revision, segment, changes, "revert")

    def _enqueue(self, revision: int, segment: str, changes: Mapping, action: str) -> dict:
        with self._lock:
            if not self._accept_tuning:
                raise RuntimeError("run is complete; tuning is read-only")
            if len(self._queue) >= self._queue_size:
                raise OverflowError("tuning queue is full")
            request = GainChange(
                self._next_request_id, int(revision), segment,
                copy.deepcopy(dict(changes)), action, time.monotonic())
            self._next_request_id += 1
            self._queue.append(request)
        return {
            "status": "pending", "request_id": request.request_id,
            "old_revision": request.old_revision, "segment": segment,
            "action": action, "changes": _jsonable(request.changes),
        }

    def apply_pending_gain_updates(self) -> list[dict]:
        """Вызывается runtime ровно в начале control tick."""
        results = []
        while True:
            with self._lock:
                if not self._queue:
                    break
                request = self._queue.popleft()
            results.append(self._apply(request))
        return results

    def _apply(self, request: GainChange) -> dict:
        segment = getattr(getattr(self.controller, "segment", None), "value", None)
        pids = controller_pids(self.controller) if self.controller is not None else {}
        before = {
            key: {name: getattr(pids[key], name) for name in ("kp", "ki", "kd")}
            for key in request.changes if pids.get(key) is not None
        }
        try:
            if segment != request.segment:
                raise RuntimeError(f"stale segment: {request.segment} -> {segment}")
            if self.controller.config_revision != request.old_revision:
                raise RuntimeError(
                    f"stale revision: {request.old_revision} -> {self.controller.config_revision}")
            for key, gains in request.changes.items():
                self._ensure_editable(key, segment)
                if pids.get(key) is None:
                    raise RuntimeError(f"PID {key} is not configured")
                self._validate_ranges(key, gains)
            for key, gains in request.changes.items():
                pids[key].set_gains_bumpless(**gains)
            self.controller.config_revision += 1
            after = {
                key: {name: getattr(pids[key], name) for name in ("kp", "ki", "kd")}
                for key in request.changes
            }
            with self._lock:
                self._effective_gains.setdefault(segment, {}).update(copy.deepcopy(after))
                self._last_applied_revision = self.controller.config_revision
            event_name = "gain_reverted" if request.action == "revert" else "gain_change_applied"
            result = {
                "status": "applied", "request_id": request.request_id,
                "old_revision": request.old_revision,
                "revision": self.controller.config_revision,
                "segment": segment, "action": request.action,
                "before": before, "after": after,
            }
            self._record_gain_event(event_name, request, result)
            return result
        except Exception as exc:
            result = {
                "status": "rejected", "request_id": request.request_id,
                "old_revision": request.old_revision,
                "revision": getattr(self.controller, "config_revision", None),
                "segment": segment, "action": request.action,
                "before": before, "after": before, "reason": str(exc),
            }
            self._record_gain_event("gain_change_rejected", request, result)
            return result

    def _record_gain_event(self, event: str, request: GainChange, result: dict) -> None:
        if self.recorder is None:
            return
        sample = self.recorder.latest_sample
        matrix_id = self._manifest.get("matrix_run_ids", {}).get(request.segment)
        self.recorder.record_event(
            event,
            data={**result, "request_sequence": request.request_id,
                  "matrix_run_id": matrix_id},
            time_s=sample.time_s if sample is not None else None,
            tick_id=getattr(self.controller, "tick_id", None),
            segment=request.segment,
        )

    def cancel_pending_gain_updates(self) -> None:
        with self._lock:
            self._accept_tuning = False
            pending, self._queue = tuple(self._queue), deque()
        for request in pending:
            result = {
                "status": "rejected", "request_id": request.request_id,
                "old_revision": request.old_revision,
                "revision": getattr(self.controller, "config_revision", None),
                "segment": request.segment, "action": request.action,
                "before": {}, "after": {}, "reason": "run completed",
            }
            self._record_gain_event("gain_change_rejected", request, result)

    def complete(self) -> None:
        """После recorder.finish держать полный run доступным, но только для чтения."""
        self.cancel_pending_gain_updates()
        if self.recorder is None or not self.recorder.directory.is_dir():
            return
        reader = RunReader(self.recorder.directory)
        self._replay_updates = _load_updates(reader)
        self._report = reader.report
        self.replay_summary = reader.summary()

    def save_candidate(self, *, segment: str | None = None, label: str = "dashboard") -> Path:
        if not self._live or self.recorder is None:
            raise RuntimeError("replay is read-only")
        if self.recorder.recording_failed:
            raise RuntimeError(f"recorder failed: {self.recorder.recording_error}")
        with self._lock:
            if self._queue:
                raise RuntimeError("gain changes are still pending")
        sample = self._latest_sample()
        if sample is None:
            raise RuntimeError("no recorded control tick")
        segment = segment or sample.segment
        if segment != sample.segment:
            raise RuntimeError(f"candidate segment {segment} is not active ({sample.segment})")
        if self._last_applied_revision > sample.config_revision:
            raise RuntimeError("wait for the next recorded tick before saving")
        gains = self._sample_gains(sample, segment)
        if any(value is None for values in gains.values() for value in values.values()):
            raise RuntimeError("candidate requires complete recorded kp/ki/kd")
        config = copy.deepcopy(self._manifest["effective_configs"][segment]["control"])
        for key, values in gains.items():
            config[_CONFIG_FIELD[key]].update(values)
        path = self.recorder.export_candidate(
            segment=segment, config_revision=sample.config_revision,
            effective_config=config, gains=gains, label=label)
        if self._replay_updates is not None:
            self._replay_updates = _load_updates(RunReader(self.recorder.directory))
        return path

    export_gains = save_candidate

    def _ensure_editable(self, pid_key: str, active_segment: str) -> None:
        if not self._live:
            raise RuntimeError("replay is read-only")
        if not self.tune_enabled:
            raise PermissionError("live tuning is disabled; use --dashboard-tune")
        if self.control_mode == "sft-active":
            raise PermissionError("sft-active gains are read-only")
        expected = AIR_PID_KEYS if active_segment == "approach" else GROUND_PID_KEYS
        if pid_key not in expected:
            raise PermissionError(f"PID {pid_key} is inactive in {active_segment}")

    def _live_position(self) -> tuple[str, int]:
        if not self._live or self.recorder is None:
            raise RuntimeError("replay is read-only")
        sample = self.recorder.latest_sample
        if sample is not None:
            return sample.segment, sample.config_revision
        segment = getattr(getattr(self.controller, "segment", None), "value", "rollout")
        return segment, int(getattr(self.controller, "config_revision", 0))

    def _validate_ranges(self, pid_key: str, gains: Mapping[str, float]) -> None:
        for name, value in gains.items():
            if name not in ("kp", "ki", "kd"):
                continue
            lower, upper, _step = self._ranges[pid_key][name]
            if not lower <= float(value) <= upper:
                raise ValueError(f"{pid_key}.{name}={value} outside [{lower}, {upper}]")

    def _current_gains(self, segment: str, pid_key: str) -> dict[str, float]:
        sample = self.recorder.latest_sample if self.recorder is not None else None
        if sample is not None and sample.segment == segment:
            values = {name: sample.values.get(f"pid_{pid_key}_{name}")
                      for name in ("kp", "ki", "kd")}
            if all(value is not None for value in values.values()):
                return {name: float(value) for name, value in values.items()}
        try:
            return dict(self._effective_gains[segment][pid_key])
        except KeyError as exc:
            raise RuntimeError(f"no gains for {segment}:{pid_key}") from exc

    def _latest_sample(self) -> RunSample | None:
        if self._replay_updates is not None:
            return next((item for _seq, item in reversed(self._replay_updates)
                         if isinstance(item, RunSample)), None)
        return self.recorder.latest_sample if self.recorder is not None else None

    def _sample_gains(self, sample: RunSample, segment: str) -> dict[str, dict[str, float]]:
        keys = AIR_PID_KEYS if segment == "approach" else GROUND_PID_KEYS
        result = {}
        for key in keys:
            values = {name: sample.values.get(f"pid_{key}_{name}")
                      for name in ("kp", "ki", "kd")}
            if all(value is not None for value in values.values()):
                result[key] = {name: float(value) for name, value in values.items()}
            else:
                try:
                    fallback = self._current_gains(segment, key)
                except RuntimeError:
                    fallback = {}
                result[key] = {
                    name: (float(values[name]) if values[name] is not None
                           else fallback.get(name))
                    for name in ("kp", "ki", "kd")}
        return result

    def _frame(self, sequence: int, sample: RunSample) -> dict:
        row = sample.as_row()
        views = {}
        for spec in VIEW_SPECS:
            if spec.phase == "ground" and sample.segment == "approach":
                continue
            if spec.phase in {"approach", "flare"} and sample.segment != "approach":
                continue
            if spec.phase == "flare" and not bool(row.get("approach_flare_active")):
                continue
            views[spec.key] = _view_point(spec.pid_key, row, sample.segment)
        return {
            "seq": sequence, "sample_sequence": sample.sequence,
            "tick_id": sample.tick_id, "t": sample.time_s,
            "timestamp_utc": sample.timestamp_utc, "segment": sample.segment,
            "views": views,
        }

    def _event(self, sequence: int, event: RunEvent) -> dict:
        return {
            "seq": sequence, "event_sequence": event.sequence,
            "timestamp_utc": event.timestamp_utc, "time_s": event.time_s,
            "tick_id": event.tick_id, "event": event.event,
            "segment": event.segment, "data": _jsonable(event.data),
        }

    def _metadata(self, sample: RunSample | None) -> dict:
        segment = sample.segment if sample is not None else self._live_position_or_default()[0]
        views = []
        for spec in VIEW_SPECS:
            active = (spec.pid_key in AIR_PID_KEYS) == (segment == "approach")
            views.append({
                **asdict(spec),
                "locked": not (self.tune_enabled and self._live and active
                               and self.control_mode != "sft-active" and self._accept_tuning),
                "ranges": {name: {"min": values[0], "max": values[1], "step": values[2]}
                           for name, values in self._ranges[spec.pid_key].items()},
            })
        scenario_doc = self._manifest.get("scenario", {})
        profile = str(self._manifest.get("aircraft_profile") or "recorded")
        controls = scenario_doc.get("aircraft_controls", {}).get(profile, {})
        return {
            "header": {
                "backend": self._manifest.get("backend", "replay"),
                "execution_id": self._run_id,
                "matrix_run_ids": self._manifest.get("matrix_run_ids", {}),
                "aircraft_profile": profile,
                "scenario_id": self._manifest.get("scenario_id"),
                "frequency_hz": self._manifest.get("frequency_hz"),
                "control_policy": self.control_mode,
                "tune_enabled": self.tune_enabled,
            },
            "views": views, "telemetry_fields": _TELEMETRY_SPECS,
            "matrix_config": {
                "selected_rows": self._manifest.get("matrix_rows", {}),
                "matrix_run_ids": self._manifest.get("matrix_run_ids", {}),
                "matrix_hashes": {
                    "catalog": self._manifest.get("matrix_catalog_sha256"),
                    "source": self._manifest.get("matrix_source_sha256"),
                    "rows": self._manifest.get("matrix_row_hashes", {}),
                },
                "expected_conditions": scenario_doc.get("conditions", {}),
                "effective_configs": self._manifest.get("effective_configs", {}),
                "statuses": controls.get("statuses", {}),
                "config_hashes": self._manifest.get("config_hashes", {}),
            },
            "replay": ({"source": self.replay_source, "summary": self.replay_summary}
                       if self.replay_source else None),
        }

    def _live_position_or_default(self) -> tuple[str, int]:
        if self._live:
            return self._live_position()
        sample = self._latest_sample()
        return ((sample.segment, sample.config_revision)
                if sample is not None else ("unknown", 0))

    def _panels(self, sample: RunSample) -> dict:
        row = sample.as_row()
        age = None
        if self._live and not self.recorder.finished:
            try:
                stamp = datetime.fromisoformat(sample.timestamp_utc)
                age = max(0.0, (datetime.now(timezone.utc) - stamp).total_seconds())
            except (TypeError, ValueError):
                pass
        mode = sample.control_mode
        known = {}
        for spec in _TELEMETRY_SPECS:
            name, valid_field = spec["name"], spec["valid_field"]
            valid = row.get(f"ics_{valid_field}") if valid_field else row.get("valid")
            known[name] = {"value": row.get(f"ics_{name}"), "valid": valid}
        raw = row.get("ics_raw_json")
        air = {
            "loc_dots": row.get("approach_loc_dots"), "gs_dots": row.get("approach_gs_dots"),
            "radio_altitude_ft": row.get("radio_altitude_ft"),
            "ias_kt": row.get("approach_input_IndicatedAirspeed"),
            "vapp_kt": row.get("approach_target_ias_kt"),
            "vertical_speed_fpm": row.get("approach_input_VerticalSpeed"),
            "target_vs_fpm": row.get("approach_target_vs_fpm"),
            "pitch_deg": row.get("pitch_deg"), "roll_deg": row.get("roll_deg"),
            "p_rad_s": row.get("p_rad"), "q_rad_s": row.get("q_rad"),
            "r_rad_s": row.get("r_rad"),
            "flare_armed": row.get("approach_flare_armed"),
            "flare_active": row.get("approach_flare_active"),
            "flare_progress": row.get("approach_flare_progress"),
            "throttle_norm": row.get("approach_throttle_norm"),
            "throttle_left_deg": row.get("ics_LeftThrottleAngle"),
            "throttle_right_deg": row.get("ics_RightThrottleAngle"),
            "thrust_left_pct": row.get("ics_EngLeftThrust"),
            "thrust_right_pct": row.get("ics_EngRigntThrust"),
            "envelope_warnings": row.get("approach_envelope_warnings"),
            "tolerances": row.get("approach_tolerances"),
        }
        ground_lateral = {
            "bench_xte_m": row.get("ics_LateralDeviation"),
            "selected_xte_m": row.get("guidance_xte_m"),
            "geodetic_fallback_m": (row.get("guidance_xte_m")
                                    if row.get("guidance_source") == "geodetic" else None),
            "source": row.get("guidance_source"),
            "track_deg": _first_present(
                row.get("track_magnetic_deg"), row.get("track_true_deg")),
            "heading_deg": _first_present(
                row.get("heading_magnetic_deg"), row.get("heading_true_deg")),
            "course_error_deg": row.get("guidance_course_error_deg"),
            "heading_error_deg": row.get("guidance_heading_error_deg"),
            "guidance_error_deg": row.get("guidance_error_deg"),
            "steering_requested": row.get("lateral_pid_requested"),
            "steering_applied": row.get("allocator_steering_applied"),
            "allocator_base": _allocator_stage(row, "base"),
            "allocator_lateral": _allocator_stage(row, "lateral"),
            "allocator_requested": _allocator_stage(row, "requested"),
            "allocator_limited": _allocator_stage(row, "limited"),
        }
        ground_longitudinal = {
            "groundspeed_ms": row.get("groundspeed_ms"),
            "reference_ms": row.get("ground_reference_speed_ms"),
            "speed_error_ms": row.get("ground_speed_error_ms"),
            "distance_m": row.get("ground_distance_m"),
            "acceleration_ms2": row.get("ground_acceleration_ms2"),
            "base": {name: row.get(f"allocator_base_{name}") for name in
                     ("brake_left", "brake_right", "reverse_left", "reverse_right")},
            "mixed": {name: row.get(f"allocator_limited_{name}") for name in
                      ("brake_left", "brake_right", "reverse_left", "reverse_right")},
            "feedback": {name: row.get(f"feedback_{name}") for name in
                         ("brake_left_mm", "brake_right_mm", "throttle_left_deg",
                          "throttle_right_deg", "thrust_left", "thrust_right")},
        }
        effective = self._sample_gains(sample, sample.segment)
        return {
            "header": {
                "backend": self._manifest.get("backend", "replay"),
                "execution_id": self._run_id,
                "matrix_run_ids": self._manifest.get("matrix_run_ids", {}),
                "aircraft_profile": self._manifest.get("aircraft_profile", "recorded"),
                "segment": sample.segment, "control_mode": mode,
                "control_mode_name": _MODE_NAMES.get(mode, str(mode)),
                "control_valid_mask": sample.control_valid_mask,
                "config_revision": sample.config_revision,
                "frequency_hz": self._manifest.get("frequency_hz"),
                "telemetry_age_s": age, "agent_active": row.get("agent_active"),
                "recorder_status": ("error" if getattr(self.recorder, "recording_failed", False)
                                    else "completed" if getattr(self.recorder, "finished", False)
                                    else "recording" if self._live else "replay"),
                "recorder_error": getattr(self.recorder, "recording_error", None),
            },
            "air": air, "ground_lateral": ground_lateral,
            "ground_longitudinal": ground_longitudinal,
            "telemetry": {"known": known, "unknown_raw": raw if isinstance(raw, dict) else {}},
            "actual_conditions": {"failures": row.get("faults"), "weather": row.get("weather")},
            "gain_layers": {
                "static": self._initial_gains.get(sample.segment),
                "predicted": row.get("predicted_gains"), "effective": effective,
                "gain_guard": row.get("gain_guard"),
                "fallback": row.get("gain_fallback_reason"),
            },
        }

    @classmethod
    def from_csv(cls, path: str | Path, **_options) -> "DashboardState":
        reader = RunReader(path)
        state = cls()
        state._manifest, state._report = reader.manifest, reader.report
        state.replay_source = str(reader.path.resolve())
        state.replay_summary = reader.summary()
        state._replay_updates = _load_updates(reader)
        sample = next((item for _seq, item in state._replay_updates
                       if isinstance(item, RunSample)), None)
        state._run_id = str(reader.manifest.get("execution_id")
                            or (sample.execution_id if sample is not None else reader.path.stem))
        state._initial_gains = _gains_from_manifest(state._manifest)
        if not state._initial_gains:
            state._initial_gains = _gains_from_samples(state._replay_updates)
        state._effective_gains = copy.deepcopy(state._initial_gains)
        profile = str(state._manifest.get("aircraft_profile") or "mc21")
        state._ranges = _gain_ranges(profile, state._initial_gains)
        state._accept_tuning = False
        return state


class DashboardServer:
    def __init__(self, state: DashboardState, *, host: str = "127.0.0.1", port: int = 8765) -> None:
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("PID dashboard may bind only to a loopback address")
        self.state = state
        self.httpd = ThreadingHTTPServer((host, port), _handler_factory(state))
        self.thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        return self.httpd.server_address[:2]

    def start(self) -> "DashboardServer":
        if self.thread is None:
            self.thread = threading.Thread(
                target=self.httpd.serve_forever, name="ismpu-pid-dashboard", daemon=True)
            self.thread.start()
        return self

    def stop(self) -> None:
        self.state.cancel_pending_gain_updates()
        if self.thread is not None:
            self.httpd.shutdown()
            self.thread.join(timeout=2.0)
            self.thread = None
        self.httpd.server_close()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, traceback):
        self.stop()
        return False


def _handler_factory(state: DashboardState):
    html_path = Path(__file__).with_name("dashboard.html")

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, _format, *_args):
            return

        def _json(self, status: int, payload) -> None:
            body = json.dumps(_jsonable(payload), ensure_ascii=False,
                              separators=(",", ":"), allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def do_GET(self):
            request = urlsplit(self.path)
            if request.path in {"/", "/dashboard.html"}:
                body = html_path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True
                return
            if request.path == "/api/state":
                query = parse_qs(request.query)
                try:
                    since = int(query.get("since", ["-1"])[0])
                except ValueError:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "since must be an integer"})
                    return
                self._json(HTTPStatus.OK, state.snapshot(
                    since, query.get("run_id", [None])[0]).as_dict())
                return
            if request.path == "/api/views":
                self._json(HTTPStatus.OK, state.snapshot(-1).metadata["views"])
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self):
            request = urlsplit(self.path)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 65536:
                    raise ValueError("request body is too large")
                payload = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(payload, dict):
                    raise TypeError("JSON body must be an object")
                if request.path.startswith("/api/gains/"):
                    key = unquote(request.path.rsplit("/", 1)[-1])
                    result = state.enqueue_gain_update(
                        key, payload, revision=payload.get("revision"),
                        segment=payload.get("segment"))
                    self._json(HTTPStatus.ACCEPTED, result)
                elif request.path == "/api/revert":
                    result = state.enqueue_revert(
                        revision=payload.get("revision"), segment=payload.get("segment"))
                    self._json(HTTPStatus.ACCEPTED, result)
                elif request.path in {"/api/candidate", "/api/export"}:
                    path = state.save_candidate(
                        segment=payload.get("segment"),
                        label=str(payload.get("label", "dashboard")))
                    self._json(HTTPStatus.CREATED, {"path": str(path.resolve())})
                else:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            except PermissionError as exc:
                self._json(HTTPStatus.FORBIDDEN, {"error": str(exc)})
            except KeyError as exc:
                self._json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except (RuntimeError, FileExistsError) as exc:
                self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
            except OverflowError as exc:
                self._json(HTTPStatus.TOO_MANY_REQUESTS, {"error": str(exc)})

    return Handler


def _view_point(pid_key: str, row: Mapping[str, object], segment: str) -> dict:
    prefix = f"pid_{pid_key}_"
    value = row.get(prefix + "value")
    if value is None:
        value = {
            "roll": row.get("roll_deg"), "pitch": row.get("pitch_deg"),
            "air_speed": row.get("ias_ms"),
        }.get(pid_key)
    feedback = {
        "roll": row.get("ics_AileronLeftAngle"),
        "pitch": _mean(row.get("ics_ElevatorLeftAngle"), row.get("ics_ElevatorRightAngle")),
        "air_speed": _mean(row.get("ics_LeftThrottleAngle"), row.get("ics_RightThrottleAngle")),
        "steer": (row.get("feedback_rudder_deg") if segment == "rollout"
                  else row.get("feedback_nose_wheel_deg")),
        "brake_l": row.get("feedback_brake_left_mm"),
        "brake_r": row.get("feedback_brake_right_mm"),
        "reverse_l": row.get("feedback_throttle_left_deg"),
        "reverse_r": row.get("feedback_throttle_right_deg"),
    }[pid_key]
    return {
        "value": value, "setpoint": row.get(prefix + "setpoint"),
        "error": row.get(prefix + "error"), "requested": row.get(prefix + "unconstrained"),
        "output": row.get(prefix + "output"), "applied": row.get(_APPLIED_FIELD[pid_key]),
        "feedback": feedback, "p": row.get(prefix + "p"), "i": row.get(prefix + "i"),
        "d": row.get(prefix + "d"), "integral": row.get(prefix + "integral"),
        "saturated": bool(row.get(prefix + "saturated")),
        "kp": row.get(prefix + "kp"), "ki": row.get(prefix + "ki"),
        "kd": row.get(prefix + "kd"),
    }


def _mean(left, right):
    values = [float(value) for value in (left, right) if isinstance(value, (int, float))]
    return sum(values) / len(values) if values else None


def _first_present(*values):
    return next((value for value in values if value is not None), None)


def _allocator_stage(row, stage: str) -> dict:
    return {name: row.get(f"allocator_{stage}_{name}") for name in
            ("rudder", "pedal", "tiller", "brake_left", "brake_right",
             "reverse_left", "reverse_right")}


def _load_updates(reader: RunReader) -> tuple[tuple[int, RunSample | RunEvent], ...]:
    items: list[RunSample | RunEvent] = list(reader.samples())
    for raw in reader.events():
        items.append(RunEvent(
            sequence=int(raw.get("sequence", 0)),
            timestamp_utc=str(raw.get("timestamp_utc") or ""),
            monotonic_s=float(raw.get("monotonic_s") or 0.0),
            time_s=raw.get("time_s"), tick_id=raw.get("tick_id"),
            event=str(raw.get("event") or "event"), segment=raw.get("segment"),
            data=dict(raw.get("data") or {}),
        ))
    items.sort(key=lambda item: (item.monotonic_s,
                                 0 if isinstance(item, RunSample) else 1,
                                 item.sequence))
    return tuple(enumerate(items))


def _gains_from_manifest(manifest: Mapping) -> dict[str, dict[str, dict[str, float]]]:
    result = {}
    for segment, value in manifest.get("effective_configs", {}).items():
        control = value.get("control", {})
        keys = AIR_PID_KEYS if segment == "approach" else GROUND_PID_KEYS
        per_segment = {}
        for key in keys:
            config = control.get(_CONFIG_FIELD[key], {})
            if all(name in config for name in ("kp", "ki", "kd")):
                per_segment[key] = {name: float(config[name]) for name in ("kp", "ki", "kd")}
        result[segment] = per_segment
    return result


def _gains_from_samples(updates) -> dict[str, dict[str, dict[str, float]]]:
    result = {}
    for _sequence, item in updates:
        if not isinstance(item, RunSample):
            continue
        keys = AIR_PID_KEYS if item.segment == "approach" else GROUND_PID_KEYS
        segment = result.setdefault(item.segment, {})
        for key in keys:
            values = {name: item.values.get(f"pid_{key}_{name}")
                      for name in ("kp", "ki", "kd")}
            if all(value is not None for value in values.values()):
                segment.setdefault(key, {name: float(value) for name, value in values.items()})
    return result


def _gain_ranges(profile: str, initial: Mapping) -> dict:
    result = copy.deepcopy(_AIR_RANGES)
    try:
        space = gain_space_for(profile)
        lo, hi = space.lo_map, space.hi_map
        for key, regulator in _GROUND_REGULATOR.items():
            result[key] = {
                name: (float(lo[regulator][name]), float(hi[regulator][name]),
                       max((float(hi[regulator][name]) - float(lo[regulator][name])) / 400.0,
                           1e-8))
                for name in ("kp", "ki", "kd")}
    except (KeyError, ValueError):
        ground = initial.get("rollout") or initial.get("taxi") or {}
        for key in GROUND_PID_KEYS:
            values = ground.get(key, {"kp": 1.0, "ki": 1.0, "kd": 1.0})
            result[key] = {
                name: (0.0, max(abs(float(values[name])) * 2.0, 1e-6),
                       max(abs(float(values[name])) / 100.0, 1e-8))
                for name in ("kp", "ki", "kd")}
    return result


def _telemetry_unit(name: str) -> str:
    if name.endswith("Valid") or name.startswith("Fault") or name.endswith("WeightOnWheels"):
        return "bool"
    if name in {"AgentIsActive", "FlightPhase", "RunwayCondition"} or name.endswith("Status"):
        return "code"
    if name in {"Latitude", "Longitude"}:
        return "deg"
    if name in {"RadioAltitude", "BaroAltitude", "Visibility"}:
        return "ft"
    if name in {"IndicatedAirspeed", "TrueAirspeed", "GroundSpeed", "WindSpeed"}:
        return "kt"
    if name == "VerticalSpeed":
        return "ft/min"
    if name.startswith("Body") and name.endswith("Rate"):
        return "deg/s"
    if name.startswith("Body") and name.endswith("Accel"):
        return "g"
    if name in {"RunwayLength", "RunwayWidth", "LateralDeviation"}:
        return "m"
    if name in {"LocDeviation", "GSDeviation"}:
        return "ddm"
    if name in {"LeftBrakePedal", "RightBrakePedal"}:
        return "mm"
    if name in {"EngLeftThrust", "EngRigntThrust"}:
        return "%"
    if name == "PrecipitationRatio":
        return "0..1"
    if name == "AirfieldTemp":
        return "degC"
    if any(token in name for token in ("Angle", "Heading", "Trk", "Wheel", "Spoiler", "AirBrake")):
        return "deg"
    return ""


def _telemetry_group(name: str) -> str:
    if name.endswith("Valid"):
        return "Validity"
    if name.startswith("Fault"):
        return "Failures"
    if name.startswith(("Wind", "Visibility", "Precipitation", "Airfield", "RunwayCondition")):
        return "Weather"
    if "Gear" in name or "Wheel" in name:
        return "Gear"
    if name.startswith(("Eng", "LeftThrottle", "RightThrottle")):
        return "Propulsion"
    if name.startswith(("LeftBrake", "RightBrake", "LeftSpoiler", "RightSpoiler")) or "AirBrake" in name:
        return "Ground/High lift"
    if name.startswith(("Loc", "GS", "Runway", "Lateral")):
        return "Runway/ILS"
    if name.startswith("Body"):
        return "Rates/Acceleration"
    if name in {"Latitude", "Longitude"}:
        return "Position"
    return "Flight/Air data"


_ICS_NAMES = tuple(item.name for item in fields(ICSInputs))
_ICS_NAME_SET = frozenset(_ICS_NAMES)
_TELEMETRY_SPECS = tuple({
    "name": name, "unit": _telemetry_unit(name), "group": _telemetry_group(name),
    "valid_field": (f"{name}Valid" if f"{name}Valid" in _ICS_NAME_SET else None),
} for name in _ICS_NAMES)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="ИСМПУ PID dashboard replay")
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
