from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class MeshData:
    """Minimal mesh container used by the simplified pipeline."""

    vertices: np.ndarray
    faces: list[tuple[int, ...]]
    bounds_min: np.ndarray
    bounds_max: np.ndarray
    source_path: Path


def _load_obj_manually(path: Path) -> MeshData:
    vertices: list[list[float]] = []
    faces: list[tuple[int, ...]] = []

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if line.startswith("v "):
            parts = line.split()
            if len(parts) >= 4:
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        elif line.startswith("f "):
            indices: list[int] = []
            for token in line.split()[1:]:
                head = token.split("/")[0]
                if head:
                    indices.append(int(head) - 1)
            if len(indices) >= 3:
                faces.append(tuple(indices))

    if not vertices:
        raise ValueError(
            f"OBJ contains no vertices: {path}. "
            "Please replace this with a SketchUp-exported white massing OBJ."
        )

    vertex_array = np.array(vertices, dtype=float)
    return MeshData(
        vertices=vertex_array,
        faces=faces,
        bounds_min=vertex_array.min(axis=0),
        bounds_max=vertex_array.max(axis=0),
        source_path=path,
    )


def load_obj_mesh(path: Path) -> MeshData:
    """Load an OBJ file.

    The project can use trimesh when available, but falls back to a tiny OBJ
    reader so the toy pipeline remains low-threshold for undergraduate teams.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"OBJ file not found: {path}. "
            "Place site_model.obj in the selected dataset folder first."
        )

    try:
        import trimesh  # type: ignore

        mesh = trimesh.load_mesh(str(path), force="mesh")
        vertices = np.asarray(mesh.vertices, dtype=float)
        if vertices.size == 0:
            raise ValueError(
                f"OBJ contains no vertices: {path}. "
                "Please export a simplified white massing model from SketchUp."
            )
        faces = [tuple(map(int, face)) for face in np.asarray(mesh.faces)]
        return MeshData(
            vertices=vertices,
            faces=faces,
            bounds_min=vertices.min(axis=0),
            bounds_max=vertices.max(axis=0),
            source_path=path,
        )
    except ModuleNotFoundError:
        return _load_obj_manually(path)

