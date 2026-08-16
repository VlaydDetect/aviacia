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
from ismpu.config.requirements import CENTERLINE_ALIGN_HEIGHT_M
from ismpu.config.runway_profiles import RunwayProfile
from ismpu.config.scenarios import ProfileStatus, weather_distance
from ismpu.config.segments import FlightSegment
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.envs.weather import RunwayCondition, WeatherState
from ismpu.runtime.evaluate import (
    FAIL, PASS, evaluate_matrix_run, evaluate_tz, verdict_of,
)
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
    selected_runs = tuple(dict.fromkeys(
        getattr(scenario, "matrix_runs", {}).values()))
    matrix_evaluations = []
    if selected_runs:
        for run_id in selected_runs:
            matrix_run = resolve_matrix_run(run_id)
            criteria = evaluate_matrix_run(matrix_run, metrics)
            matrix_evaluations.append({
                "matrix_run_id": run_id,
                "code": matrix_run.code,
                "source_criteria": matrix_run.criteria,
                "verdict": verdict_of(criteria),
                "criteria": [item.as_dict() for item in criteria],
            })
        acceptance_criteria = [
            item for evaluation in matrix_evaluations
            for item in evaluation["criteria"]
        ]
        verdict = FAIL if any(
            item["verdict"] == FAIL for item in matrix_evaluations) else PASS
        ground_criteria = []
    else:
        ground_criteria = evaluate_tz(metrics["tz_diagnostics"], scenario) \
            if metrics["ground_samples"] else []
        acceptance_criteria = [item.as_dict() for item in ground_criteria]
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
    elif verdict == FAIL or (not selected_runs and approach_status == FAIL):
        status = FAIL
    elif not selected_runs and approach_status == "INCOMPLETE":
        status = "INCOMPLETE"
    elif stop_reason in {"completed", "operator_completed"}:
        status = PASS
    else:
        status = "INCOMPLETE"
    matrix_results = _matrix_results(
        scenario, status, metrics, recording_error, matrix_evaluations)
    profile = str(reader.manifest.get("aircraft_profile") or "mc21")
    accepted_segments = _accepted_segments(scenario, profile, metrics)
    expert_classical = reader.manifest.get("control_policy", "classical") == "classical"
    return {
        "schema_version": 2,
        "execution_id": reader.manifest.get("execution_id"),
        "stop_reason": stop_reason,
        "status": status,
        "acceptance_valid": acceptance_valid,
        "sft_eligible": (
            acceptance_valid and status == PASS and accepted_segments and expert_classical),
        "recording_failed": recording_failed,
        "recording_error": recording_error,
        "metrics": metrics,
        "criteria": acceptance_criteria,
        "approach_criteria_a11": approach_criteria,
        "matrix_evaluations": matrix_evaluations,
        "environment_diagnostics": _environment_diagnostics(scenario, metrics),
        "matrix_results": matrix_results,
        "runtime": runtime_report,
    }


