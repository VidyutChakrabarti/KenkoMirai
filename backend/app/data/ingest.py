from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = Path(__file__).with_name("config.yaml")


class DatasetValidationError(ValueError):
    pass


def resolve_path(config_path: Path, configured_path: str, *, environment_name: str | None = None) -> Path:
    override = os.getenv(environment_name) if environment_name else None
    if override:
        candidate = Path(override).expanduser().resolve()
    else:
        candidate = (config_path.parent / configured_path).resolve()
    if not candidate.is_file():
        raise FileNotFoundError(f"configured dataset does not exist: {candidate}")
    return candidate


def load_config(config_path: str | Path = DEFAULT_CONFIG) -> tuple[Path, dict[str, Any]]:
    config_file = Path(config_path).resolve()
    if not config_file.is_file():
        raise FileNotFoundError(f"data config does not exist: {config_file}")
    with config_file.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    if not isinstance(config, dict):
        raise DatasetValidationError("data config must be a mapping")
    return config_file, config


def ingest_data(config_path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_file, config = load_config(config_path)
    configured_path = config.get("mobility_csv")
    required_columns = config.get("required_columns")
    if not isinstance(configured_path, str) or not configured_path.strip():
        raise DatasetValidationError("mobility_csv must be configured")
    if not isinstance(required_columns, list) or not all(isinstance(value, str) for value in required_columns):
        raise DatasetValidationError("required_columns must be a list of strings")
    if not required_columns or len(set(required_columns)) != len(required_columns):
        raise DatasetValidationError("required_columns must be non-empty and unique")

    dataset = resolve_path(config_file, configured_path, environment_name="KENKOMIRAI_MOBILITY_CSV")
    records: list[dict[str, str]] = []
    with dataset.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        available = set(reader.fieldnames or ())
        missing = set(required_columns) - available
        if missing:
            raise DatasetValidationError(f"mobility dataset is missing columns: {sorted(missing)}")
        for row in reader:
            records.append({column: (row.get(column) or "").strip() for column in required_columns})
    if not records:
        raise DatasetValidationError("mobility dataset contains no records")
    return {
        "source": str(dataset),
        "record_count": len(records),
        "columns": required_columns,
        "records": records,
    }
