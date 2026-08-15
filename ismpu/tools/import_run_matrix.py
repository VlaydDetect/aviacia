"""Одноразовый импорт исходной Excel-матрицы в runtime-каталог JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CATALOG_SCHEMA_VERSION = 1
WORKBOOK_VERSION = 3
SHEETS = (
    ("А_Заход_и_посадка", "approach", 156),
    ("Б_ВПП_и_руление", "ground", 124),
)
COLUMNS = (
    "№", "Шифр", "Прогон", "Отказ / режим", "Параметры отказа", "Момент ввода",
    "Условие", "Ветер: направление", "Ветер: скорость, м/с", "Порывы / сдвиг",
    "Видимость", "Состояние ВПП", "Критерии успеха", "Статус",
    "Факт. макс. отклонения", "Комментарий",
)


def _scalar(value: Any, pandas) -> Any:
    if pandas.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def import_workbook(path: str | Path) -> dict[str, Any]:
    """Прочитать книгу целиком; функция не используется production runtime."""
    import pandas as pd

    source = Path(path)
    runs: list[dict[str, Any]] = []
    sheet_meta: list[dict[str, Any]] = []
    for sheet_name, role, expected_rows in SHEETS:
        frame = pd.read_excel(source, sheet_name=sheet_name, dtype=object)
        actual_columns = tuple(str(column) for column in frame.columns)
        if actual_columns != COLUMNS:
            raise ValueError(
                f"лист {sheet_name!r}: ожидались колонки {COLUMNS!r}, получены {actual_columns!r}"
            )
        if len(frame) != expected_rows:
            raise ValueError(
                f"лист {sheet_name!r}: ожидалось {expected_rows} строк, получено {len(frame)}"
            )
        sheet_meta.append({"name": sheet_name, "role": role, "rows": len(frame)})
        for index, row in frame.iterrows():
            cells = {column: _scalar(row[column], pd) for column in COLUMNS}
            code, run_number = str(cells["Шифр"]), int(cells["Прогон"])
            runs.append({
                "matrix_run_id": f"{code}/{run_number}",
                "sheet": sheet_name,
                "sheet_role": role,
                "excel_row": int(index) + 2,
                "cells": cells,
            })

    run_ids = [run["matrix_run_id"] for run in runs]
    codes = {run["cells"]["Шифр"] for run in runs}
    if len(runs) != 280 or len(set(run_ids)) != len(run_ids) or len(codes) != 22:
        raise ValueError(
            "матрица должна содержать 280 уникальных прогонов и 22 шифра, "
            f"получено {len(runs)} прогонов и {len(codes)} шифров"
        )
    return {
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
        "workbook_version": WORKBOOK_VERSION,
        "source_filename": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "columns": list(COLUMNS),
        "sheets": sheet_meta,
        "runs": runs,
    }


def write_catalog(workbook: str | Path, output: str | Path) -> Path:
    target = Path(output)
    target.write_text(
        json.dumps(import_workbook(workbook), ensure_ascii=False, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return target


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workbook", nargs="?", default=root / "docs" / "Матрица_прогонов_ПИД_ИСМПУ.xlsx")
    parser.add_argument(
        "--output", default=root / "ismpu" / "config" / "run_matrix.v3.json")
    args = parser.parse_args(argv)
    print(write_catalog(args.workbook, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
