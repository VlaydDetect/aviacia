"""Порядок и фактический статус кампании из 280 матричных прогонов."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from ismpu.config.run_matrix import MATRIX_RUNS, resolve_matrix_run, runs_for_code
from ismpu.runtime.run_report import aggregate_matrix_results


_CODE_PHASE = {
    "Б.1.2": 3,
    "Б.2.1": 4, "Б.2.2": 4, "Б.2.3": 4,
    "Б.3.1": 5, "Б.3.2": 5, "Б.3.3": 5,
    "А.1.1": 6, "А.1.2": 6,
    "А.2.1": 7, "А.2.2": 7, "А.2.3": 7,
    "А.3.1": 7, "А.3.2": 7, "А.3.3": 7, "А.3.4": 7,
    "А.4.1": 7, "А.4.2": 7, "А.4.3": 7,
    "Б.4.1": 8, "Б.4.2": 8,
}
_ORDERED_CODES = tuple(_CODE_PHASE)


def campaign_rows():
    """Канонический порядок этапа 7; первая строка Б.1.1 вынесена отдельно."""
    b11 = runs_for_code("Б.1.1")
    rows = (b11[0], *b11[1:])
    for code in _ORDERED_CODES:
        rows += runs_for_code(code)
    if len(rows) != len(MATRIX_RUNS) or len({row.matrix_run_id for row in rows}) != len(rows):
        raise RuntimeError("порядок кампании не покрывает ровно 280 строк матрицы")
    return rows


def campaign_phase(matrix_run) -> int:
    if matrix_run.matrix_run_id == "Б.1.1/1":
        return 1
    if matrix_run.code == "Б.1.1":
        return 2
    return _CODE_PHASE[matrix_run.code]


def scan_campaign(root: str | Path = "runs") -> list[dict]:
    """Последняя попытка каждой строки; отдельный изменяемый ledger не создаётся."""
    root = Path(root)
    manifests = [root / "manifest.json"] if (root / "manifest.json").is_file() \
        else list(root.rglob("manifest.json")) if root.exists() else []
    latest: dict[str, tuple[str, dict]] = {}
    for manifest_path in manifests:
        report_path = manifest_path.with_name("report.json")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            report = (
                json.loads(report_path.read_text(encoding="utf-8"))
                if report_path.is_file() else {})
        except (OSError, json.JSONDecodeError):
            continue
        stamp = str(manifest.get("finished_at") or manifest.get("started_at") or "")
        run_ids = dict.fromkeys(manifest.get("matrix_run_ids", {}).values())
        for run_id in run_ids:
            try:
                resolve_matrix_run(str(run_id))
            except KeyError:
                continue
            attempt = {
                "status": str(report.get("status") or "INCOMPLETE").upper(),
                "acceptance_valid": bool(report.get("acceptance_valid", False)),
                "sft_eligible": bool(report.get("sft_eligible", False)),
                "execution_id": manifest.get("execution_id"),
                "timestamp": stamp,
                "directory": str(manifest_path.parent.resolve()),
                "config_status": _config_status(manifest, str(run_id)),
                "candidate_count": len(list((manifest_path.parent / "candidates").glob("*.json"))),
            }
            if run_id not in latest or stamp >= latest[run_id][0]:
                latest[str(run_id)] = (stamp, attempt)

    result = []
    for row in campaign_rows():
        attempt = latest.get(row.matrix_run_id, ("", {}))[1]
        result.append({
            "phase": campaign_phase(row),
            "matrix_run_id": row.matrix_run_id,
            "code": row.code,
            "condition": row.condition.code,
            "status": "PENDING",
            **attempt,
        })
    return result


def next_campaign_row(root: str | Path = "runs"):
    item = next((item for item in scan_campaign(root) if item["status"] != "PASS"), None)
    return resolve_matrix_run(item["matrix_run_id"]) if item is not None else None


def campaign_summary(root: str | Path = "runs") -> dict:
    rows = scan_campaign(root)
    counts = Counter(item["status"] for item in rows)
    next_row = next((item for item in rows if item["status"] != "PASS"), None)
    return {
        "total": len(rows),
        "counts": dict(sorted(counts.items())),
        "next": next_row,
        "complete": next_row is None,
    }


def _config_status(manifest: dict, run_id: str) -> dict[str, str]:
    scenario = manifest.get("scenario")
    profile = str(manifest.get("aircraft_profile") or "mc21")
    if not isinstance(scenario, dict):
        return {}
    controls = scenario.get("aircraft_controls", {}).get(profile, {})
    statuses = controls.get("statuses", {}) if isinstance(controls, dict) else {}
    return {
        segment: str(statuses.get(segment, "unknown"))
        for segment, selected in manifest.get("matrix_run_ids", {}).items()
        if selected == run_id
    }


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="ИСМПУ: кампания настройки 280 строк")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "status", "next"):
        command = sub.add_parser(name)
        command.add_argument("root", nargs="?", default="runs")
    report = sub.add_parser("report")
    report.add_argument("root", nargs="?", default="runs")
    report.add_argument("--output")
    args = parser.parse_args(argv)

    if args.command == "report":
        print(aggregate_matrix_results(args.root, args.output))
    elif args.command == "status":
        print(json.dumps(campaign_summary(args.root), ensure_ascii=False, indent=2))
    elif args.command == "next":
        row = next_campaign_row(args.root)
        print(json.dumps(None if row is None else {
            "phase": campaign_phase(row),
            "matrix_run_id": row.matrix_run_id,
            "condition": row.condition.code,
            "operator_setup": row.operator_setup,
            "criteria": row.criteria,
        }, ensure_ascii=False, indent=2))
    else:
        for row in campaign_rows():
            print(f"{campaign_phase(row)}\t{row.matrix_run_id}\t{row.condition.code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
