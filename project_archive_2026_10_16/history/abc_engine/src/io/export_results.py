from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def ensure_dir(path: Path) -> Path:
    """Create a directory if needed and return it."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    """Write a DataFrame as UTF-8 CSV."""
    path = Path(path)
    ensure_dir(path.parent)
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def _json_ready(value):
    """Convert numpy/pandas values into JSON-serialisable Python values."""
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value) if not isinstance(value, (dict, list, tuple)) else False:
        return None
    return value


def write_json(data: dict, path: Path) -> Path:
    """Write a dictionary as formatted UTF-8 JSON."""
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(
        json.dumps(_json_ready(data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path

