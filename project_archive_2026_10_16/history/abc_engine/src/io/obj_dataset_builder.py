from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, SITE_ZONE_COLUMNS, STREET_COLUMNS
from src.algorithm_c_validation.run_validation import NODE_COLUMNS
from src.io.export_results import ensure_dir, write_csv, write_json


PROTECTED_ZONE_COLUMNS = [
    "zone_id",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "reason",
    "notes",
]


@dataclass
class ObjGroup:
    """Geometry group parsed from a Wavefront OBJ file."""

    name: str
    vertex_indices: set[int]


def _safe_dataset_name(path: Path) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in path.stem)
    return safe.strip("_") or "obj_dataset"


def _parse_obj_groups(path: Path) -> tuple[list[tuple[float, float, float]], list[ObjGroup]]:
    """Parse vertices and object/group membership from a simple OBJ file."""
    vertices: list[tuple[float, float, float]] = []
    groups: list[ObjGroup] = []
    current = ObjGroup("OBJ001", set())
    groups.append(current)

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("o ", "g ")):
            name = line.split(maxsplit=1)[1].strip() if len(line.split(maxsplit=1)) > 1 else ""
            name = name or f"OBJ{len(groups) + 1:03d}"
            current = ObjGroup(name, set())
            groups.append(current)
            continue
        if line.startswith("v "):
            parts = line.split()
            if len(parts) >= 4:
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            continue
        if line.startswith("f "):
            for token in line.split()[1:]:
                head = token.split("/")[0]
                if not head:
                    continue
                index = int(head)
                if index < 0:
                    index = len(vertices) + index + 1
                current.vertex_indices.add(index - 1)

    if not vertices:
        raise ValueError(f"OBJ contains no vertices: {path}")

    # Some exporters write vertices under a group but faces after no explicit group.
    used_indices = set().union(*(group.vertex_indices for group in groups))
    if not used_indices:
        groups = [ObjGroup("OBJ001", set(range(len(vertices))))]
    else:
        groups = [group for group in groups if group.vertex_indices]
    return vertices, groups


def _group_to_building_row(
    index: int,
    group: ObjGroup,
    vertices: list[tuple[float, float, float]],
    min_height_m: float,
) -> dict | None:
    coords = [vertices[i] for i in group.vertex_indices if 0 <= i < len(vertices)]
    if not coords:
        return None
    xs = [item[0] for item in coords]
    ys = [item[1] for item in coords]
    zs = [item[2] for item in coords]
    height = max(zs) - min(zs)
    width_x = max(xs) - min(xs)
    width_y = max(ys) - min(ys)
    if height < min_height_m or width_x <= 0 or width_y <= 0:
        return None

    building_id = f"OBJ_B{index:03d}"
    return {
        "building_id": building_id,
        "name": group.name[:80],
        "x_min": round(min(xs), 3),
        "x_max": round(max(xs), 3),
        "y_min": round(min(ys), 3),
        "y_max": round(max(ys), 3),
        "height_m": round(height, 3),
        "floors": max(1, round(height / 3.0)),
        "movable": True,
        "protected": False,
        "facade_type": "auto_from_obj_group",
        "notes": "auto-generated from OBJ group/object bounding box; verify before design use",
    }


def _fallback_street(buildings: pd.DataFrame) -> pd.DataFrame:
    x_min = float(buildings["x_min"].min())
    x_max = float(buildings["x_max"].max())
    y_min = float(buildings["y_min"].min())
    y_max = float(buildings["y_max"].max())
    span_x = x_max - x_min
    span_y = y_max - y_min
    width = round(max(3.0, min(10.0, min(span_x, span_y) * 0.12)), 3)
    if span_x >= span_y:
        start_x, start_y, end_x, end_y = x_min, (y_min + y_max) / 2, x_max, (y_min + y_max) / 2
        direction = "auto-east-west"
    else:
        start_x, start_y, end_x, end_y = (x_min + x_max) / 2, y_min, (x_min + x_max) / 2, y_max
        direction = "auto-north-south"
    return pd.DataFrame(
        [
            {
                "street_id": "AUTO_STREET_001",
                "start_x": round(start_x, 3),
                "start_y": round(start_y, 3),
                "end_x": round(end_x, 3),
                "end_y": round(end_y, 3),
                "width_m": width,
                "main_direction": direction,
                "pedestrian_priority": True,
                "notes": "auto-inferred fallback street; replace with surveyed road centerline",
            }
        ],
        columns=STREET_COLUMNS,
    )


