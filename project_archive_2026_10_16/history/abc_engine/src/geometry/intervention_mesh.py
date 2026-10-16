from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.geometry.mesh_utils import write_boxes_obj


def interventions_to_boxes(interventions: pd.DataFrame) -> list[dict]:
    """Convert intervention rows into reference boxes for OBJ export."""
    boxes: list[dict] = []
    for _, row in interventions.iterrows():
        sx = max(float(row["size_x"]), 0.2)
        sy = max(float(row["size_y"]), 0.2)
        sz = max(float(row["size_z"]), 0.2)
        x = float(row["x"])
        y = float(row["y"])
        z = float(row["z"])
        boxes.append(
            {
                "name": f"{row['candidate_id']}_{row['intervention_id']}_{row['type']}",
                "x_min": x - sx / 2,
                "x_max": x + sx / 2,
                "y_min": y - sy / 2,
                "y_max": y + sy / 2,
                "z_min": z,
                "z_max": z + sz,
            }
        )
    return boxes


def write_candidate_obj(interventions: pd.DataFrame, output_path: Path) -> Path:
    """Write candidate intervention reference boxes as OBJ."""
    boxes = interventions_to_boxes(interventions)
    return write_boxes_obj(
        boxes,
        output_path,
        "Candidate intervention boxes. Subtract boxes mark suggested void cuts.",
    )

