"""Проверяемое продвижение dashboard candidate в sparse scenario override."""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

from ismpu.config.json_config import scenario_from_document
from ismpu.config.run_matrix import (
    CATALOG_SHA256, SOURCE_SHA256, resolve_matrix_run, runs_for_code,
)
from ismpu.runtime.run_artifacts import json_sha256
from ismpu.runtime.run_reader import RunReader


PASS = "PASS"
_FIELDS = {
    "approach": {"roll_pid", "pitch_pid", "speed_pid"},
    "rollout": {"runway_center", "brake_l", "brake_r", "rev_l", "rev_r"},
    "taxi": {"runway_center", "brake_l", "brake_r", "rev_l", "rev_r"},
}


class PromotionError(ValueError):
    pass


def promote_candidate(
    candidate_path: str | Path,
    *,
    output: str | Path | None = None,
    accepted: bool = False,
    evidence_root: str | Path | None = None,
    verify_replay: bool = True,
) -> Path:
    """Проверить run и записать новый scenario JSON; registry исходников не меняется."""
    candidate_path = Path(candidate_path).resolve()
    candidate = _read_json(candidate_path)
    run_directory = candidate_path.parent.parent
    manifest, _report = _validate_run(run_directory, verify_replay=verify_replay)
    _validate_candidate(candidate, manifest, run_directory)

    segment = str(candidate["segment"])
    run_id = str(candidate.get("matrix_run_id") or "")
    if not run_id:
        raise PromotionError("candidate не привязан к конкретной строке матрицы")
    matrix_run = resolve_matrix_run(run_id)
    base = manifest["effective_configs"][segment]["control"]
    effective = candidate["effective_config"]
    patch = _gain_patch(base, effective, segment)

    status = "tuned"
    if accepted:
        _validate_full_evidence(
            candidate, run_directory, evidence_root, verify_replay=verify_replay)
        status = "accepted"

    document = copy.deepcopy(manifest["scenario"])
    profile = str(candidate["aircraft_profile"])
    try:
        controls = document["aircraft_controls"][profile]
    except KeyError as exc:
        raise PromotionError(f"scenario не содержит профиль {profile}") from exc
    overrides = controls.setdefault("run_overrides", {})
    destination = overrides.setdefault(run_id, {}).setdefault(segment, {})
    for field, values in patch.items():
        destination.setdefault(field, {}).update(values)
    controls["statuses"][segment] = status
    # Полная валидация schema + применимости override к строке матрицы до записи.
    scenario_from_document(document)

    target = (Path(output) if output is not None else
              candidate_path.with_name(f"{candidate_path.stem}.{status}.scenario.json"))
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        document, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(target)
    return target


def _validate_run(run_directory: Path, *, verify_replay: bool) -> tuple[dict, dict]:
    manifest = _read_json(run_directory / "manifest.json")
    report = _read_json(run_directory / "report.json")
    if report.get("status") != PASS or not report.get("acceptance_valid"):
        raise PromotionError(
            f"прогон не прошёл приёмку: status={report.get('status')}, "
            f"acceptance_valid={report.get('acceptance_valid')}")
    if manifest.get("recording_failed") or report.get("recording_failed"):
        raise PromotionError(
            f"ошибка recorder: {manifest.get('recording_error') or report.get('recording_error')}")
    metrics = report.get("metrics", {})
    if not isinstance(metrics, dict):
        raise PromotionError("report.metrics должен быть JSON object")
    if int(metrics.get("dropout_samples") or 0) != 0:
        raise PromotionError("в телеметрии есть dropout/error frames")
    if manifest.get("execution_id") != report.get("execution_id"):
        raise PromotionError("execution_id manifest/report не совпадает")
    if verify_replay:
        replay = RunReader(run_directory).replay(atol=1e-12, rtol=1e-12)
        if not replay.success:
            first = replay.mismatches[0] if replay.mismatches else None
            raise PromotionError(f"command replay failed: {first}")
    return manifest, report


def _validate_candidate(candidate: dict, manifest: dict, run_directory: Path) -> None:
    required = {
        "execution_id", "aircraft_profile", "segment", "config_revision",
        "matrix_run_id", "hashes", "effective_config",
    }
    missing = required - set(candidate)
    if missing:
        raise PromotionError(f"candidate: отсутствуют поля {sorted(missing)}")
    if candidate["execution_id"] != manifest.get("execution_id"):
        raise PromotionError("candidate execution_id не совпадает с run")
    segment = str(candidate["segment"])
    if segment not in _FIELDS:
        raise PromotionError(f"неизвестный segment: {segment}")
    if candidate["matrix_run_id"] != manifest.get("matrix_run_ids", {}).get(segment):
        raise PromotionError("candidate matrix_run_id не совпадает с manifest")
    row_hash, base_hash = _validate_manifest_hashes(
        manifest, segment, str(candidate["matrix_run_id"]))
    hashes = candidate["hashes"]
    expected = {
        "matrix_catalog_sha256": CATALOG_SHA256,
        "matrix_source_sha256": SOURCE_SHA256,
        "matrix_row_sha256": row_hash,
        "base_config_sha256": base_hash,
        "effective_config_sha256": json_sha256(candidate["effective_config"]),
    }
    for name, value in expected.items():
        if hashes.get(name) != value:
            raise PromotionError(f"hash mismatch: {name}")
    samples = list(RunReader(run_directory).samples())
    if not samples:
        raise PromotionError("прогон не содержит control samples")
    last = samples[-1]
    if last.segment != segment or last.config_revision != int(candidate["config_revision"]):
        raise PromotionError("candidate revision/segment не совпадает с последним sample")


