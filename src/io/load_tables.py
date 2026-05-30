from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def _parse_scalar(value: str):
    """Parse a small YAML-like scalar used by the fallback config reader."""
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none"}:
        return None

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def read_config(path: Path) -> dict:
    """Read a YAML config file.

    PyYAML is preferred when installed. A tiny flat-key fallback keeps the
    demo runnable on machines that have not installed requirements yet.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        import yaml  # type: ignore

        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Config must be a mapping: {path}")
        return data
    except ModuleNotFoundError:
        data: dict = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = _parse_scalar(value)
        return data


def read_table(path: Path, required_columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Read a CSV table and validate the required schema."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required CSV file not found: {path}")

    df = pd.read_csv(path)
    if required_columns:
        missing = [column for column in required_columns if column not in df.columns]
        if missing:
            raise ValueError(f"{path} is missing required columns: {missing}")
    return df


def to_bool(value) -> bool:
    """Convert common CSV truthy/falsy values to bool."""
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y", "是"}


def normalise_bool_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Return a copy with selected columns converted to boolean values."""
    result = df.copy()
    for column in columns:
        if column in result.columns:
            result[column] = result[column].map(to_bool)
    return result

