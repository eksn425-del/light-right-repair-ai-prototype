from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.geometry.mesh_utils import buildings_to_boxes, write_boxes_obj
from src.io.export_results import ensure_dir


def _building_rows() -> list[dict]:
    heights = [9, 12, 15, 6, 12, 9]
    widths = [12, 14, 11, 15, 13, 12]
    gaps = [3, 2, 4, 3, 2]

    rows: list[dict] = []
    x = 6.0
    for index, width in enumerate(widths):
        building_id = f"B{index + 1:02d}"
        protected = building_id in {"B03"}
        movable = building_id in {"B02", "B04", "B06"} and not protected
        height = heights[index]
        rows.append(
            {
                "building_id": building_id,
                "name": f"north_block_{index + 1}",
                "x_min": x,
                "x_max": x + width,
                "y_min": 6.0,
                "y_max": 23.0,
                "height_m": height,
                "floors": round(height / 3),
                "movable": movable,
                "protected": protected,
                "facade_type": "mixed_old_shopfront",
                "notes": "toy north-side massing",
            }
        )
        x += width + (gaps[index] if index < len(gaps) else 0)

    heights_south = [6, 9, 12, 15, 9, 12]
    widths_south = [13, 10, 16, 12, 15, 10]
    gaps_south = [2, 4, 2, 3, 4]
    x = 4.0
    for index, width in enumerate(widths_south):
        building_id = f"B{index + 7:02d}"
        protected = building_id in {"B09"}
        movable = building_id in {"B08", "B10", "B12"} and not protected
        height = heights_south[index]
        rows.append(
            {
                "building_id": building_id,
                "name": f"south_block_{index + 1}",
                "x_min": x,
                "x_max": x + width,
                "y_min": -24.0,
                "y_max": -6.0,
                "height_m": height,
                "floors": round(height / 3),
                "movable": movable,
                "protected": protected,
                "facade_type": "mixed_old_residential",
                "notes": "toy south-side massing",
            }
        )
        x += width + (gaps_south[index] if index < len(gaps_south) else 0)

    return rows


def generate_toy_street(dataset_dir: Path, overwrite: bool = False) -> dict[str, Path]:
    """Generate a small old-street dataset used to test the full pipeline.

    The toy model is intentionally simple: one east-west street, two rows of
    box buildings, several editable blocks, and several protected blocks.
    """
    dataset_dir = ensure_dir(Path(dataset_dir))
    expected = {
        "site_model": dataset_dir / "site_model.obj",
        "buildings": dataset_dir / "buildings.csv",
        "streets": dataset_dir / "streets.csv",
        "nodes": dataset_dir / "nodes.csv",
        "protected_zones": dataset_dir / "protected_zones.csv",
        "site_zones": dataset_dir / "site_zones.csv",
    }
    if not overwrite and all(path.exists() for path in expected.values()):
        return expected

    buildings = pd.DataFrame(_building_rows())
    streets = pd.DataFrame(
        [
            {
                "street_id": "S01",
                "start_x": 0.0,
                "start_y": 0.0,
                "end_x": 98.0,
                "end_y": 0.0,
                "width_m": 10.0,
                "main_direction": "east-west",
                "pedestrian_priority": True,
                "notes": "toy main old street, width about 10m",
            }
        ]
    )
    nodes = pd.DataFrame(
        [
            {
                "node_id": "N01",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "node_type": "east_entrance",
                "importance": 5,
                "notes": "street entrance",
            },
            {
                "node_id": "N02",
                "x": 24.0,
                "y": 0.0,
                "z": 0.0,
                "node_type": "small_shop_cluster",
                "importance": 4,
                "notes": "active storefront segment",
            },
            {
                "node_id": "N03",
                "x": 48.0,
                "y": 0.0,
                "z": 0.0,
                "node_type": "narrow_shadow_segment",
                "importance": 5,
                "notes": "expected darker street segment",
            },
            {
                "node_id": "N04",
                "x": 72.0,
                "y": 0.0,
                "z": 0.0,
                "node_type": "community_pause_point",
                "importance": 3,
                "notes": "possible gray-space node",
            },
            {
                "node_id": "N05",
                "x": 98.0,
                "y": 0.0,
                "z": 0.0,
                "node_type": "west_entrance",
                "importance": 5,
                "notes": "street entrance",
            },
        ]
    )

    protected_rows = []
    for _, row in buildings[buildings["protected"]].iterrows():
        protected_rows.append(
            {
                "zone_id": f"PZ_{row['building_id']}",
                "x_min": row["x_min"],
                "x_max": row["x_max"],
                "y_min": row["y_min"],
                "y_max": row["y_max"],
                "z_min": 0.0,
                "z_max": row["height_m"],
                "reason": "toy protected historical facade",
                "notes": "do not cut or occupy in candidate generation",
            }
        )
    protected_zones = pd.DataFrame(protected_rows)
    site_zones = pd.DataFrame(
        [
            {
                "zone_id": "Z01",
                "name": "toy_main_street_corridor",
                "zone_type": "street_corridor",
                "x_min": 0.0,
                "x_max": 98.0,
                "y_min": -5.0,
                "y_max": 5.0,
                "priority": 5,
                "needs_light_improvement": True,
                "needs_accessibility_improvement": True,
                "protected": False,
                "notes": "legacy linear-street test area",
            },
            {
                "zone_id": "Z02",
                "name": "toy_pocket_activity_node",
                "zone_type": "community_node",
                "x_min": 40.0,
                "x_max": 58.0,
                "y_min": -5.0,
                "y_max": 5.0,
                "priority": 4,
                "needs_light_improvement": True,
                "needs_accessibility_improvement": True,
                "protected": False,
                "notes": "placeholder for pocket public-space diagnosis",
            },
        ]
    )

    buildings.to_csv(expected["buildings"], index=False, encoding="utf-8")
    streets.to_csv(expected["streets"], index=False, encoding="utf-8")
    nodes.to_csv(expected["nodes"], index=False, encoding="utf-8")
    protected_zones.to_csv(expected["protected_zones"], index=False, encoding="utf-8")
    site_zones.to_csv(expected["site_zones"], index=False, encoding="utf-8")
    write_boxes_obj(
        buildings_to_boxes(buildings),
        expected["site_model"],
        "Toy street white massing model generated from buildings.csv",
    )
    return expected
