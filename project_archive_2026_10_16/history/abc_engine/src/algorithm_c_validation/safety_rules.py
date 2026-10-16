from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.load_tables import read_config


def load_accessibility_rules(path: Path) -> dict:
    """Load safety/accessibility thresholds from YAML."""
    rules = read_config(path)
    defaults = {
        "max_slope_percent": 8.0,
        "min_clear_width_m": 1.2,
        "max_step_height_m": 0.16,
        "guardrail_required_height_m": 1.0,
        "min_accessibility_coverage": 0.8,
    }
    return {**defaults, **rules}


def evaluate_safety_violations(interventions: pd.DataFrame, rules: dict) -> dict:
    """Count simplified safety rule violations for one candidate."""
    if interventions.empty:
        return {
            "slope_violation_count": 0,
            "width_violation_count": 0,
            "step_violation_count": 0,
            "guardrail_violation_count": 0,
            "risk_flags": [],
        }

    max_slope = float(rules["max_slope_percent"])
    min_width = float(rules["min_clear_width_m"])
    max_step = float(rules["max_step_height_m"])
    guardrail_height = float(rules["guardrail_required_height_m"])

    slope_violations = 0
    width_violations = 0
    step_violations = 0
    guardrail_violations = 0
    risk_flags: list[str] = []

    for _, item in interventions.iterrows():
        item_type = str(item["type"])
        size_x = float(item["size_x"])
        size_y = float(item["size_y"])
        size_z = float(item["size_z"])
        z = float(item["z"])

        if item_type == "reorganize" and min(size_x, size_y) < min_width:
            width_violations += 1
            risk_flags.append("clear_width_too_small")

        if item_type == "reorganize" and size_x > 0:
            implied_slope = size_z / size_x * 100 if "ramp" in str(item.get("notes", "")).lower() else 0
            if implied_slope > max_slope:
                slope_violations += 1
                risk_flags.append("slope_too_steep")

        if item_type == "reorganize" and z > max_step:
            step_violations += 1
            risk_flags.append("step_height_too_large")

        if item_type == "add" and size_z >= guardrail_height:
            risk_flags.append("guardrail_detail_required")
            if min(size_x, size_y) < min_width:
                guardrail_violations += 1

        if bool(item.get("protected_conflict", False)):
            risk_flags.append("protected_zone_conflict")

    return {
        "slope_violation_count": int(slope_violations),
        "width_violation_count": int(width_violations),
        "step_violation_count": int(step_violations),
        "guardrail_violation_count": int(guardrail_violations),
        "risk_flags": sorted(set(risk_flags)),
    }

