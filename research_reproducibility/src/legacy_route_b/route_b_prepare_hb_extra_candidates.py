from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from honeybee.model import Model
from honeybee_radiance.sensorgrid import Sensor, SensorGrid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
CODE = Path(__file__).resolve().parent
RESULTS = RUNTIME.results_dir
BATCH = ROOT / "hb_radiance_project_batch_extra"

sys.path.insert(0, str(CODE))
from route_b_prepare_hb_batch import building_shades, create_grid, load_canonical, write_wea  # noqa: E402


def scenario_name(pair: str) -> str:
    a, b = [x.strip() for x in pair.split(",")]
    return f"{a}_{b}_rule_flat"


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    must = pd.read_csv(RESULTS / "123_需追加HB_Radiance复核候选清单.csv")
    buildings, geom_by_id = load_canonical()
    grid = create_grid(geom_by_id, grid_size=RUNTIME.grid_size_m, sensor_z=RUNTIME.sensor_height_m)
    sensors = [Sensor(pos=(r.x, r.y, r.z), dir=(0, 0, 1)) for r in grid.itertuples(index=False)]
    grid_label = f"ground_{RUNTIME.grid_size_m:g}m_road_open_space"
    sensor_grid = SensorGrid(grid_label, sensors)

    scenario_rows, volume_rows, run_rows = [], [], []
    for row in must.itertuples(index=False):
        pair = row.building_ids
        scenario = {
            "scenario": scenario_name(pair),
            "pair": pair,
            "model_type": "rule_flat",
            "note": f"2.5D Top/Pareto 追加复核候选 {pair}",
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
        recipe_inputs = {
            "model": str(hbjson),
            "wea": str(wea),
            "timestep": int(60 / RUNTIME.timestep_minutes),
            "grid-filter": "*",
            "north": RUNTIME.north_deg,
            "min-sensor-count": 200,
            "cpu-count": RUNTIME.cpu_count,
        }
        input_json.write_text(json.dumps(recipe_inputs, ensure_ascii=True, indent=2), encoding="ascii")
        selected_vol = sum(v["removed_volume_m3"] for v in vols if v["selected"])
        scenario_rows.append(
            {
                "scenario": scenario["scenario"],
                "pair": pair,
                "model_type": "rule_flat",
                "sensor_count": len(grid),
                "date": "2026-12-21",
                "time_range": "08:15-15:45",
                "timestep_minutes": RUNTIME.timestep_minutes,
                "grid_size_m": RUNTIME.grid_size_m,
                "sensor_height_m": RUNTIME.sensor_height_m,
                "north_deg": RUNTIME.north_deg,
                "radiance_recipe": "lbt-recipes direct-sun-hours",
                "hbjson": str(hbjson),
                "wea": str(wea),
                "input_json": str(input_json),
                "intervention_volume_m3": selected_vol,
                "source_rank_2p5d_score": getattr(row, "rank_2p5d_score"),
                "source_is_pareto_front_2p5d": getattr(row, "is_pareto_front"),
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

    pd.DataFrame(scenario_rows).to_csv(RESULTS / "125_HB_Radiance追加场景参数表.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(volume_rows).to_csv(RESULTS / "126_HB_Radiance追加体量结果.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(run_rows).to_csv(BATCH / "run_manifest.csv", index=False, encoding="utf-8-sig")
    (BATCH / "prepare_summary.json").write_text(
        json.dumps(
            {"generated_at": datetime.now().isoformat(timespec="seconds"), "scenario_count": len(run_rows), "sensor_count": len(grid)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_run_metadata(
        RUNTIME,
        stage="prepare_hb_extra",
        inputs=[RESULTS / "123_需追加HB_Radiance复核候选清单.csv"],
        extra={"scenario_count": len(run_rows), "sensor_count": len(grid)},
    )
    print(BATCH / "run_manifest.csv")
    print(pd.DataFrame(run_rows)[["scenario"]].to_string(index=False))


if __name__ == "__main__":
    main()
