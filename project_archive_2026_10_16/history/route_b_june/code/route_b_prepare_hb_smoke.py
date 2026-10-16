from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import pandas as pd
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.datacollection import HourlyDiscontinuousCollection
from ladybug.datatype.energyflux import DiffuseHorizontalIrradiance, DirectNormalIrradiance
from ladybug.dt import DateTime
from ladybug.header import Header
from ladybug.location import Location
from ladybug.wea import Wea
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Point3D
from shapely.geometry import shape
from shapely.ops import unary_union

# Register Honeybee Radiance model properties.
import honeybee_radiance.properties.model  # noqa: F401
from honeybee.model import Model
from honeybee.shade import Shade
from honeybee_radiance.sensorgrid import Sensor, SensorGrid


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
PROJECT = ROOT / "hb_radiance_project_smoke"
CANONICAL = ROOT / "canonical_site_v2"
DATASET = Path(r"E:\AI项目\谢研组\algorithm_ready_lakeside_v2")


def clean_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in value)


def load_canonical_geometries():
    buildings = pd.read_csv(CANONICAL / "canonical_buildings.csv")
    geo = json.loads((CANONICAL / "canonical_site_v2.geojson").read_text(encoding="utf-8"))
    geom_by_id = {feat["properties"]["building_id"]: shape(feat["geometry"]) for feat in geo["features"]}
    return buildings, geom_by_id


def point_segment_distance(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    if abs(dx) < 1e-12 and abs(dy) < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = min(1.0, max(0.0, t))
    cx = ax + t * dx
    cy = ay + t * dy
    return math.hypot(px - cx, py - cy)


def create_grid(buildings: pd.DataFrame, geom_by_id: dict, grid_size=3.0, sensor_z=0.1):
    streets = pd.read_csv(DATASET / "streets.csv")
    all_geom = unary_union([g for g in geom_by_id.values() if not g.is_empty])
    minx, miny, maxx, maxy = all_geom.bounds
    sx = pd.concat([streets["start_x"], streets["end_x"]]).astype(float)
    sy = pd.concat([streets["start_y"], streets["end_y"]]).astype(float)
    minx = min(minx, sx.min()) - 6.0
    maxx = max(maxx, sx.max()) + 6.0
    miny = min(miny, sy.min()) - 6.0
    maxy = max(maxy, sy.max()) + 6.0
    rows = []
    gid = 1
    x = minx
    while x <= maxx + 1e-9:
        y = miny
        while y <= maxy + 1e-9:
            p = shape({"type": "Point", "coordinates": [x, y]})
            inside_building = any(g.covers(p) for g in geom_by_id.values())
            near_street = False
            for s in streets.itertuples(index=False):
                d = point_segment_distance(x, y, float(s.start_x), float(s.start_y), float(s.end_x), float(s.end_y))
                if d <= float(s.width_m) / 2.0 + 5.0:
                    near_street = True
                    break
            if (not inside_building) and near_street:
                rows.append(
                    {
                        "grid_id": f"G{gid:05d}",
                        "x": round(x, 3),
                        "y": round(y, 3),
                        "z": sensor_z,
                        "grid_size_m": grid_size,
                        "sensor_height_m": sensor_z,
                    }
                )
                gid += 1
            y += grid_size
        x += grid_size
    return pd.DataFrame(rows)


def face_from_points(identifier: str, pts: list[tuple[float, float, float]]) -> Shade | None:
    if len(pts) < 3:
        return None
    try:
        face = Face3D([Point3D(*p) for p in pts])
        return Shade(clean_id(identifier), face, is_detached=True)
    except Exception:
        return None


def shades_for_buildings(buildings: pd.DataFrame, geom_by_id: dict, height_overrides: dict[str, float] | None = None):
    shades = []
    height_overrides = height_overrides or {}
    by_id = buildings.set_index("building_id")
    for bid, geom in geom_by_id.items():
        if bid not in by_id.index:
            continue
        height = float(height_overrides.get(bid, by_id.loc[bid, "height_m"]))
        geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        for part_i, poly in enumerate(geoms, start=1):
            coords = list(poly.exterior.coords)[:-1]
            top = [(x, y, height) for x, y in coords]
            shade = face_from_points(f"{bid}_p{part_i}_roof", top)
            if shade:
                shades.append(shade)
            for i, (x1, y1) in enumerate(coords):
                x2, y2 = coords[(i + 1) % len(coords)]
                wall = [(x1, y1, 0.0), (x2, y2, 0.0), (x2, y2, height), (x1, y1, height)]
                shade = face_from_points(f"{bid}_p{part_i}_wall{i+1}", wall)
                if shade:
                    shades.append(shade)
    return shades


def write_wea(path: Path):
    location = Location(
        city="Xiamen_Guankou",
        state="Fujian",
        country="China",
        latitude=24.55,
        longitude=118.03,
        time_zone=8,
        elevation=10,
    )
    datetimes = []
    for hour in range(8, 16):
        datetimes.append(DateTime(12, 21, hour, 15))
        datetimes.append(DateTime(12, 21, hour, 45))
    ap = AnalysisPeriod(12, 21, 8, 12, 21, 15, timestep=2)
    dni_header = Header(DirectNormalIrradiance(), "W/m2", ap)
    dhi_header = Header(DiffuseHorizontalIrradiance(), "W/m2", ap)
    dni = HourlyDiscontinuousCollection(dni_header, [1000] * len(datetimes), datetimes)
    dhi = HourlyDiscontinuousCollection(dhi_header, [0] * len(datetimes), datetimes)
    wea = Wea(location, dni, dhi)
    wea.write(str(path), write_hours=True)


def main():
    PROJECT.mkdir(parents=True, exist_ok=True)
    (PROJECT / "inputs").mkdir(exist_ok=True)
    (PROJECT / "simulation").mkdir(exist_ok=True)
    buildings, geom_by_id = load_canonical_geometries()
    grid = create_grid(buildings, geom_by_id)
    grid.to_csv(PROJECT / "inputs" / "baseline_sensor_points.csv", index=False, encoding="utf-8-sig")
    sensors = [Sensor(pos=(r.x, r.y, r.z), dir=(0, 0, 1)) for r in grid.itertuples(index=False)]
    sensor_grid = SensorGrid("ground_3m_road_open_space", sensors)
    model = Model(
        "canonical_site_v2_baseline",
        orphaned_shades=shades_for_buildings(buildings, geom_by_id),
        units="Meters",
        tolerance=0.01,
    )
    model.properties.radiance.add_sensor_grid(sensor_grid)
    hbjson = PROJECT / "inputs" / "baseline_canonical_site_v2.hbjson"
    model.to_hbjson(name=hbjson.name, folder=str(hbjson.parent), indent=2)
    wea = PROJECT / "inputs" / "winter_solstice_30min_0815_1545.wea"
    write_wea(wea)
    recipe_inputs = {
        "model": str(hbjson),
        "wea": str(wea),
        "timestep": 2,
        "north": 0,
        "grid_filter": "*",
        "min_sensor_count": 200,
        "cpu_count": 4,
        "simulation_folder": str(PROJECT / "simulation" / "baseline_direct_sun_hours"),
    }
    input_json = PROJECT / "inputs" / "baseline_direct_sun_hours_inputs.json"
    input_json.write_text(json.dumps(recipe_inputs, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "sensor_count": len(grid),
        "hbjson": str(hbjson),
        "wea": str(wea),
        "recipe_inputs": str(input_json),
    }
    (PROJECT / "inputs" / "baseline_prepare_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
