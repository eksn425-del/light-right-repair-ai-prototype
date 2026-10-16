from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


LEVEL_TO_OPERATIONS = {
    0: "none",
    1: "facade_update;function_activation_only",
    2: "ground_floor_opening;gray_space_reorganize;small_addition",
    3: "subtract;step_back;light_well;partial_opening",
    4: "key_renewal;function_replacement;mass_reorganization;public_space_insertion",
}


def _read_status_table(path: Path) -> pd.DataFrame:
    """Read the team-submitted modifiable-status table from CSV or XLSX."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Status table not found: {path}")
    if path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def _parse_level(status: str, value) -> int | None:
    if pd.notna(value) and str(value).strip() != "":
        return int(float(value))
    status_text = str(status).strip().lower()
    if status_text in {"不可干预", "不可改", "不能改", "no", "false", "0"}:
        return 0
    if status_text in {"可干预", "可改", "能改", "yes", "true", "1"}:
        return 3
    return None


def convert_modifiable_status(
    dataset_dir: Path,
    status_table_path: Path,
    output_path: Path | None = None,
) -> Path:
    """Convert a simple可改/不可改 list into the full intervention-level table."""
    dataset_dir = Path(dataset_dir)
    output_path = output_path or dataset_dir / "intervention_levels_checked.csv"
    buildings = pd.read_csv(dataset_dir / "buildings.csv")
    status = _read_status_table(status_table_path).copy()

    required = {"building_id", "intervention_status", "reason"}
    missing = sorted(required - set(status.columns))
    if missing:
        raise ValueError(f"{status_table_path} is missing required columns: {missing}")

    if "intervention_level" not in status.columns:
        status["intervention_level"] = ""
    if "checker" not in status.columns:
        status["checker"] = ""
    if "notes" not in status.columns:
        status["notes"] = ""

    status["building_id"] = status["building_id"].astype(str)
    status_by_id = status.set_index("building_id", drop=False)

    rows = []
    for _, building in buildings.iterrows():
        building_id = str(building["building_id"])
        submitted = status_by_id.loc[building_id] if building_id in status_by_id.index else {}
        status_text = str(submitted.get("intervention_status", "")).strip() if len(submitted) else ""
        reason = str(submitted.get("reason", "")).strip() if len(submitted) else ""
        level = _parse_level(status_text, submitted.get("intervention_level", "") if len(submitted) else "")
        operations = LEVEL_TO_OPERATIONS.get(level, "")
        public_service = "yes" if "幼儿园" in reason or "公共服务" in reason else "unknown"
        protected = bool(building.get("protected", False))
        if level == 0:
            protected = True

        rows.append(
            {
                "building_id": building_id,
                "name": building.get("name", ""),
                "height_m": building.get("height_m", ""),
                "current_function": "幼儿园" if "幼儿园" in reason else "",
                "heritage_value": "unknown",
                "public_service": public_service,
                "vacancy_or_low_efficiency": "unknown",
                "structure_or_property_risk": "unknown",
                "intervention_level": "" if level is None else level,
                "allowed_operations": operations,
                "intervention_reason": reason,
                "confidence": "confirmed_by_team" if status_text else "to_check",
                "field_checker": submitted.get("checker", "") if len(submitted) else "",
                "notes": submitted.get("notes", "") if len(submitted) else "",
            }
        )

    result = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert team可改/不可改 list to intervention_levels_checked.csv.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "real_guankou" / "lakeside_leisure_ready",
    )
    parser.add_argument("--status-table", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = convert_modifiable_status(args.dataset_dir, args.status_table, args.output)
    print(f"Wrote intervention-level table: {output}")


if __name__ == "__main__":
    main()
