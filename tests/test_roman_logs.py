import hashlib
import json

import pytest

from ismpu.runtime.roman_logs import RomanLogImporter, verify_manifest
from ismpu.utils.converts import Converts


@pytest.fixture
def roman_csv(tmp_path):
    path = tmp_path / "roman.csv"
    path.write_text(
        "time_s,ground_speed_kt,heading_deg,ra_ft,ias_kt,pitch_deg,roll_deg,"
        "vs_fpm,loc_ddm,gs_ddm,track_magnetic_deg,elevator_cmd,"
        "aileron_cmd_deg,throttle_cmd_norm,roll_kp,pitch_ki,speed_kd\n"
        "0.0,150,75,1000,140,2,1,-750,0.01,-0.02,74.8,0.1,2,0.5,-7,0.2,0.3\n"
        "0.1,149,75,990,139,2,1,-740,0,0,75,0,1,0.49,-7,0.2,0.3\n",
        encoding="utf-8",
    )
    return path


def test_roman_csv_is_normalized_for_common_replay(roman_csv):
    importer = RomanLogImporter(roman_csv)
    rows = list(importer.rows())

    assert rows[0]["segment"] == "approach"
    assert rows[0]["groundspeed_ms"] == pytest.approx(150 * Converts.KTS_TO_MS)
    assert rows[0]["ias_ms"] == pytest.approx(140 * Converts.KTS_TO_MS)
    assert rows[0]["magnetic_track_deg"] == 74.8
    assert rows[0]["pid_roll_kp"] == -7
    assert importer.summary() == {
        "rows": 2,
        "duration_s": 0.1,
        "min_ra_ft": 990.0,
        "max_ra_ft": 1000.0,
    }


def test_manifest_reports_missing_and_changed_sources(tmp_path):
    source = tmp_path / "source"
    base = source / "logs"
    base.mkdir(parents=True)
    ok = base / "ok.csv"
    changed = base / "changed.csv"
    ok.write_bytes(b"ok")
    changed.write_bytes(b"new")
    manifest = {
        "base_path": "logs",
        "files": {
            "ok.csv": {
                "bytes": 2,
                "sha256": hashlib.sha256(b"ok").hexdigest(),
            },
            "changed.csv": {
                "bytes": 3,
                "sha256": hashlib.sha256(b"old").hexdigest(),
            },
            "missing.csv": {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()},
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_manifest(manifest_path, source)
    assert result == {
        "ok": ["ok.csv"],
        "missing": ["missing.csv"],
        "changed": ["changed.csv"],
    }