def _fallback_nodes(streets: pd.DataFrame) -> pd.DataFrame:
    street = streets.iloc[0]
    return pd.DataFrame(
        [
            {
                "node_id": "AUTO_N001",
                "x": street["start_x"],
                "y": street["start_y"],
                "z": 0.0,
                "node_type": "auto_entry",
                "importance": 4,
                "notes": "auto-generated from fallback street",
            },
            {
                "node_id": "AUTO_N002",
                "x": round((float(street["start_x"]) + float(street["end_x"])) / 2, 3),
                "y": round((float(street["start_y"]) + float(street["end_y"])) / 2, 3),
                "z": 0.0,
                "node_type": "auto_midpoint",
                "importance": 5,
                "notes": "auto-generated from fallback street",
            },
            {
                "node_id": "AUTO_N003",
                "x": street["end_x"],
                "y": street["end_y"],
                "z": 0.0,
                "node_type": "auto_entry",
                "importance": 4,
                "notes": "auto-generated from fallback street",
            },
        ],
        columns=NODE_COLUMNS,
    )


def _fallback_site_zones(buildings: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "zone_id": "AUTO_Z001",
                "name": "auto OBJ analysis zone",
                "zone_type": "auto_context",
                "x_min": round(float(buildings["x_min"].min()), 3),
                "x_max": round(float(buildings["x_max"].max()), 3),
                "y_min": round(float(buildings["y_min"].min()), 3),
                "y_max": round(float(buildings["y_max"].max()), 3),
                "priority": 3,
                "needs_light_improvement": True,
                "needs_accessibility_improvement": True,
                "protected": False,
                "notes": "auto-generated from OBJ bounds; replace with project-specific zones",
            }
        ],
        columns=SITE_ZONE_COLUMNS,
    )


def build_dataset_from_obj(
    obj_path: Path,
    output_dir: Path,
    overwrite: bool = False,
    min_height_m: float = 0.5,
) -> dict:
    """Create a runnable dataset folder from a grouped white-model OBJ.

    This is a coarse fallback for early validation. Reliable optimisation still
    requires architecture students to provide building IDs, road centerlines,
    protected zones, and accessibility data.
    """
    obj_path = Path(obj_path)
    output_dir = ensure_dir(Path(output_dir))
    if not obj_path.exists():
        raise FileNotFoundError(f"OBJ file not found: {obj_path}")
    if any(output_dir.iterdir()) and not overwrite:
        expected = output_dir / "site_model.obj"
        if expected.exists():
            return {"dataset_dir": str(output_dir), "summary": str(output_dir / "auto_obj_summary.json")}
        raise FileExistsError(f"Output dataset is not empty: {output_dir}")

    vertices, groups = _parse_obj_groups(obj_path)
    rows = []
    for group in groups:
        row = _group_to_building_row(len(rows) + 1, group, vertices, min_height_m)
        if row is not None:
            rows.append(row)
    if not rows:
        raise ValueError(
            "No building-like OBJ groups were detected. "
            "Use a grouped SketchUp white model with z-up massing volumes."
        )

    buildings = pd.DataFrame(rows, columns=BUILDING_COLUMNS)
    streets = _fallback_street(buildings)
    nodes = _fallback_nodes(streets)
    protected_zones = pd.DataFrame(columns=PROTECTED_ZONE_COLUMNS)
    site_zones = _fallback_site_zones(buildings)

    shutil.copy2(obj_path, output_dir / "site_model.obj")
    write_csv(buildings, output_dir / "buildings.csv")
    write_csv(streets, output_dir / "streets.csv")
    write_csv(nodes, output_dir / "nodes.csv")
    write_csv(protected_zones, output_dir / "protected_zones.csv")
    write_csv(site_zones, output_dir / "site_zones.csv")

    warning = "ok"
    if len(buildings) == 1:
        warning = (
            "Only one building group was detected. The pipeline can run, but "
            "building-level optimisation is not reliable until the OBJ is grouped by building."
        )
    summary = {
        "source_obj": str(obj_path),
        "dataset_dir": str(output_dir),
        "building_count": int(len(buildings)),
        "group_count": int(len(groups)),
        "street_source": "auto-inferred fallback",
        "node_source": "auto-inferred fallback",
        "protected_zone_source": "empty auto fallback",
        "warning": warning,
        "required_for_real_use": [
            "verify buildings.csv IDs and footprints",
            "replace streets.csv with surveyed road centerlines",
            "mark protected buildings/zones",
            "add real accessibility nodes/routes",
        ],
    }
    summary_path = write_json(summary, output_dir / "auto_obj_summary.json")
    return {
        "dataset_dir": str(output_dir),
        "summary": str(summary_path),
        "building_count": int(len(buildings)),
        "warning": warning,
    }


def default_auto_dataset_dir(data_dir: Path, obj_path: Path) -> Path:
    """Return the default dataset path for a standalone OBJ import."""
    return Path(data_dir) / "auto_obj" / _safe_dataset_name(Path(obj_path))
