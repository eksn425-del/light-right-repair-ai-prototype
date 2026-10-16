from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _distance_point_to_rect(x: float, y: float, row: pd.Series) -> float:
    dx = max(float(row["x_min"]) - x, 0.0, x - float(row["x_max"]))
    dy = max(float(row["y_min"]) - y, 0.0, y - float(row["y_max"]))
    return float((dx * dx + dy * dy) ** 0.5)


def build_building_variables(dataset_dir: Path, diagnosis_dir: Path, output_path: Path) -> Path:
    """Build building-level variables for light-restoration strategy analysis."""
    dataset_dir = Path(dataset_dir)
    diagnosis_dir = Path(diagnosis_dir)
    output_path = Path(output_path)

    buildings = pd.read_csv(dataset_dir / "buildings.csv")
    dark_zones = pd.read_csv(diagnosis_dir / "dark_zones.csv")

    dark_counts = (
        dark_zones.groupby("nearest_building_id")
        .size()
        .rename("nearest_dark_zone_count")
        .reset_index()
        .rename(columns={"nearest_building_id": "building_id"})
    )
    severe_counts = (
        dark_zones[dark_zones["severity"].astype(str).str.lower() == "high"]
        .groupby("nearest_building_id")
        .size()
        .rename("nearest_severe_dark_zone_count")
        .reset_index()
        .rename(columns={"nearest_building_id": "building_id"})
    )

    rows = []
    for _, row in buildings.iterrows():
        width_x = abs(float(row["x_max"]) - float(row["x_min"]))
        width_y = abs(float(row["y_max"]) - float(row["y_min"]))
        area = width_x * width_y
        height = float(row["height_m"])
        volume = area * height
        perimeter = 2 * (width_x + width_y)
        slenderness = height / max(min(width_x, width_y), 0.001)
        aspect_ratio = max(width_x, width_y) / max(min(width_x, width_y), 0.001)
        center_x = (float(row["x_min"]) + float(row["x_max"])) / 2
        center_y = (float(row["y_min"]) + float(row["y_max"])) / 2

        if dark_zones.empty:
            nearest_dark_distance = None
            nearest_dark_sunlight = None
        else:
            distances = dark_zones.apply(
                lambda dz: _distance_point_to_rect(float(dz["x"]), float(dz["y"]), row),
                axis=1,
            )
            nearest_index = distances.idxmin()
            nearest_dark_distance = round(float(distances.loc[nearest_index]), 3)
            nearest_dark_sunlight = float(dark_zones.loc[nearest_index, "sunlight_hours"])

        rows.append(
            {
                "building_id": row["building_id"],
                "height_m": height,
                "footprint_width_x_m": round(width_x, 3),
                "footprint_width_y_m": round(width_y, 3),
                "footprint_area_m2": round(area, 3),
                "volume_m3": round(volume, 3),
                "perimeter_m": round(perimeter, 3),
                "aspect_ratio_xy": round(aspect_ratio, 3),
                "height_to_min_width_ratio": round(slenderness, 3),
                "center_x": round(center_x, 3),
                "center_y": round(center_y, 3),
                "movable": row.get("movable", ""),
                "protected": row.get("protected", ""),
                "nearest_dark_zone_distance_m": nearest_dark_distance,
                "nearest_dark_zone_sunlight_hours": nearest_dark_sunlight,
            }
        )

    variables = pd.DataFrame(rows)
    variables = variables.merge(dark_counts, on="building_id", how="left")
    variables = variables.merge(severe_counts, on="building_id", how="left")
    variables[["nearest_dark_zone_count", "nearest_severe_dark_zone_count"]] = variables[
        ["nearest_dark_zone_count", "nearest_severe_dark_zone_count"]
    ].fillna(0).astype(int)
    variables["shading_priority_score"] = (
        variables["nearest_dark_zone_count"] * 1.0
        + variables["nearest_severe_dark_zone_count"] * 1.5
        + variables["height_m"] / variables["height_m"].max() * 2.0
        + variables["volume_m3"] / variables["volume_m3"].max() * 2.0
    ).round(3)
    variables = variables.sort_values(
        ["shading_priority_score", "nearest_dark_zone_count", "volume_m3"],
        ascending=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    variables.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build building-level variables for light-equity analysis.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "real_guankou" / "lakeside_leisure_ready",
    )
    parser.add_argument(
        "--diagnosis-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "validation_lakeside_6m" / "A_diagnosis",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "light_product_2026_06_02" / "building_variables.csv",
    )
    args = parser.parse_args()
    output = build_building_variables(args.dataset_dir, args.diagnosis_dir, args.output)
    print(f"Wrote building variables: {output}")


if __name__ == "__main__":
    main()