def _metrics(reader: RunReader) -> dict:
    """Свести поток записанных кадров в метрики ТЗ, SFT и диагностики стенда."""
    samples = valid_samples = dropout_samples = ground_samples = approach_samples = 0
    saturation_ticks = sft_fallbacks = 0
    first_time = last_time = final_speed = final_distance = None
    xte_rollout = xte_taxi = heading_max = None
    approach_course = approach_glideslope = approach_axis = None
    approach_axis_at_30m = approach_axis_altitude_error_ft = None
    approach_runway_heading = None
    previous_approach_ra = previous_approach_xte = None
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
    weather_by_segment: dict[str, dict] = {}
    segment_samples: dict[str, int] = {}
    applied_gains: dict[str, dict] = {}
    feedback_samples: dict[str, int] = {}
    previous_segment = None
    handover = None
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
        segment_samples[segment] = segment_samples.get(segment, 0) + 1
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
            ias = _optional(row.get("ias_ms"))
            ias_kts = None if ias is None else ias * Converts.MS_TO_KTS
            normal_g = _optional(row.get("accel_norm_g"))
            lateral_g = _optional(row.get("accel_side_g"))
            touchdown = {
                "tick_id": row.get("tick_id"), "time_s": time_s,
                "groundspeed_ms": speed,
                "groundspeed_kts": speed_kts,
                "indicated_airspeed_kts": ias_kts,
                "along_track_m": _touchdown_along_track(row),
                "vapp_kt": vapp,
                "vertical_speed_ms": _optional(row.get("vertical_speed_ms")),
                "vertical_speed_fpm": sink_fpm,
                "normal_load_g": normal_g,
                "lateral_load_g": lateral_g,
                "sink_situation": sink_situation(sink_fpm).name if sink_fpm is not None else None,
                "speed_situation": (
                    touchdown_speed_situation(ias_kts, vapp).name
                    if ias_kts is not None and vapp is not None else None),
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
            radio_altitude_ft = _optional(row.get("radio_altitude_ft"))
            if radio_altitude_ft is not None:
                xte = _optional(row.get("lateral_deviation_m"))
                if xte is None:
                    projection = _runway_projection(row)
                    xte = projection[0] if projection is not None else None
                target_ft = CENTERLINE_ALIGN_HEIGHT_M / Converts.FT_TO_M
                if xte is not None and radio_altitude_ft == target_ft:
                    approach_axis_at_30m = abs(xte)
                    approach_axis_altitude_error_ft = 0.0
                elif (
                    xte is not None
                    and previous_approach_ra is not None
                    and previous_approach_xte is not None
                    and (previous_approach_ra - target_ft)
                    * (radio_altitude_ft - target_ft) <= 0.0
                    and radio_altitude_ft != previous_approach_ra
                ):
                    fraction = (
                        (target_ft - previous_approach_ra)
                        / (radio_altitude_ft - previous_approach_ra))
                    approach_axis_at_30m = abs(
                        previous_approach_xte + fraction * (xte - previous_approach_xte))
                    approach_axis_altitude_error_ft = 0.0
                previous_approach_ra, previous_approach_xte = radio_altitude_ft, xte
            approach_runway_heading = _max_abs(
                approach_runway_heading, _approach_runway_heading_error(row))
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
                heading_max = _max_abs(heading_max, _runway_heading_error(row))
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
        # Fallback считается по фактически записанным тактам, а не по внутреннему
        # счётчику модели: так report остаётся воспроизводимым только из артефакта.
        if bool(row.get("sft_fallback")):
            sft_fallbacks += 1

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
            weather_by_segment[segment] = row["weather"]

        if previous_segment == FlightSegment.APPROACH.value \
                and segment != FlightSegment.APPROACH.value and handover is None:
            handover = _handover_ratio(row, reader.manifest)
        previous_segment = segment

        revision_key = f"{segment}:{int(_number(row.get('config_revision'), 0))}"
        gains = {}
        names = ("roll", "pitch", "air_speed") if segment == "approach" else (
            "steer", "brake_l", "brake_r", "reverse_l", "reverse_r")
        for name in names:
            values = {
                gain: _optional(row.get(f"pid_{name}_{gain}"))
                for gain in ("kp", "ki", "kd")
            }
            if all(value is not None for value in values.values()):
                gains[name] = values
        if gains:
            applied_gains[revision_key] = gains
        for name in (
            "feedback_rudder_deg", "feedback_nose_wheel_deg",
            "feedback_brake_left_mm", "feedback_brake_right_mm",
            "feedback_throttle_left_deg", "feedback_throttle_right_deg",
            "feedback_thrust_left", "feedback_thrust_right",
            "feedback_longitudinal_accel_g", "feedback_lateral_accel_g",
            "feedback_yaw_rate_rad_s",
        ):
            if _optional(row.get(name)) is not None:
                feedback_samples[name] = feedback_samples.get(name, 0) + 1

    duration = (last_time - first_time) if samples else 0.0
    diagnostics = {
        "samples": ground_samples,
        "xte_rollout_max_m": xte_rollout,
        "xte_taxi_max_m": xte_taxi,
        "heading_max_deg": heading_max,
        "final_speed_kts": None if final_speed is None else final_speed * Converts.MS_TO_KTS,
        "saturation_ratio": saturation_ticks / valid_samples if valid_samples else None,
        "sft_fallbacks": sft_fallbacks,
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
            "approach_axis_at_30m_m": approach_axis_at_30m,
            "approach_axis_sample_height_error_ft": approach_axis_altitude_error_ft,
            "approach_runway_heading_deg": approach_runway_heading,
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
            "by_channel_ratio": {
                name: count / valid_samples for name, count in saturation_by_channel.items()
            } if valid_samples else {},
        },
        "applied_gains": applied_gains,
        "feedback_samples": feedback_samples,
        "segment_samples": segment_samples,
        "handover": handover,
        "environment": last_weather,
        "environment_by_segment": weather_by_segment,
        "tz_diagnostics": diagnostics,
    }


