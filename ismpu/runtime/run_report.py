"""Расчёт отчёта прогона и сборка результатов матрицы."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from ismpu.config.criticality import (
    lateral_load_situation, normal_load_situation, sink_situation,
    touchdown_speed_situation,
)
from ismpu.config.run_matrix import COLUMNS, RESULT_COLUMNS, resolve_matrix_run
from ismpu.config.segments import FlightSegment
from ismpu.runtime.evaluate import FAIL, PASS, evaluate_tz, verdict_of
from ismpu.runtime.run_reader import RunReader
from ismpu.utils.converts import Converts


def build_run_report(
    run_directory: str | Path,
    *,
    scenario,
    runtime_report=None,
    recording_failed: bool = False,
    recording_error: str | None = None,
) -> dict:
    """Потоково посчитать метрики без загрузки полёта в память."""
    reader = RunReader(run_directory)
    recording_failed = recording_failed or bool(reader.manifest.get("recording_failed"))
    recording_error = recording_error or reader.manifest.get("recording_error")
    metrics = _metrics(reader)
    runtime_report = runtime_report if isinstance(runtime_report, dict) else {}
    conditions_valid = bool(runtime_report.get("conditions_valid", True))
    ground_criteria = evaluate_tz(metrics["tz_diagnostics"], scenario) \
        if metrics["ground_samples"] else []
    verdict = verdict_of(ground_criteria) if ground_criteria else PASS
    approach_criteria = runtime_report.get("approach_criteria_a11")
    approach_status = (
        approach_criteria.get("status")
        if isinstance(approach_criteria, dict) and metrics["approach_samples"] else None)
    acceptance_valid = (
        not recording_failed and conditions_valid and metrics["valid_samples"] > 0)
    stop_reason = runtime_report.get("stop_reason")
    if not acceptance_valid:
        status = "INVALID"
    elif verdict == FAIL or approach_status == FAIL:
        status = FAIL
    elif approach_status == "INCOMPLETE":
        status = "INCOMPLETE"
    elif stop_reason == "completed":
        status = PASS
    else:
        status = "INCOMPLETE"
    matrix_results = _matrix_results(scenario, status, metrics, recording_error)
    return {
        "schema_version": 1,
        "execution_id": reader.manifest.get("execution_id"),
        "stop_reason": stop_reason,
        "status": status,
        "acceptance_valid": acceptance_valid,
        "sft_eligible": acceptance_valid and status == PASS,
        "recording_failed": recording_failed,
        "recording_error": recording_error,
        "metrics": metrics,
        "criteria": [item.as_dict() for item in ground_criteria],
        "approach_criteria_a11": approach_criteria,
        "matrix_results": matrix_results,
        "runtime": runtime_report,
    }


def _metrics(reader: RunReader) -> dict:
    samples = valid_samples = dropout_samples = ground_samples = approach_samples = saturation_ticks = 0
    first_time = last_time = final_speed = final_distance = None
    xte_rollout = xte_taxi = heading_max = None
    approach_course = approach_glideslope = approach_axis = None
    approach_ias_min = approach_ias_max = None
    tolerance_violation_ticks = 0
    envelope_warnings: dict[str, int] = {}
    speed_error_max = speed_error_sq = speed_error_count = 0
    touchdown = None
    previous_contact = False
    previous_failures = ()
    failure_at = response_delay = None
    previous_commands = None
    last_weather = None
    saturation_by_channel: dict[str, int] = {}
    for row in reader.rows():
        samples += 1
        time_s = _number(row.get("time_s"), 0.0)
        first_time = time_s if first_time is None else first_time
        last_time = time_s
        if not bool(row.get("valid")):
            dropout_samples += 1
            continue
        valid_samples += 1
        segment = str(row.get("segment") or "unknown")
        speed = _optional(row.get("groundspeed_ms"))
        if speed is not None:
            final_speed = speed
        distance = _optional(row.get("ground_distance_m"))
        if distance is not None:
            final_distance = distance
        contact = bool(row.get("main_gear_contact"))
        if (contact and not previous_contact and touchdown is None
                and (approach_samples > 0 or valid_samples > 1)):
            sink_fpm = _touchdown_vs_fpm(row)
            limits = row.get("approach_limits") or {}
            vapp = _optional(limits.get("vapp_kt")) if isinstance(limits, dict) else None
            speed_kts = None if speed is None else speed * Converts.MS_TO_KTS
            normal_g = _optional(row.get("accel_norm_g"))
            lateral_g = _optional(row.get("accel_side_g"))
            touchdown = {
                "tick_id": row.get("tick_id"), "time_s": time_s,
                "groundspeed_ms": speed,
                "groundspeed_kts": speed_kts,
                "vertical_speed_ms": _optional(row.get("vertical_speed_ms")),
                "vertical_speed_fpm": sink_fpm,
                "normal_load_g": normal_g,
                "lateral_load_g": lateral_g,
                "sink_situation": sink_situation(sink_fpm).name if sink_fpm is not None else None,
                "speed_situation": (
                    touchdown_speed_situation(speed_kts, vapp).name
                    if speed_kts is not None and vapp is not None else None),
                "normal_load_situation": (
                    normal_load_situation(normal_g).name if normal_g is not None else None),
                "lateral_load_situation": (
                    lateral_load_situation(lateral_g).name if lateral_g is not None else None),
            }
        previous_contact = contact

        if segment == FlightSegment.APPROACH.value:
            approach_samples += 1
            approach_course = _max_abs(approach_course, row.get("approach_course_deg"))
            approach_glideslope = _max_abs(
                approach_glideslope, row.get("approach_glideslope_deg"))
            approach_axis = _max_abs(approach_axis, row.get("lateral_deviation_m"))
            ias = _optional(row.get("approach_input_IndicatedAirspeed"))
            if ias is not None:
                approach_ias_min = ias if approach_ias_min is None else min(approach_ias_min, ias)
                approach_ias_max = ias if approach_ias_max is None else max(approach_ias_max, ias)
            tolerance = row.get("approach_tolerances")
            if isinstance(tolerance, dict) and not tolerance.get("landing_allowed", True):
                tolerance_violation_ticks += 1
            for warning in row.get("approach_envelope_warnings") or ():
                envelope_warnings[str(warning)] = envelope_warnings.get(str(warning), 0) + 1
        else:
            ground_samples += 1
            xte = row.get("guidance_xte_m")
            if segment == FlightSegment.TAXI.value:
                xte_taxi = _max_abs(xte_taxi, xte)
            else:
                xte_rollout = _max_abs(xte_rollout, xte)
            if speed is not None and speed * Converts.MS_TO_KTS >= 30.0:
                heading_max = _max_abs(heading_max, row.get("guidance_course_error_deg"))
            error = _optional(row.get("ground_speed_error_ms"))
            if error is not None:
                speed_error_max = max(speed_error_max, abs(error))
                speed_error_sq += error * error
                speed_error_count += 1

        saturated = []
        for name in ("roll", "pitch", "air_speed", "steer", "brake_l", "brake_r",
                     "reverse_l", "reverse_r"):
            if bool(row.get(f"pid_{name}_saturated")):
                saturated.append(name)
                saturation_by_channel[name] = saturation_by_channel.get(name, 0) + 1
        allocator = row.get("allocator_saturated") or []
        if isinstance(allocator, str):
            allocator = [item for item in allocator.split(";") if item]
        for name in allocator:
            key = f"allocator:{name}"
            saturation_by_channel[key] = saturation_by_channel.get(key, 0) + 1
        if saturated or allocator:
            saturation_ticks += 1

        failures = tuple(row.get("faults") or ())
        commands = tuple(_optional(row.get(name)) for name in (
            "cmd_rudder_norm", "cmd_pedal_norm", "cmd_tiller_norm", "cmd_brake_l",
            "cmd_brake_r", "cmd_reverse_l", "cmd_reverse_r"))
        if failures != previous_failures:
            failure_at = time_s
            response_delay = 0.0 if samples == 1 else None
        elif failure_at is not None and response_delay is None and previous_commands is not None:
            if any(a is not None and b is not None and abs(a - b) > 1e-6
                   for a, b in zip(commands, previous_commands)):
                response_delay = time_s - failure_at
        previous_failures, previous_commands = failures, commands
        if isinstance(row.get("weather"), dict):
            last_weather = row["weather"]

    duration = (last_time - first_time) if samples else 0.0
    diagnostics = {
        "samples": ground_samples,
        "xte_rollout_max_m": xte_rollout,
        "xte_taxi_max_m": xte_taxi,
        "heading_max_deg": heading_max,
        "final_speed_kts": None if final_speed is None else final_speed * Converts.MS_TO_KTS,
        "saturation_ratio": saturation_ticks / valid_samples if valid_samples else None,
        "shield_fallbacks": 0,
        "rate_p95": {},
    }
    return {
        "samples": samples, "valid_samples": valid_samples,
        "dropout_samples": dropout_samples,
        "dropout_ratio": dropout_samples / samples if samples else None,
        "approach_samples": approach_samples,
        "ground_samples": ground_samples, "duration_s": duration,
        "distance_m": final_distance,
        "max_deviations": {
            "approach_course_deg": approach_course,
            "approach_glideslope_deg": approach_glideslope,
            "approach_axis_m": approach_axis,
            "rollout_xte_m": xte_rollout, "taxi_xte_m": xte_taxi,
            "runway_heading_deg": heading_max,
        },
        "touchdown": touchdown,
        "approach_envelope": {
            "ias_min_kt": approach_ias_min,
            "ias_max_kt": approach_ias_max,
            "tolerance_violation_ticks": tolerance_violation_ticks,
            "warnings": envelope_warnings,
        },
        "speed_profile": {
            "max_abs_error_ms": speed_error_max if speed_error_count else None,
            "rmse_ms": math.sqrt(speed_error_sq / speed_error_count) if speed_error_count else None,
            "final_speed_ms": final_speed,
        },
        "failure_response_delay_s": response_delay,
        "failure_response_basis": "first ground actuator command delta > 1e-6",
        "saturation": {
            "ticks": saturation_ticks,
            "ratio": saturation_ticks / valid_samples if valid_samples else None,
            "by_channel": saturation_by_channel,
        },
        "environment": last_weather,
        "tz_diagnostics": diagnostics,
    }


def _matrix_results(scenario, status: str, metrics: dict, error: str | None) -> list[dict]:
    results = []
    deviations = metrics["max_deviations"]
    measured = "; ".join(
        f"{name}={value:.3f}" for name, value in deviations.items() if value is not None)
    for segment, run_id in getattr(scenario, "matrix_runs", {}).items():
        matrix_run = resolve_matrix_run(run_id)
        row = dict(matrix_run.cells)
        row[RESULT_COLUMNS[0]] = status
        row[RESULT_COLUMNS[1]] = measured
        row[RESULT_COLUMNS[2]] = error or (
            f"segment={segment.value}; samples={metrics['samples']}; "
            f"duration={metrics['duration_s']:.2f}s")
        results.append(row)
    return results


def aggregate_matrix_results(root: str | Path, output: str | Path | None = None) -> Path:
    """Собрать последние результаты выбранных строк в CSV с колонками исходной книги."""
    root = Path(root)
    latest: dict[str, tuple[str, dict]] = {}
    manifests = [root / "manifest.json"] if (root / "manifest.json").is_file() \
        else list(root.rglob("manifest.json"))
    for manifest_path in manifests:
        report_path = manifest_path.with_name("report.json")
        if not report_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        stamp = str(manifest.get("finished_at") or manifest.get("started_at") or "")
        for row in report.get("matrix_results", ()):
            run_id = f"{row.get('Шифр')}/{row.get('Прогон')}"
            if run_id not in latest or stamp >= latest[run_id][0]:
                latest[run_id] = (stamp, row)
    output = Path(output) if output is not None else root / "matrix-results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for _stamp, row in sorted(latest.values(), key=lambda item: int(item[1].get("№", 0))):
            writer.writerow({name: row.get(name, "") for name in COLUMNS})
    return output


def _touchdown_vs_fpm(row) -> float | None:
    direct = _optional(row.get("approach_input_VerticalSpeed"))
    if direct is not None:
        return direct
    value = _optional(row.get("vertical_speed_ms"))
    return None if value is None else value / Converts.FTM_TO_MS


def _optional(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _number(value, default=0.0):
    result = _optional(value)
    return default if result is None else result


def _max_abs(current, value):
    value = _optional(value)
    return current if value is None else max(current or 0.0, abs(value))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ИСМПУ: отчёты прогонов")
    sub = parser.add_subparsers(dest="command", required=True)
    aggregate = sub.add_parser("aggregate", help="собрать matrix-results.csv")
    aggregate.add_argument("root", nargs="?", default="runs")
    aggregate.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    if args.command == "aggregate":
        print(aggregate_matrix_results(args.root, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
