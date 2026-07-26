"""Импорт и проверка внешних CSV-прогонов roman_aviacia_ics."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from ismpu.utils.converts import Converts


def _number(row: dict, key: str, default=None):
    raw = row.get(key)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


class RomanLogImporter:
    """Потоково нормализует основной и authority CSV Романа."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def rows(self):
        with self.path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = set(reader.fieldnames or ())
            authority = "axis" in fields and "target_ra_ft" in fields
            for sequence, row in enumerate(reader):
                yield (
                    self._authority_row(row, sequence)
                    if authority else self._approach_row(row, sequence)
                )

    @staticmethod
    def _approach_row(row: dict, sequence: int) -> dict:
        normalized = {
            "sequence": sequence,
            "time_s": _number(row, "time_s", 0.0),
            "segment": "approach",
            "valid": 1,
            "groundspeed_ms": _number(row, "ground_speed_kt", 0.0) * Converts.KTS_TO_MS,
            "heading_true_deg": _number(row, "heading_deg"),
            "radio_altitude_ft": _number(row, "ra_ft"),
            "ias_ms": _number(row, "ias_kt", 0.0) * Converts.KTS_TO_MS,
            "pitch_deg": _number(row, "pitch_deg"),
            "roll_deg": _number(row, "roll_deg"),
            "vertical_speed_fpm": _number(row, "vs_fpm"),
            "lateral_deviation_m": _number(row, "lateral_deviation"),
            "loc_deviation": _number(row, "loc_ddm"),
            "gs_deviation": _number(row, "gs_ddm"),
            "magnetic_track_deg": _number(row, "track_magnetic_deg"),
            "cmd_elevator_g": _number(row, "elevator_cmd"),
            "cmd_aileron_deg": _number(row, "aileron_cmd_deg"),
            "cmd_throttle_norm": _number(row, "throttle_cmd_norm"),
            "cmd_rudder_norm": _number(row, "rudder_cmd_deg"),
            "criteria_status": row.get("criteria_status", ""),
            "envelope_warnings": row.get("envelope_warnings", ""),
        }
        for short, source in (
            ("roll", "roll"), ("pitch", "pitch"), ("air_speed", "speed"),
        ):
            for gain in ("kp", "ki", "kd"):
                normalized[f"pid_{short}_{gain}"] = _number(row, f"{source}_{gain}")
            normalized[f"pid_{short}_i"] = _number(row, f"{source}_i_term")
        return normalized

    @staticmethod
    def _authority_row(row: dict, sequence: int) -> dict:
        return {
            "sequence": sequence,
            "time_s": _number(row, "time_s", 0.0),
            "segment": row.get("segment", "approach"),
            "axis": row.get("axis"),
            "event": row.get("event"),
            "valid": 1,
            "groundspeed_ms": _number(row, "ground_speed_kt", 0.0) * Converts.KTS_TO_MS,
            "radio_altitude_ft": _number(row, "ra_ft"),
            "ias_ms": _number(row, "ias_kt", 0.0) * Converts.KTS_TO_MS,
            "pitch_deg": _number(row, "pitch_deg"),
            "roll_deg": _number(row, "roll_deg"),
            "vertical_speed_fpm": _number(row, "vs_fpm"),
            "cmd_elevator_g": _number(row, "elevator_cmd_g"),
            "cmd_aileron_deg": _number(row, "aileron_cmd_deg"),
            "cmd_throttle_norm": _number(row, "throttle_hold_norm"),
        }

    def summary(self) -> dict:
        count = 0
        first = last = None
        min_ra = max_ra = None
        for row in self.rows():
            count += 1
            current = row.get("time_s")
            first = current if first is None else first
            last = current
            ra = row.get("radio_altitude_ft")
            if ra is not None:
                min_ra = ra if min_ra is None else min(min_ra, ra)
                max_ra = ra if max_ra is None else max(max_ra, ra)
        return {
            "rows": count,
            "duration_s": (last - first) if first is not None and last is not None else 0.0,
            "min_ra_ft": min_ra,
            "max_ra_ft": max_ra,
        }


def verify_manifest(manifest_path: str | Path, source_root: str | Path) -> dict:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    root = Path(source_root) / manifest["base_path"]
    missing, changed, ok = [], [], []
    for name, expected in manifest["files"].items():
        path = root / name
        if not path.is_file():
            missing.append(name)
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected["sha256"] or path.stat().st_size != expected["bytes"]:
            changed.append(name)
        else:
            ok.append(name)
    return {"ok": ok, "missing": missing, "changed": changed}
