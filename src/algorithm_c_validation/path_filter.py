from __future__ import annotations

import math

import pandas as pd


def _sorted_nodes(nodes: pd.DataFrame) -> pd.DataFrame:
    return nodes.sort_values(["x", "y", "node_id"]).reset_index(drop=True)


def build_candidate_routes(
    candidate_id: str,
    nodes: pd.DataFrame,
    streets: pd.DataFrame,
    interventions: pd.DataFrame,
    rules: dict,
    estimated_light_gain: float,
) -> pd.DataFrame:
    """Build simplified route records between consecutive nodes."""
    ordered = _sorted_nodes(nodes)
    route_rows: list[dict] = []
    min_width = float(rules["min_clear_width_m"])
    base_width = float(streets["width_m"].min()) if not streets.empty else min_width
    protected_conflict = bool(interventions["protected_conflict"].astype(bool).any()) if not interventions.empty else False

    for index in range(max(len(ordered) - 1, 0)):
        start = ordered.iloc[index]
        end = ordered.iloc[index + 1]
        length = math.hypot(float(end["x"]) - float(start["x"]), float(end["y"]) - float(start["y"]))
        is_accessible = base_width >= min_width and not protected_conflict
        route_rows.append(
            {
                "route_id": f"R{index + 1:03d}",
                "candidate_id": candidate_id,
                "start_node_id": start["node_id"],
                "end_node_id": end["node_id"],
                "length_m": round(length, 3),
                "average_sunlight_hours": round(2.5 + estimated_light_gain / max(len(ordered), 1), 3),
                "is_accessible": bool(is_accessible),
                "notes": "node-to-node route placeholder based on street width and candidate conflicts",
            }
        )

    return pd.DataFrame(
        route_rows,
        columns=[
            "route_id",
            "candidate_id",
            "start_node_id",
            "end_node_id",
            "length_m",
            "average_sunlight_hours",
            "is_accessible",
            "notes",
        ],
    )

