from __future__ import annotations

import json
import math
import sys
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
from shapely import affinity
from shapely.geometry import Point, shape
from shapely.ops import unary_union

import honeybee_radiance.properties.model  # noqa: F401
from honeybee.model import Model
from honeybee.shade import Shade
from honeybee_radiance.sensorgrid import Sensor, SensorGrid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
BATCH = ROOT / "hb_radiance_project_batch"
CANONICAL = ROOT / "canonical_site_v2"
DATASET = RUNTIME.source_dataset
RESULTS = RUNTIME.results_dir


SCENARIOS = [
    {"scenario": "baseline", "pair": "", "model_type": "baseline", "note": "现状规范几何"},
    {"scenario": "C6_C33_rule_flat", "pair": "C6,C33", "model_type": "rule_flat", "note": "C6/C33整体减高规则模型"},
    {"scenario": "C6_C33_design_stepback", "pair": "C6,C33", "model_type": "design_stepback", "note": "C6/C33保留底层界面的上部退台转译模型"},
    {"scenario": "C13_C24_rule_flat", "pair": "C13,C24", "model_type": "rule_flat", "note": "C13/C24整体减高规则模型"},
    {"scenario": "C13_C24_design_stepback", "pair": "C13,C24", "model_type": "design_stepback", "note": "C13/C24保留底层界面的上部退台转译模型"},
    {"scenario": "height_priority_C3_C19", "pair": "C3,C19", "model_type": "rule_flat", "note": "高度优先公平基线"},
    {"scenario": "low_sun_nearest_C26_C35", "pair": "C26,C35", "model_type": "rule_flat", "note": "低日照邻近公平基线"},
]


def clean_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in value)


def load_canonical():
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
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def create_grid(geom_by_id: dict, grid_size: float | None = None, sensor_z: float | None = None):
    """Create the fixed analysis grid using the resolved runtime settings."""

    grid_size = RUNTIME.grid_size_m if grid_size is None else float(grid_size)
    sensor_z = RUNTIME.sensor_height_m if sensor_z is None else float(sensor_z)
    streets = pd.read_csv(DATASET / "streets.csv")
    all_geom = unary_union([g for g in geom_by_id.values() if not g.is_empty])
    minx, miny, maxx, maxy = all_geom.bounds
    sx = pd.concat([streets["start_x"], streets["end_x"]]).astype(float)
    sy = pd.concat([streets["start_y"], streets["end_y"]]).astype(float)
    minx = min(minx, sx.min()) - 6.0
    maxx = max(maxx, sx.max()) + 6.0
    miny = min(miny, sy.min()) - 6.0
    maxy = max(maxy, sy.max()) + 6.0
    rows, gid = [], 1
    x = minx
    while x <= maxx + 1e-9:
        y = miny
        while y <= maxy + 1e-9:
            p = Point(x, y)
            inside = any(g.covers(p) for g in geom_by_id.values())
            near = False
            for s in streets.itertuples(index=False):
                d = point_segment_distance(x, y, float(s.start_x), float(s.start_y), float(s.end_x), float(s.end_y))
                if d <= float(s.width_m) / 2.0 + 5.0:
                    near = True
                    break
            if (not inside) and near:
                rows.append({"grid_id": f"G{gid:05d}", "x": round(x, 3), "y": round(y, 3), "z": sensor_z})
                gid += 1
            y += grid_size
        x += grid_size
    return pd.DataFrame(rows)


def reduced_height(h: float) -> float:
    """Return the shared config-driven reduced height."""

    return RUNTIME.reduced_height(h)


def face(identifier: str, pts):
    try:
        return Shade(clean_id(identifier), Face3D([Point3D(*p) for p in pts]), is_detached=True)
    except Exception:
        return None


