from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from honeybee.model import Model
from honeybee_radiance.sensorgrid import Sensor, SensorGrid


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
CODE = ROOT / "code"
RESULTS = ROOT / "results_csv"
BATCH = ROOT / "hb_radiance_project_final_design"

sys.path.insert(0, str(CODE))
from route_b_prepare_hb_batch import building_shades, create_grid, load_canonical, write_wea  # noqa: E402


FINAL_PAIRS = [
    ("C9,C24", "最高低日照面积下降候选"),
    ("C9,C15", "较高收益与较低体量平衡候选"),
    ("C9,C13", "较低体量高收益候选"),
]


def scenario_name(pair: str) -> str:
    a, b = [x.strip() for x in pair.split(",")]
    return f"{a}_{b}_design_stepback"


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    buildings, geom_by_id = load_canonical()
    grid = create_grid(geom_by_id, grid_size=3.0, sensor_z=0.1)
    sensors = [Sensor(pos=(r.x, r.y, r.z), dir=(0, 0, 1)) for r in grid.itertuples(index=False)]
    sensor_grid = SensorGrid("ground_3m_road_open_space", sensors)

    scenario_rows, volume_rows, run_rows = [], [], []
    for pair, note in FINAL_PAIRS:
        scenario = {
            "scenario": scenario_name(pair),
            "pair": pair,
            "model_type": "design_stepback",
            "note": f"最终候选设计转译复核：{note}",
        }
        scen_dir = BATCH / scenario["scenario"]
        inp_dir = scen_dir / "inputs"
        inp_dir.mkdir(parents=True, exist_ok=True)
        shades, vols = building_shades(buildings, geom_by_id, scenario)
        volume_rows.extend(vols)
        model = Model(f"canonical_site_v2_{scenario['scenario']}", orphaned_shades=shades, units="Meters", tolerance=0.01)
        model.properties.radiance.add_sensor_grid(sensor_grid)
        hbjson = inp_dir / f"{scenario['scenario']}.hbjson"
        model.to_hbjson(name=hbjson.name, folder=str(hbjson.parent), indent=2)
        wea = inp_dir / "winter_solstice_30min_0815_1545.wea"
        write_wea(wea)
        input_json = inp_dir / f"{scenario['scenario']}_inputs.json"
        input_json.write_text(
            json.dumps(
                {
                    "model": str(hbjson),
                    "wea": str(wea),
                    "timestep": 2,
                    "grid-filter": "*",
                    "north": 0,
                    "min-sensor-count": 200,
                    "cpu-count": 4,
                },
                ensure_ascii=True,
                indent=2,
            ),
            encoding="ascii",
        )
        selected_vol = sum(v["removed_volume_m3"] for v in vols if v["selected"])
        scenario_rows.append(
            {
                "scenario": scenario["scenario"],
                "pair": pair,
                "model_type": "design_stepback",
                "sensor_count": len(grid),
                "date": "2026-12-21",
                "time_range": "08:15-15:45",
                "timestep_minutes": 30,
                "grid_size_m": 3.0,
                "sensor_height_m": 0.1,
                "north_deg": 0,
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

    pd.DataFrame(scenario_rows).to_csv(RESULTS / "136_HB_Radiance最终候选设计转译场景参数表.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(volume_rows).to_csv(RESULTS / "137_HB_Radiance最终候选设计转译体量结果.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(run_rows).to_csv(BATCH / "run_manifest.csv", index=False, encoding="utf-8-sig")
    (BATCH / "prepare_summary.json").write_text(
        json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"), "scenario_count": len(run_rows)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(BATCH / "run_manifest.csv")
    print(pd.DataFrame(run_rows)[["scenario"]].to_string(index=False))


if __name__ == "__main__":
    main()
