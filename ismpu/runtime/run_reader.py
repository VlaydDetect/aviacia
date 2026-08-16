"""Единое потоковое чтение run-directory, replay и прежних CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from ismpu.config.scenarios import Scenario
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import Telemetry
from ismpu.envs.sim_interface import ApproachData
from ismpu.io.ics_connector import ICSInputs
from ismpu.runtime.roman_logs import RomanLogImporter
from ismpu.runtime.run_artifacts import (
    APPROACH_INPUT_FIELDS, COMMAND_FIELDS, GROUND_DIAGNOSTIC_FIELDS,
    ICS_INPUT_FIELDS, PID_FIELDS, RunSample, SAMPLE_ID_FIELDS,
    controller_pids, sample_values,
)
from ismpu.utils.converts import Converts


@dataclass(frozen=True)
class ReplayMismatch:
    tick_id: int
    sequence: int
    field: str
    expected: object
    actual: object


@dataclass(frozen=True)
class ReplayReport:
    samples: int
    compared_values: int
    mismatch_count: int
    max_abs_error: float
    mismatches: tuple[ReplayMismatch, ...]

    @property
    def success(self) -> bool:
        return self.mismatch_count == 0

    def as_dict(self) -> dict:
        return {
            "samples": self.samples,
            "compared_values": self.compared_values,
            "mismatch_count": self.mismatch_count,
            "max_abs_error": self.max_abs_error if math.isfinite(self.max_abs_error) else None,
            "success": self.success,
            "mismatches": [item.__dict__ for item in self.mismatches],
        }


class RunReader:
    """Run-directory и любой поддержанный CSV через один streaming API."""

    def __init__(self, source: str | Path) -> None:
        source = Path(source)
        self.directory = source if source.is_dir() else source.parent
        self.path = source / "telemetry.csv" if source.is_dir() else source
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self.manifest = self._load_manifest()
        with self.path.open("r", encoding="utf-8-sig", newline="") as stream:
            self.fieldnames = tuple(csv.DictReader(stream).fieldnames or ())
        self.canonical = "pid_roll_output" in self.fieldnames or "tick_id" in self.fieldnames

    def _load_manifest(self) -> dict:
        for name in ("manifest.json", "metadata.json"):
            path = self.directory / name
            if path.is_file():
                return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def rows(self):
        """Нормализованные строки; отсутствующие P/D legacy-лога остаются ``None``."""
        if not self.canonical:
            yield from RomanLogImporter(self.path).rows()
            return
        with self.path.open("r", encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                yield {key: _parse_cell(value) for key, value in row.items()}

    def events(self):
        path = self.directory / "events.jsonl"
        if not path.is_file():
            return
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)

    def samples(self):
        """Типизированный поток новых и legacy-строк с синтетическими ID для старых CSV."""
        execution_id = str(self.manifest.get("execution_id") or self.path.stem)
        scenario_id = str(self.manifest.get("scenario_id") or "legacy")
        for sequence, row in enumerate(self.rows()):
            base = {
                "execution_id": row.get("execution_id") or execution_id,
                "tick_id": int(_number(row.get("tick_id"), sequence + 1)),
                "sequence": int(_number(row.get("sequence"), sequence)),
                "timestamp_utc": str(row.get("timestamp_utc") or ""),
                "monotonic_s": _number(row.get("monotonic_s"), row.get("time_s") or 0.0),
                "time_s": _number(row.get("time_s"), 0.0),
                "dt": _number(row.get("dt"), 0.0),
                "scenario_id": str(row.get("scenario_id") or scenario_id),
                "segment": str(row.get("segment") or "unknown"),
                "control_mode": row.get("control_mode"),
                "control_valid_mask": row.get("control_valid_mask"),
                "command_sent": bool(row.get("command_sent", False)),
                "config_revision": int(_number(row.get("config_revision"), 0)),
            }
            values = {key: value for key, value in row.items() if key not in SAMPLE_ID_FIELDS}
            yield RunSample(values=values, **base)

    @property
    def report(self) -> dict:
        path = self.directory / "report.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def raw_packets(self, direction: str):
        if direction not in {"rx", "tx"}:
            raise ValueError("direction must be 'rx' or 'tx'")
        path = self.directory / f"raw-{direction}.jsonl"
        if not path.is_file():
            return
        with path.open("rb") as stream:
            yield from stream

    def summary(self) -> dict:
        count = 0
        first = last = None
        for row in self.rows():
            count += 1
            current = _number(row.get("time_s"), 0.0)
            first = current if first is None else first
            last = current
        return {"rows": count, "duration_s": (last - first) if count else 0.0}

    def replay(self, controller: ControllingSystem | None = None, *,
               atol: float = 1e-9, rtol: float = 1e-9) -> ReplayReport:
        """Пересчитать команды без backend/UDP и сверить каждый записанный такт."""
        scenario_doc = self.manifest.get("scenario")
        if not isinstance(scenario_doc, dict):
            raise ValueError("replay контроллера требует manifest со сценарием")
        scenario = Scenario.from_dict(
            scenario_doc,
            legacy_aircraft_profile=str(self.manifest.get("aircraft_profile", "mc21")),
        )
        profile = str(self.manifest.get("aircraft_profile", "mc21"))
        controller = controller or ControllingSystem()
        controller.bind_scenario(scenario, profile)

        samples = compared = mismatch_count = 0
        max_error = 0.0
        mismatches: list[ReplayMismatch] = []
        started = False
        for row in self.rows():
            telemetry = telemetry_from_row(row)
            if not started:
                segment = str(row.get("segment") or "rollout")
                controller.begin_flight(
                    telemetry,
                    FlightSegment.TAXI if segment == FlightSegment.TAXI.value else None,
                )
                started = True
            _apply_recorded_gains(controller, row)
            controller.control_step(_number(row.get("dt"), 0.05), telemetry, send=False)
            actual = sample_values(telemetry, controller)
            tick_id = int(_number(row.get("tick_id"), samples + 1))
            sequence = int(_number(row.get("sequence"), samples))
            for field, expected, observed in (
                ("tick_id", tick_id, controller.tick_id),
                ("sequence", sequence, samples),
            ):
                compared += 1
                if expected != observed:
                    mismatch_count += 1
                    if len(mismatches) < 100:
                        mismatches.append(ReplayMismatch(
                            tick_id, sequence, field, expected, observed))
            samples += 1
            for field in _REPLAY_FIELDS:
                expected = row.get(field)
                if expected is None:
                    continue
                observed = actual.get(field)
                compared += 1
                equal, error = _equal(expected, observed, atol=atol, rtol=rtol)
                max_error = max(max_error, error)
                if not equal:
                    mismatch_count += 1
                    if len(mismatches) < 100:
                        mismatches.append(ReplayMismatch(
                            tick_id, sequence, field, expected, observed))
        return ReplayReport(samples, compared, mismatch_count, max_error, tuple(mismatches))


_REPLAY_FIELDS = (
    COMMAND_FIELDS + GROUND_DIAGNOSTIC_FIELDS
    + tuple(field for field in PID_FIELDS if not field.endswith(("_kp", "_ki", "_kd")))
    + tuple(f"approach_{name}" for name in (
        "aileron_deg", "elevator_g", "throttle_norm", "loc_dots", "gs_dots",
        "course_deg", "glideslope_deg", "target_heading_deg", "heading_error_deg",
        "target_roll_deg", "target_vs_fpm", "target_pitch_deg", "flare_active",
        "flare_progress", "terminal_hold_active",
    ))
)


def replay_run(source: str | Path, *, atol: float = 1e-9, rtol: float = 1e-9) -> ReplayReport:
    return RunReader(source).replay(atol=atol, rtol=rtol)


def telemetry_from_row(row: dict) -> Telemetry:
    """Восстановить входной кадр: raw ICS приоритетен, иначе SI/backend-neutral slice."""
    raw = {name: row.get(f"ics_{name}") for name in ICS_INPUT_FIELDS}
    if all(value is not None for value in raw.values()):
        extras = row.get("ics_raw_json")
        if isinstance(extras, dict):
            raw.update(extras)
        telemetry = Telemetry.from_ics(ICSInputs.from_dict(raw))
        # Эти значения уже прошли профильный sign/geometry boundary в исходном runtime.
        telemetry.runway_heading_deg_direct = (
            row.get("runway_heading_magnetic_deg") or row.get("runway_heading_true_deg"))
        telemetry.runway_length_m_direct = row.get("runway_length_m")
        telemetry.runway_width_m_direct = row.get("runway_width_m")
        telemetry.lateral_deviation_m_direct = row.get("lateral_deviation_m")
        return telemetry

    approach = None
    values = {name: row.get(f"approach_input_{name}") for name in APPROACH_INPUT_FIELDS}
    if any(value is not None for value in values.values()):
        approach = ApproachData(**{
            name: value for name, value in values.items() if value is not None})
    elif str(row.get("segment")) == FlightSegment.APPROACH.value:
        approach = ApproachData(
            RadioAltitude=_number(row.get("radio_altitude_ft"), 0.0),
            IndicatedAirspeed=_number(row.get("ias_ms"), 0.0) * Converts.MS_TO_KTS,
            GroundSpeed=_number(row.get("groundspeed_ms"), 0.0) * Converts.MS_TO_KTS,
            VerticalSpeed=_number(row.get("vertical_speed_fpm"), 0.0),
            PitchAngle=_number(row.get("pitch_deg"), 0.0),
            RollAngle=_number(row.get("roll_deg"), 0.0),
            TrkAngleMagnetic=_number(row.get("track_magnetic_deg"), 0.0),
            RunwayHeading=_number(row.get("runway_heading_magnetic_deg"), 0.0),
            LocDeviation=_number(row.get("loc_deviation"), 0.0),
            GSDeviation=_number(row.get("gs_deviation"), 0.0),
        )
    failures = frozenset(
        FailureMode[name] for name in (row.get("faults") or []) if name in FailureMode.__members__)
    return Telemetry(
        lat=row.get("lat"), lon=row.get("lon"), groundspeed_ms=row.get("groundspeed_ms"),
        heading_true_deg=row.get("heading_true_deg"),
        heading_magnetic_deg=row.get("heading_magnetic_deg"),
        track_true_deg=row.get("track_true_deg"),
        track_magnetic_deg=row.get("track_magnetic_deg"),
        runway_heading_true_deg=row.get("runway_heading_true_deg"),
        runway_heading_magnetic_deg=row.get("runway_heading_magnetic_deg"),
        pitch_deg=row.get("pitch_deg"), roll_deg=row.get("roll_deg"),
        elevation_m=row.get("elevation_m"), agl_m=row.get("agl_m"),
        vy_ms=row.get("vertical_speed_ms"), p_rad=row.get("p_rad"), q_rad=row.get("q_rad"),
        r_rad=row.get("r_rad"), accel_long_g=row.get("accel_long_g"),
        accel_norm_g=row.get("accel_norm_g"), accel_side_g=row.get("accel_side_g"),
        wind_speed_ms=row.get("wind_speed_ms"), wind_dir_from_deg=row.get("wind_dir_from_deg"),
        lateral_deviation_sign=_number(row.get("lateral_deviation_sign"), 1.0),
        approach_inputs=approach, ias_ms_direct=row.get("ias_ms"),
        radio_altitude_ft_direct=row.get("radio_altitude_ft"),
        ils_valid_direct=_bool_or_none(row.get("ils_valid")),
        main_gear_contact_direct=_bool_or_none(row.get("main_gear_contact")),
        runway_heading_deg_direct=(row.get("runway_heading_magnetic_deg")
                                    or row.get("runway_heading_true_deg")),
        runway_length_m_direct=row.get("runway_length_m"),
        runway_width_m_direct=row.get("runway_width_m"),
        lateral_deviation_m_direct=row.get("lateral_deviation_m"),
        weight_on_wheels_direct=_bool_or_none(row.get("weight_on_wheels")),
        flight_phase_direct=row.get("flight_phase"), faults_direct=failures,
        agent_is_active_direct=_bool_or_none(row.get("agent_active")),
        valid=bool(row.get("valid", True)),
    )


def _apply_recorded_gains(controller, row: dict) -> None:
    for name, pid in controller_pids(controller).items():
        if pid is None:
            continue
        for gain in ("kp", "ki", "kd"):
            value = row.get(f"pid_{name}_{gain}")
            if value is not None:
                setattr(pid, gain, float(value))


def _parse_cell(value: str | None):
    if value in (None, ""):
        return None
    text = value.strip()
    if text in {"True", "False"}:
        return text == "True"
    if text[:1] in "[{" or text in {"true", "false", "null"}:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    try:
        number = float(text)
        return int(number) if number.is_integer() and not any(ch in text.lower() for ch in (".", "e")) else number
    except ValueError:
        return value


def _number(value, default=0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _bool_or_none(value):
    return None if value is None else bool(value)


def _equal(expected, actual, *, atol: float, rtol: float) -> tuple[bool, float]:
    if isinstance(expected, bool):
        return bool(expected) is bool(actual), 0.0
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        try:
            actual_number = float(actual)
        except (TypeError, ValueError):
            return False, math.inf
        error = abs(float(expected) - actual_number)
        return error <= atol + rtol * abs(float(expected)), error
    return expected == actual, 0.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ИСМПУ: deterministic offline replay")
    parser.add_argument("source", help="run-directory или telemetry.csv")
    parser.add_argument("--atol", type=float, default=1e-9)
    parser.add_argument("--rtol", type=float, default=1e-9)
    args = parser.parse_args(argv)
    report = replay_run(args.source, atol=args.atol, rtol=args.rtol)
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
