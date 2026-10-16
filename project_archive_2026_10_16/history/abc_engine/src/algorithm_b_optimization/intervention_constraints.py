from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.load_tables import read_table, to_bool


INTERVENTION_LEVEL_COLUMNS = [
    "building_id",
    "name",
    "height_m",
    "current_function",
    "heritage_value",
    "public_service",
    "vacancy_or_low_efficiency",
    "structure_or_property_risk",
    "intervention_level",
    "allowed_operations",
    "intervention_reason",
    "confidence",
    "field_checker",
    "notes",
]


def find_intervention_level_table(dataset_dir: Path, site_config: dict) -> Path | None:
    """Return the human-checked intervention table when available.

    The draft template is intentionally ignored unless explicitly enabled in
    config, because blank/to-check rows should not silently block all candidates.
    """
    dataset_dir = Path(dataset_dir)
    checked = dataset_dir / "intervention_levels_checked.csv"
    if checked.exists():
        return checked

    draft = dataset_dir / "intervention_levels_template.csv"
    if draft.exists() and to_bool(site_config.get("use_draft_intervention_levels", False)):
        return draft
    return None


def _parse_level(value) -> int | None:
    if pd.isna(value) or str(value).strip() == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _operation_set(value) -> set[str]:
    if pd.isna(value):
        return set()
    return {
        item.strip().lower()
        for item in str(value).replace(",", ";").split(";")
        if item.strip()
    }


def apply_intervention_levels_to_buildings(
    buildings: pd.DataFrame, intervention_levels: pd.DataFrame
) -> pd.DataFrame:
    """Merge human intervention levels into buildings and update editability."""
    if intervention_levels.empty:
        return buildings

    result = buildings.copy()
    levels = intervention_levels.copy()
    levels["building_id"] = levels["building_id"].astype(str)
    keep_columns = [
        "building_id",
        "current_function",
        "heritage_value",
        "public_service",
        "vacancy_or_low_efficiency",
        "structure_or_property_risk",
        "intervention_level",
        "allowed_operations",
        "intervention_reason",
        "confidence",
    ]
    levels = levels[[column for column in keep_columns if column in levels.columns]]
    result = result.merge(levels, on="building_id", how="left", suffixes=("", "_constraint"))

    parsed_levels = result["intervention_level"].map(_parse_level)
    level_0 = parsed_levels == 0
    level_1 = parsed_levels == 1
    if "movable" in result.columns:
        result.loc[level_0 | level_1, "movable"] = False
    if "protected" in result.columns:
        result.loc[level_0, "protected"] = True

    return result


def _target_ids(target_value: str) -> list[str]:
    ids = []
    for raw_item in str(target_value).split("|"):
        item = raw_item.strip()
        if not item or item.startswith("zone:"):
            continue
        ids.append(item)
    return ids


def _allows_intervention(row: pd.Series, intervention_type: str) -> bool:
    level = _parse_level(row.get("intervention_level"))
    operations = _operation_set(row.get("allowed_operations"))

    if level is None and not operations:
        return True
    if level == 0:
        return False
    if level == 1:
        return False

    if intervention_type == "subtract":
        return level is not None and level >= 3 or bool(
            operations
            & {
                "subtract",
                "step_back",
                "light_well",
                "partial_opening",
                "mass_reorganization",
            }
        )
    if intervention_type == "reorganize":
        return level is not None and level >= 2 or bool(
            operations
            & {
                "reorganize",
                "ground_floor_opening",
                "gray_space_reorganize",
                "mass_reorganization",
                "key_renewal",
                "public_space_insertion",
            }
        )
    if intervention_type == "add":
        return level is not None and level >= 2 or bool(
            operations
            & {
                "add",
                "small_addition",
                "public_space_insertion",
                "key_renewal",
            }
        )
    return True


def filter_intervention_pool_by_constraints(
    pool: pd.DataFrame, buildings: pd.DataFrame, intervention_levels: pd.DataFrame
) -> tuple[pd.DataFrame, dict]:
    """Filter candidate operations using human intervention levels."""
    if intervention_levels.empty or pool.empty:
        return pool, {"enabled": False, "filtered_count": 0, "remaining_count": int(len(pool))}

    buildings_by_id = buildings.set_index(buildings["building_id"].astype(str), drop=False)
    keep_mask: list[bool] = []
    blocked_rows: list[dict] = []

    for _, intervention in pool.iterrows():
        target_ids = _target_ids(str(intervention.get("target_building_id", "")))
        if not target_ids:
            keep_mask.append(True)
            continue

        matched = [buildings_by_id.loc[target_id] for target_id in target_ids if target_id in buildings_by_id.index]
        if not matched:
            keep_mask.append(True)
            continue

        allowed = any(_allows_intervention(row, str(intervention.get("type", ""))) for row in matched)
        keep_mask.append(allowed)
        if not allowed:
            blocked_rows.append(
                {
                    "intervention_id": intervention.get("intervention_id", ""),
                    "type": intervention.get("type", ""),
                    "target_building_id": intervention.get("target_building_id", ""),
                }
            )

    filtered = pool.loc[keep_mask].reset_index(drop=True)
    if filtered.empty:
        raise ValueError(
            "Intervention constraints filtered out every Algorithm B operation. "
            "Check intervention_levels_checked.csv for overly strict or blank levels."
        )

    summary = {
        "enabled": True,
        "input_count": int(len(pool)),
        "filtered_count": int(len(pool) - len(filtered)),
        "remaining_count": int(len(filtered)),
        "blocked_examples": blocked_rows[:10],
    }
    return filtered, summary


def load_intervention_levels(dataset_dir: Path, site_config: dict) -> tuple[pd.DataFrame, Path | None]:
    """Load the active intervention-level table, if the dataset provides one."""
    path = find_intervention_level_table(dataset_dir, site_config)
    if path is None:
        return pd.DataFrame(columns=INTERVENTION_LEVEL_COLUMNS), None
    return read_table(path, INTERVENTION_LEVEL_COLUMNS), path
