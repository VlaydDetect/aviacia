"""Версионированный каталог 280 прогонов исходной Excel-матрицы.

Production runtime читает только :mod:`json`-каталог рядом с этим модулем. Повторный импорт
Excel выполняется явно через ``python -m ismpu.tools.import_run_matrix``.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ismpu.config.runway_profiles import UUEE_06R
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.envs.weather import FrictionProfile, RunwayCondition, WeatherState
from ismpu.utils.converts import Converts


CATALOG_PATH = Path(__file__).with_name("run_matrix.v3.json")
_CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
CATALOG_SHA256 = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()
CATALOG_SCHEMA_VERSION = int(_CATALOG["catalog_schema_version"])
WORKBOOK_VERSION = int(_CATALOG["workbook_version"])
SOURCE_FILENAME = str(_CATALOG["source_filename"])
SOURCE_SHA256 = str(_CATALOG["source_sha256"])
COLUMNS = tuple(str(column) for column in _CATALOG["columns"])
OPERATOR_COLUMNS = COLUMNS[:13]
RESULT_COLUMNS = COLUMNS[13:]


_PRESET_BY_CODE = {
    "А.1.1": "a_1_1_track",
    "А.1.2": "a_1_2_flare",
    "А.2.1": "a_2_1_gear_left_up",
    "А.2.2": "a_2_2_gear_nose_up",
    "А.2.3": "a_2_3_gear_partial",
    "А.3.1": "a_3_1_stab_nose_down_high",
    "А.3.2": "a_3_2_stab_nose_up_high",
    "А.3.3": "a_3_3_stab_nose_down_low",
    "А.3.4": "a_3_4_stab_nose_up_low",
    "А.4.1": "a_4_1_engine_out_high",
    "А.4.2": "a_4_2_engine_partial",
    "А.4.3": "a_4_3_engine_out_low",
    "Б.1.1": "b_1_1_rollout",
    "Б.1.2": "b_1_2_taxi",
    "Б.2.1": "b_2_1_nws_stuck_neutral",
    "Б.2.2": "b_2_2_nws_stuck_offset",
    "Б.2.3": "b_2_3_nws_limited",
    "Б.3.1": "b_3_1_reverse_left_fail",
    "Б.3.2": "b_3_2_reverse_asymmetric",
    "Б.3.3": "b_3_3_residual_thrust",
    "Б.4.1": "b_4_1_through",
    "Б.4.2": "b_4_2_through_engine_out",
}

_BENCH_FAULTS = {
    "А.2.1": (FailureMode.GEAR_CONFIG,),
    "А.2.2": (FailureMode.GEAR_CONFIG,),
    "А.2.3": (FailureMode.GEAR_CONFIG,),
    "А.4.1": (FailureMode.ENGINE_OUT_LEFT,),
    "А.4.2": (FailureMode.THRUST_LEFT_DEGRADED,),
    "А.4.3": (FailureMode.ENGINE_OUT_LEFT,),
    "Б.2.1": (FailureMode.NWS_FAIL,),
    "Б.2.2": (FailureMode.NWS_FAIL,),
    "Б.2.3": (FailureMode.NWS_FAIL,),
    "Б.3.1": (FailureMode.REVERSE_LEFT_FAIL,),
    "Б.3.2": (FailureMode.REVERSE_LEFT_FAIL,),
    "Б.3.3": (FailureMode.THRUST_LEFT_DEGRADED,),
    "Б.4.2": (FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL),
}

_AMBIGUOUS = {
    "А.2.1": ("А.2.2", "А.2.3"),
    "А.2.2": ("А.2.1", "А.2.3"),
    "А.2.3": ("А.2.1", "А.2.2"),
    "А.3.1": ("А.3.2", "А.3.3", "А.3.4"),
    "А.3.2": ("А.3.1", "А.3.3", "А.3.4"),
    "А.3.3": ("А.3.1", "А.3.2", "А.3.4"),
    "А.3.4": ("А.3.1", "А.3.2", "А.3.3"),
    "А.4.1": ("А.4.3",),
    "А.4.3": ("А.4.1",),
    "Б.2.1": ("Б.2.2", "Б.2.3"),
    "Б.2.2": ("Б.2.1", "Б.2.3"),
    "Б.2.3": ("Б.2.1", "Б.2.2"),
    "Б.3.1": ("Б.3.2",),
    "Б.3.2": ("Б.3.1",),
}

# Сквозные строки используют собственные условия, но заранее определённые пары законов.
THROUGH_PROFILE_CODES = {
    "Б.4.1": {
        FlightSegment.APPROACH: "А.1.2",
        FlightSegment.ROLLOUT: "Б.1.1",
    },
    "Б.4.2": {
        FlightSegment.APPROACH: "А.4.1",
        FlightSegment.ROLLOUT: "Б.3.1",
    },
}


def normalize_code(value: str) -> str:
    return value.strip().upper().replace("A", "А").replace("B", "Б")


def _segment_for_code(code: str) -> str:
    if code.startswith("А."):
        return "approach"
    if code == "Б.1.2":
        return "taxi"
    if code.startswith("Б.4."):
        return "through"
    return "rollout"


def _number(text: Any) -> float:
    match = re.search(r"\d+(?:[,.]\d+)?", str(text))
    return float(match.group().replace(",", ".")) if match else 0.0


def _weather(cells: Mapping[str, Any]) -> tuple[WeatherState, str]:
    condition = str(cells["Условие"])
    direction = str(cells["Ветер: направление"])
    disturbances = str(cells["Порывы / сдвиг"])
    runway = str(cells["Состояние ВПП"])
    speed_kts = _number(cells["Ветер: скорость, м/с"]) * Converts.MS_TO_KTS
    crosswind = -speed_kts if "слева" in direction else speed_kts if "справа" in direction else 0.0
    headwind = speed_kts if "встречн" in direction else -speed_kts if "попутн" in direction else 0.0

    friction = RunwayCondition.DRY.value
    rain = 0.0
    friction_profile = None
    if "по третям" in runway:
        friction = RunwayCondition.WET.value
        friction_profile = FrictionProfile((
            (0.0, RunwayCondition.DRY.value),
            (UUEE_06R.length_m / 3.0, RunwayCondition.WET.value),
            (2.0 * UUEE_06R.length_m / 3.0, RunwayCondition.PUDDLY.value),
        ))
    elif "слой воды" in runway:
        friction, rain = RunwayCondition.PUDDLY.value, 1.0
    elif "мокрая" in runway:
        friction, rain = RunwayCondition.WET.value, 0.5

    gust_kts = 0.0
    turbulence = 0.0
    variability = 0.0
    if "порыв" in disturbances:
        after_to = disturbances.split("до", 1)[-1]
        gust_kts = _number(after_to) * Converts.MS_TO_KTS
        turbulence, variability = 0.5, 0.5
    elif "сдвиг" in condition:
        gust_kts, variability = speed_kts, 1.0

    visibility = 300.0 if "300" in str(cells["Видимость"]) else 5000.0
    weather = WeatherState.from_crosswind(
        crosswind,
        headwind,
        gust_kts=gust_kts,
        turbulence=turbulence,
        variability_pct=variability,
        runway_friction=friction,
        friction_profile=friction_profile,
        rain_pct=rain,
        visibility_m=visibility,
    )
    note = disturbances if disturbances not in ("нет", "None") else ""
    return weather, note


@dataclass(frozen=True)
class MatrixCondition:
    """Условия одной конкретной строки каталога."""

    matrix_run_id: str
    code: str
    title: str
    weather: WeatherState
    note: str = ""


@dataclass(frozen=True)
class MatrixRun:
    """Одна из 280 строк: задание оператору и критерии конкретного прогона."""

    matrix_run_id: str
    sheet: str
    sheet_role: str
    excel_row: int
    cells: Mapping[str, Any]

    @property
    def code(self) -> str:
        return str(self.cells["Шифр"])

    @property
    def run_number(self) -> int:
        return int(self.cells["Прогон"])

    @property
    def sequence(self) -> int:
        return int(self.cells["№"])

    @property
    def preset(self) -> str:
        return _PRESET_BY_CODE[self.code]

    @property
    def segment(self) -> str:
        return _segment_for_code(self.code)

    @property
    def title(self) -> str:
        return str(self.cells["Отказ / режим"])

    @property
    def failure(self) -> str:
        return str(self.cells["Параметры отказа"])

    @property
    def injection(self) -> str:
        return str(self.cells["Момент ввода"])

    @property
    def criteria(self) -> str:
        return str(self.cells["Критерии успеха"])

    @property
    def operator_setup(self) -> dict[str, Any]:
        return {column: self.cells[column] for column in OPERATOR_COLUMNS}

    @property
    def result_template(self) -> dict[str, Any]:
        return {column: self.cells[column] for column in RESULT_COLUMNS}

    @property
    def bench_faults(self) -> tuple[FailureMode, ...]:
        return _BENCH_FAULTS.get(self.code, ())

    @property
    def ambiguous_with(self) -> tuple[str, ...]:
        return _AMBIGUOUS.get(self.code, ())

    @property
    def condition(self) -> MatrixCondition:
        weather, note = _weather(self.cells)
        raw = str(self.cells["Условие"])
        return MatrixCondition(self.matrix_run_id, raw, raw, weather, note)

    def failures_for(self, segment: FlightSegment) -> frozenset[FailureMode]:
        if self.code == "Б.4.2" and segment is FlightSegment.APPROACH:
            return frozenset({FailureMode.ENGINE_OUT_LEFT})
        return frozenset(self.bench_faults)


MATRIX_RUNS = tuple(MatrixRun(
    matrix_run_id=str(raw["matrix_run_id"]),
    sheet=str(raw["sheet"]),
    sheet_role=str(raw["sheet_role"]),
    excel_row=int(raw["excel_row"]),
    cells=dict(raw["cells"]),
) for raw in _CATALOG["runs"])
RUN_MATRIX = MATRIX_RUNS
RUN_BY_ID = {run.matrix_run_id: run for run in MATRIX_RUNS}


@dataclass(frozen=True)
class MatrixCase:
    """Производная группировка строк одного шифра; исходные тексты живут в каталоге."""

    code: str
    rows: tuple[MatrixRun, ...]

    @property
    def preset(self) -> str:
        return _PRESET_BY_CODE[self.code]

    @property
    def segment(self) -> str:
        return self.rows[0].segment

    @property
    def title(self) -> str:
        return self.rows[0].title

    @property
    def failure(self) -> str:
        return self.rows[0].failure

    @property
    def injection(self) -> str:
        return self.rows[0].injection

    @property
    def criteria(self) -> str:
        return self.rows[0].criteria

    @property
    def conditions(self) -> tuple[MatrixCondition, ...]:
        return tuple(row.condition for row in self.rows)

    @property
    def bench_faults(self) -> tuple[FailureMode, ...]:
        return self.rows[0].bench_faults

    @property
    def ambiguous_with(self) -> tuple[str, ...]:
        return self.rows[0].ambiguous_with

    @property
    def runs(self) -> int:
        return len(self.rows)


_BY_CODE: dict[str, list[MatrixRun]] = defaultdict(list)
for _run in MATRIX_RUNS:
    _BY_CODE[_run.code].append(_run)
MATRIX_CASES = tuple(MatrixCase(code, tuple(rows)) for code, rows in _BY_CODE.items())
APPROACH_CASES = tuple(case for case in MATRIX_CASES if case.segment == "approach")
GROUND_CASES = tuple(case for case in MATRIX_CASES if case.segment != "approach")
CASE_BY_CODE = {case.code: case for case in MATRIX_CASES}
CASE_BY_PRESET = {case.preset: case for case in MATRIX_CASES}
APPROACH_CONDITIONS = APPROACH_CASES[0].conditions
GROUND_CONDITIONS = CASE_BY_CODE["Б.1.1"].conditions
TOTAL_RUNS = len(MATRIX_RUNS)

if (
    CATALOG_SCHEMA_VERSION != 1
    or len(MATRIX_RUNS) != 280
    or len(APPROACH_CASES) != 12
    or len(GROUND_CASES) != 10
    or set(_BY_CODE) != set(_PRESET_BY_CODE)
):
    raise RuntimeError("каталог матрицы повреждён или имеет неподдерживаемую версию")


def resolve_matrix_run(value: str | MatrixRun) -> MatrixRun:
    if isinstance(value, MatrixRun):
        return value
    key = value.strip()
    if key in RUN_BY_ID:
        return RUN_BY_ID[key]
    try:
        code, number = key.rsplit("/", 1)
        normalized = f"{normalize_code(code)}/{int(number)}"
    except (ValueError, TypeError) as exc:
        raise KeyError(f"run_id должен иметь вид <шифр>/<номер>, получено {value!r}") from exc
    try:
        return RUN_BY_ID[normalized]
    except KeyError as exc:
        raise KeyError(f"в матрице нет прогона {value!r}") from exc


def runs_for_code(code: str) -> tuple[MatrixRun, ...]:
    normalized = normalize_code(code)
    try:
        return tuple(_BY_CODE[normalized])
    except KeyError as exc:
        raise KeyError(f"в матрице нет шифра {code!r}") from exc


def cases_for_segment(segment: str) -> tuple[MatrixCase, ...]:
    return tuple(case for case in MATRIX_CASES if case.segment == segment)


def runs_for_segment(segment: str) -> tuple[MatrixRun, ...]:
    return tuple(run for run in MATRIX_RUNS if run.segment == segment)


def ground_cases() -> tuple[MatrixCase, ...]:
    return GROUND_CASES


def ground_runs() -> tuple[MatrixRun, ...]:
    return tuple(run for run in MATRIX_RUNS if run.segment in ("rollout", "taxi", "through"))