def prism_shades(prefix: str, poly, z0: float, z1: float):
    shades = []
    if z1 <= z0 + 1e-9 or poly.is_empty:
        return shades
    coords = list(poly.exterior.coords)[:-1]
    roof = face(f"{prefix}_roof_{z1:g}", [(x, y, z1) for x, y in coords])
    if roof:
        shades.append(roof)
    for i, (x1, y1) in enumerate(coords):
        x2, y2 = coords[(i + 1) % len(coords)]
        sh = face(f"{prefix}_wall_{i+1}_{z0:g}_{z1:g}", [(x1, y1, z0), (x2, y2, z0), (x2, y2, z1), (x1, y1, z1)])
        if sh:
            shades.append(sh)
    return shades


def building_shades(buildings, geom_by_id, scenario):
    by_id = buildings.set_index("building_id")
    pair = [x for x in scenario["pair"].split(",") if x]
    selected = set(pair)
    shades = []
    volume_rows = []
    for bid, geom in geom_by_id.items():
        if bid not in by_id.index:
            continue
        h = float(by_id.loc[bid, "height_m"])
        mode = scenario["model_type"] if bid in selected else "baseline"
        geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        orig_area = sum(g.area for g in geoms)
        removed_volume = 0.0
        if mode == "rule_flat":
            h2 = reduced_height(h)
            removed_volume = orig_area * (h - h2)
            for part_i, poly in enumerate(geoms, 1):
                shades.extend(prism_shades(f"{bid}_p{part_i}_rule", poly, 0, h2))
        elif mode == "design_stepback":
            h_rule = reduced_height(h)
            base_h = min(RUNTIME.height_floor_m, h)
            removed_volume = orig_area * (h - h_rule)
            for part_i, poly in enumerate(geoms, 1):
                shades.extend(prism_shades(f"{bid}_p{part_i}_base", poly, 0, base_h))
                if h > base_h + 1e-9 and h_rule > base_h:
                    area_fraction = max(0.05, min(1.0, (h_rule - base_h) / (h - base_h)))
                    factor = math.sqrt(area_fraction)
                    c = poly.centroid
                    upper = affinity.scale(poly, xfact=factor, yfact=factor, origin=(c.x, c.y))
                    shades.extend(prism_shades(f"{bid}_p{part_i}_upper_stepback", upper, base_h, h))
        else:
            for part_i, poly in enumerate(geoms, 1):
                shades.extend(prism_shades(f"{bid}_p{part_i}_base", poly, 0, h))
        volume_rows.append(
            {
                "scenario": scenario["scenario"],
                "building_id": bid,
                "selected": bid in selected,
                "model_type": mode,
                "original_height_m": h,
                "rule_reduced_height_m": reduced_height(h) if bid in selected else h,
                "footprint_area_m2": orig_area,
                "removed_volume_m3": removed_volume,
            }
        )
    return shades, volume_rows


