from __future__ import annotations

import json
from pathlib import Path

from ladybug.analysisperiod import AnalysisPeriod
from ladybug.datacollection import HourlyDiscontinuousCollection
from ladybug.datatype.energyflux import DiffuseHorizontalIrradiance, DirectNormalIrradiance
from ladybug.dt import DateTime
from ladybug.header import Header
from ladybug.location import Location
from ladybug.wea import Wea
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Point3D

import honeybee_radiance.properties.model  # noqa: F401
from honeybee.model import Model
from honeybee.shade import Shade
from honeybee_radiance.sensorgrid import Sensor, SensorGrid


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
PROJECT = ROOT / "hb_radiance_wall_smoke"


def write_wea(path: Path):
    location = Location("Xiamen_Guankou", "Fujian", "China", 24.55, 118.03, 8, 10)
    datetimes = [DateTime(12, 21, 8, 15), DateTime(12, 21, 12, 15)]
    ap = AnalysisPeriod(12, 21, 8, 12, 21, 12, timestep=2)
    dni = HourlyDiscontinuousCollection(Header(DirectNormalIrradiance(), "W/m2", ap), [1000, 1000], datetimes)
    dhi = HourlyDiscontinuousCollection(Header(DiffuseHorizontalIrradiance(), "W/m2", ap), [0, 0], datetimes)
    Wea(location, dni, dhi).write(str(path), write_hours=True)


def main():
    (PROJECT / "inputs").mkdir(parents=True, exist_ok=True)
    # Wall lies on y=0. The 08:15 sun vector has negative Y, so a sensor at y=5
    # should look through the wall toward the sun, while y=-5 should be open.
    wall = Shade(
        "test_wall_y0",
        Face3D(
            [
                Point3D(-10, 0, 0),
                Point3D(10, 0, 0),
                Point3D(10, 0, 10),
                Point3D(-10, 0, 10),
            ]
        ),
        is_detached=True,
    )
    sensors = [
        Sensor(pos=(0, 5, 0.1), dir=(0, 0, 1)),
        Sensor(pos=(0, -5, 0.1), dir=(0, 0, 1)),
    ]
    model = Model("wall_smoke", orphaned_shades=[wall], units="Meters")
    model.properties.radiance.add_sensor_grid(SensorGrid("two_points", sensors))
    hbjson = PROJECT / "inputs" / "wall_smoke.hbjson"
    model.to_hbjson(name=hbjson.name, folder=str(hbjson.parent), indent=2)
    wea = PROJECT / "inputs" / "wall_smoke.wea"
    write_wea(wea)
    inp = {
        "model": str(hbjson),
        "wea": str(wea),
        "timestep": 2,
        "north": 0,
        "grid-filter": "*",
        "min-sensor-count": 1,
        "cpu-count": 1,
    }
    p = PROJECT / "inputs" / "wall_smoke_inputs.json"
    p.write_text(json.dumps(inp, ensure_ascii=True, indent=2), encoding="ascii")
    print(p)


if __name__ == "__main__":
    main()