def _gain_patch(base: dict, effective: dict, segment: str) -> dict:
    if set(base) != set(effective):
        raise PromotionError("candidate изменяет структуру effective config")
    patch = {}
    for field in base:
        before, after = base[field], effective[field]
        if before == after:
            continue
        if field not in _FIELDS[segment] or not isinstance(before, dict) or not isinstance(after, dict):
            raise PromotionError(f"dashboard candidate не вправе менять {field}")
        if set(before) != set(after):
            raise PromotionError(f"candidate изменяет структуру {field}")
        changed = {name: after[name] for name in before if before[name] != after[name]}
        illegal = set(changed) - {"kp", "ki", "kd"}
        if illegal:
            raise PromotionError(f"candidate содержит не-gain поля {field}: {sorted(illegal)}")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool)
               or not math.isfinite(float(value)) for value in changed.values()):
            raise PromotionError(f"candidate содержит нечисловой/неfinite gain в {field}")
        if changed:
            patch[field] = changed
    return patch


def _validate_full_evidence(
    candidate: dict,
    origin: Path,
    evidence_root: str | Path | None,
    *,
    verify_replay: bool,
) -> None:
    matrix_run = resolve_matrix_run(str(candidate["matrix_run_id"]))
    required = {item.matrix_run_id for item in runs_for_code(matrix_run.code)}
    passed = set()
    expected_hash = candidate["hashes"]["effective_config_sha256"]
    manifests = [origin / "manifest.json"]
    if evidence_root is not None:
        manifests.extend(Path(evidence_root).resolve().rglob("manifest.json"))
    for manifest_path in dict.fromkeys(manifests):
        manifest = _read_json(manifest_path)
        segment = str(candidate["segment"])
        run_id = manifest.get("matrix_run_ids", {}).get(segment)
        if run_id not in required or manifest.get("config_hashes", {}).get(segment) != expected_hash:
            continue
        _validate_manifest_hashes(manifest, segment, str(run_id))
        directory = manifest_path.parent
        _validate_run(directory, verify_replay=verify_replay)
        if any(event.get("event") in {"gain_change_applied", "gain_reverted"}
               for event in RunReader(directory).events()):
            raise PromotionError(
                f"accepted evidence {run_id} содержит live-изменение gains")
        passed.add(str(run_id))
    missing = sorted(required - passed)
    if missing:
        raise PromotionError(
            "accepted требует PASS полного набора строк с тем же config hash; "
            f"не хватает: {missing}")


def _validate_manifest_hashes(manifest: dict, segment: str, run_id: str) -> tuple[str, str]:
    """Пересчитать matrix/config hashes, а не доверять двум согласованно изменённым JSON."""
    if manifest.get("matrix_catalog_sha256") != CATALOG_SHA256:
        raise PromotionError("manifest matrix catalog hash не совпадает с текущим")
    if manifest.get("matrix_source_sha256") != SOURCE_SHA256:
        raise PromotionError("manifest matrix source hash не совпадает с текущим")
    matrix_run = resolve_matrix_run(run_id)
    if matrix_run.segment not in {segment, "through"}:
        raise PromotionError(f"matrix row {run_id} неприменима к segment {segment}")
    row_hash = json_sha256(matrix_run.cells)
    recorded_row = manifest.get("matrix_rows", {}).get(segment)
    if (manifest.get("matrix_row_hashes", {}).get(segment) != row_hash
            or json_sha256(recorded_row) != row_hash):
        raise PromotionError("manifest matrix row hash не совпадает с текущей строкой")
    try:
        control = manifest["effective_configs"][segment]["control"]
    except (KeyError, TypeError) as exc:
        raise PromotionError(f"manifest не содержит effective config для {segment}") from exc
    config_hash = json_sha256(control)
    if manifest.get("config_hashes", {}).get(segment) != config_hash:
        raise PromotionError("manifest config hash не совпадает с effective config")
    return row_hash, config_hash


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise PromotionError(f"нет файла: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError(f"не удалось прочитать {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PromotionError(f"ожидался JSON object: {path}")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ИСМПУ: validate and promote PID candidate")
    parser.add_argument("candidate")
    parser.add_argument("--output")
    parser.add_argument("--accepted", action="store_true")
    parser.add_argument("--evidence-root")
    args = parser.parse_args(argv)
    result = promote_candidate(
        args.candidate, output=args.output, accepted=args.accepted,
        evidence_root=args.evidence_root)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