def write_wea(path: Path):
    """Write a direct-sun-hours WEA using the configured local period."""

    local_times = RUNTIME.analysis_datetimes()
    first, last = local_times[0], local_times[-1]
    location = Location(
        "Xiamen_Guankou",
        "Fujian",
        "China",
        RUNTIME.latitude,
        RUNTIME.longitude,
        RUNTIME.utc_offset_hours,
        10,
    )
    datetimes = [DateTime(t.month, t.day, t.hour, t.minute) for t in local_times]
    ap = AnalysisPeriod(
        first.month,
        first.day,
        first.hour,
        last.month,
        last.day,
        last.hour,
        timestep=RUNTIME.timesteps_per_hour,
    )
    dni = HourlyDiscontinuousCollection(Header(DirectNormalIrradiance(), "W/m2", ap), [1000] * len(datetimes), datetimes)
    dhi = HourlyDiscontinuousCollection(Header(DiffuseHorizontalIrradiance(), "W/m2", ap), [0] * len(datetimes), datetimes)
    Wea(location, dni, dhi).write(str(path), write_hours=True)


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    buildings, geom_by_id = load_canonical()
    grid = create_grid(geom_by_id, grid_size=RUNTIME.grid_size_m, sensor_z=RUNTIME.sensor_height_m)
    RESULTS.mkdir(exist_ok=True)
    grid.to_csv(RESULTS / "100_HB_Radiance传感点.csv", index=False, encoding="utf-8-sig")
    sensors = [Sensor(pos=(r.x, r.y, r.z), dir=(0, 0, 1)) for r in grid.itertuples(index=False)]
    grid_label = f"ground_{RUNTIME.grid_size_m:g}m_road_open_space"
    sensor_grid = SensorGrid(grid_label, sensors)

    scenario_rows, volume_rows, run_rows = [], [], []
    for scenario in SCENARIOS:
        scen_dir = BATCH / scenario["scenario"]
        inp_dir = scen_dir / "inputs"
        inp_dir.mkdir(parents=True, exist_ok=True)
        shades, vols = building_shades(buildings, geom_by_id, scenario)
        volume_rows.extend(vols)
        model = Model(f"canonical_site_v2_{scenario['scenario']}", orphaned_shades=shades, units="Meters", tolerance=0.01)
        model.properties.radiance.add_sensor_grid(sensor_grid)
        hbjson = inp_dir / f"{scenario['scenario']}.hbjson"
        model.to_hbjson(name=hbjson.name, folder=str(hbjson.parent), indent=2)
        wea = inp_dir / f"analysis_{RUNTIME.timestep_minutes}min_{RUNTIME.start_time.replace(':', '')}_{RUNTIME.end_time.replace(':', '')}.wea"
        write_wea(wea)
        recipe_inputs = {
            "model": str(hbjson),
            "wea": str(wea),
            "timestep": RUNTIME.timesteps_per_hour,
            "north": RUNTIME.north_deg,
            "grid-filter": "*",
            "min-sensor-count": 200,
            "cpu-count": RUNTIME.cpu_count,
        }
        input_json = inp_dir / f"{scenario['scenario']}_inputs.json"
        input_json.write_text(json.dumps(recipe_inputs, ensure_ascii=True, indent=2), encoding="ascii")
        selected_vol = sum(v["removed_volume_m3"] for v in vols if v["selected"])
        scenario_rows.append(
            {
                "scenario": scenario["scenario"],
                "pair": scenario["pair"],
                "model_type": scenario["model_type"],
                "sensor_count": len(grid),
                "date": RUNTIME.analysis_date,
                "time_range": f"{RUNTIME.start_time}-{RUNTIME.end_time}",
                "timestep": RUNTIME.timesteps_per_hour,
                "timezone": RUNTIME.timezone,
                "utc_offset_hours": RUNTIME.utc_offset_hours,
                "grid_size_m": RUNTIME.grid_size_m,
                "sensor_height_m": RUNTIME.sensor_height_m,
                "north_deg": RUNTIME.north_deg,
                "radiance_recipe": "lbt-recipes direct-sun-hours",
                "hbjson": str(hbjson),
                "wea": str(wea),
                "input_json": str(input_json),
                "intervention_volume_m3": selected_vol,
                "note": scenario["note"],
            }
        )
        run_rows.append(
            {
                "scenario": scenario["scenario"],
                "project_folder": str(scen_dir),
                "input_json": str(input_json),
                "debug_folder": str(scen_dir / "debug"),
            }
        )
    pd.DataFrame(scenario_rows).to_csv(RESULTS / "100_HB_Radiance场景参数表.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(volume_rows).to_csv(RESULTS / "108_统一体量结果.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(run_rows).to_csv(BATCH / "run_manifest.csv", index=False, encoding="utf-8-sig")
    (BATCH / "prepare_summary.json").write_text(json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"), "scenario_count": len(SCENARIOS), "sensor_count": len(grid)}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="prepare_hb_batch",
        inputs=[CANONICAL / "canonical_buildings.csv", CANONICAL / "canonical_site_v2.geojson", DATASET / "streets.csv"],
        extra={"scenario_count": len(SCENARIOS), "sensor_count": len(grid)},
    )
    print(BATCH / "run_manifest.csv")


if __name__ == "__main__":
    main()