def _matrix_results(
    scenario, status: str, metrics: dict, error: str | None, evaluations: list[dict],
) -> list[dict]:
    results = []
    by_run = {item["matrix_run_id"]: item for item in evaluations}
    for run_id in dict.fromkeys(getattr(scenario, "matrix_runs", {}).values()):
        matrix_run = resolve_matrix_run(run_id)
        evaluation = by_run.get(run_id, {})
        criteria = evaluation.get("criteria", ())
        measured = "; ".join(
            f"{item['name']}={item['measured']:.3f}"
            for item in criteria if item.get("measured") is not None)
        row = dict(matrix_run.cells)
        row[RESULT_COLUMNS[0]] = (
            status if status in {"INVALID", "INCOMPLETE"}
            else evaluation.get("verdict", status))
        row[RESULT_COLUMNS[1]] = measured
        row[RESULT_COLUMNS[2]] = error or (
            f"run_id={run_id}; samples={metrics['samples']}; "
            f"duration={metrics['duration_s']:.2f}s")
        results.append(row)
    return results


def _accepted_segments(scenario, profile: str, metrics: dict) -> bool:
    """SFT получает только PASS, записанный уже под accepted-конфигурацией."""
    segments = {
        FlightSegment(name) for name, count in metrics.get("segment_samples", {}).items()
        if count and name in {item.value for item in FlightSegment}
    }
    if not segments:
        return False
    try:
        return all(
            scenario.control_status(profile, segment) is ProfileStatus.ACCEPTED
            for segment in segments)
    except KeyError:
        return False


def _environment_diagnostics(scenario, metrics: dict) -> list[dict]:
    """Ожидаемая/фактическая погода видна в отчёте, но не подменяет отказной гейт."""
    result = []
    actual_by_segment = metrics.get("environment_by_segment", {})
    for segment, run_id in getattr(scenario, "matrix_runs", {}).items():
        expected = scenario.conditions_for(segment).weather
        actual_raw = actual_by_segment.get(segment.value)
        actual = None
        if isinstance(actual_raw, dict):
            try:
                actual = WeatherState.from_dict(actual_raw)
            except (TypeError, ValueError):
                actual = None
        result.append({
            "matrix_run_id": run_id,
            "segment": segment.value,
            "expected": expected.to_dict(),
            "actual": actual_raw,
            "available": actual is not None,
            "weather_distance": (
                weather_distance(expected, actual) if actual is not None else None),
            "weather_matches": (
                weather_distance(expected, actual) <= 1e-3 if actual is not None else False),
            "diagnostics": {
                "friction": actual.runway_friction if actual is not None else None,
                "wind_speed_kts": actual.wind_speed_kts if actual is not None else None,
                "rain_pct": actual.rain_pct if actual is not None else None,
                "aquaplaning_risk": (
                    actual.runway_friction >= RunwayCondition.PUDDLY.value
                    if actual is not None else None),
            },
            "acceptance_impact": "report_only",
        })
    return result


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


