from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.geometry.mesh_utils import buildings_to_boxes, write_boxes_obj  # noqa: E402
from src.io.export_results import ensure_dir  # noqa: E402


def export_modified_candidate_model(
    dataset_dir: Path,
    interventions_path: Path,
    candidate_id: str,
    output_dir: Path,
    max_reduction_fraction: float = 0.35,
) -> dict:
    """Export a simplified full-site OBJ with candidate height reductions applied."""
    dataset_dir = Path(dataset_dir)
    interventions_path = Path(interventions_path)
    output_dir = ensure_dir(Path(output_dir))

    buildings = pd.read_csv(dataset_dir / "buildings.csv")
    interventions = pd.read_csv(interventions_path)
    selected = interventions[interventions["candidate_id"].astype(str) == str(candidate_id)].copy()

    modified = buildings.copy()
    change_rows = []
    for building_index, building in modified.iterrows():
        building_id = str(building["building_id"])
        related = []
        for _, intervention in selected.iterrows():
            if str(intervention.get("type", "")) != "subtract":
                continue
            targets = {
                item.strip()
                for item in str(intervention.get("target_building_id", "")).split("|")
                if item.strip()
            }
            if building_id in targets:
                related.append(float(intervention.get("size_z", 0.0)))
        if not related:
            continue

        old_height = float(building["height_m"])
        reduction = min(sum(related), old_height * max_reduction_fraction)
        new_height = max(old_height - reduction, 1.0)
        modified.at[building_index, "height_m"] = round(new_height, 3)
        change_rows.append(
            {
                "candidate_id": candidate_id,
                "building_id": building_id,
                "old_height_m": old_height,
                "new_height_m": round(new_height, 3),
                "height_reduction_m": round(reduction, 3),
                "notes": "simplified full-site box model for daylight re-check; not a precise boolean SU model",
            }
        )

    obj_path = output_dir / f"{candidate_id}_modified_full_site.obj"
    write_boxes_obj(buildings_to_boxes(modified), obj_path, f"{candidate_id} simplified modified full-site model")

    csv_path = output_dir / f"{candidate_id}_height_changes.csv"
    pd.DataFrame(change_rows).to_csv(csv_path, index=False, encoding="utf-8-sig")

    return {"obj": obj_path, "height_changes": csv_path, "changed_count": len(change_rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export simplified full-site OBJ for a selected candidate.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "real_guankou" / "lakeside_leisure_ready",
    )
    parser.add_argument(
        "--interventions",
        type=Path,
        default=PROJECT_ROOT
        / "outputs"
        / "light_product_2026_06_02"
        / "strategy_comparison_postsim"
        / "conservative"
        / "B_candidates"
        / "interventions.csv",
    )
    parser.add_argument("--candidate-id", default="candidate_01")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "light_product_2026_06_02" / "recommended_conservative_model",
    )
    args = parser.parse_args()
    result = export_modified_candidate_model(
        dataset_dir=args.dataset_dir,
        interventions_path=args.interventions,
        candidate_id=args.candidate_id,
        output_dir=args.output_dir,
    )
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