def _runway_projection(row) -> tuple[float, float] | None:
    values = {
        name: _optional(row.get(name)) for name in (
            "lat", "lon", "runway_threshold_lat", "runway_threshold_lon",
            "runway_end_lat", "runway_end_lon",
        )
    }
    if any(value is None for value in values.values()):
        return None
    if values["lat"] == 0.0 and values["lon"] == 0.0:
        return None
    profile = RunwayProfile(
        name=str(row.get("runway_profile_name") or "recorded"),
        airport=str(row.get("runway_airport") or ""),
        runway=str(row.get("runway_designator") or ""),
        threshold_lat=values["runway_threshold_lat"],
        threshold_lon=values["runway_threshold_lon"],
        end_lat=values["runway_end_lat"],
        end_lon=values["runway_end_lon"],
        heading_true_deg=_number(row.get("runway_heading_true_deg"), 0.0),
        elevation_m=_number(row.get("runway_elevation_m"), 0.0),
        width_m=_number(row.get("runway_width_m"), 60.0),
    )
    guidance = RunwayTracker(runway_profile=profile).guidance(
        values["lat"], values["lon"],
        _number(row.get("track_true_deg"), profile.heading_true_deg),
        _number(row.get("groundspeed_ms"), 0.0),
        aircraft_heading_deg=_number(
            row.get("heading_true_deg"), profile.heading_true_deg),
        runway_profile=profile,
        source="report",
    )
    return guidance.xte, guidance.along_track


def _touchdown_along_track(row) -> float | None:
    direct = _optional(row.get("guidance_along_track_m"))
    if direct is not None:
        return direct
    projection = _runway_projection(row)
    return projection[1] if projection is not None else None


def _wrapped_error(target, actual) -> float | None:
    target, actual = _optional(target), _optional(actual)
    if target is None or actual is None:
        return None
    return (target - actual + 180.0) % 360.0 - 180.0


def _approach_runway_heading_error(row) -> float | None:
    error = _wrapped_error(
        row.get("approach_input_RunwayHeading"),
        row.get("approach_input_TrkAngleMagnetic"),
    )
    return error if error is not None else _wrapped_error(
        row.get("runway_heading_magnetic_deg"), row.get("track_magnetic_deg"))


def _runway_heading_error(row) -> float | None:
    error = _wrapped_error(
        row.get("runway_heading_true_deg"), row.get("heading_true_deg"))
    if error is None:
        error = _wrapped_error(
            row.get("runway_heading_magnetic_deg"), row.get("heading_magnetic_deg"))
    return error if error is not None else _optional(row.get("guidance_heading_error_deg"))


def _handover_ratio(row, manifest: dict) -> dict:
    segment = str(row.get("segment") or "rollout")
    try:
        control = manifest["effective_configs"][segment]["control"]
    except (KeyError, TypeError):
        return {"max_rate_ratio": None, "reason": "нет effective config участка"}
    dt = _optional(row.get("dt"))
    if dt is None or dt <= 0.0:
        return {"max_rate_ratio": None, "reason": "нет dt первого наземного такта"}
    groups = {
        "steering": (
            control.get("steering_rate_per_s"),
            ("cmd_rudder_norm", "cmd_pedal_norm", "cmd_tiller_norm")),
        "brake": (
            control.get("brake_rate_per_s"), ("cmd_brake_l", "cmd_brake_r")),
        "reverse": (
            control.get("reverse_rate_per_s"), ("cmd_reverse_l", "cmd_reverse_r")),
    }
    ratios = {}
    for name, (rate, fields) in groups.items():
        rate = _optional(rate)
        values = [_optional(row.get(field)) for field in fields]
        values = [abs(value) for value in values if value is not None]
        if rate is not None and rate > 0.0 and values:
            ratios[name] = max(values) / (rate * dt)
    return {
        "max_rate_ratio": max(ratios.values()) if ratios else None,
        "by_channel": ratios,
        "basis": "first_ground_command / configured_rate_limit / dt",
    }


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
