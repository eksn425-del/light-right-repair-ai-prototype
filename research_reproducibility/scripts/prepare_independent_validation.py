"""Prepare Honeybee models for the frozen independent validation sample."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from honeybee.model import Model
from honeybee_radiance.sensorgrid import Sensor, SensorGrid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "legacy_route_b"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402
from route_b_prepare_hb_batch import building_shades, create_grid, load_canonical, write_wea  # noqa: E402


def main() -> None:
    runtime = load_runtime()
    validation = runtime.run_dir / "independent_validation"
    sample = pd.read_csv(validation / "VALIDATION_SAMPLE_FROZEN.csv")
    batch = validation / "hb_batch"
    results = runtime.results_dir
    batch.mkdir(parents=True, exist_ok=True)
    buildings, geom_by_id = load_canonical()
    grid = create_grid(geom_by_id, grid_size=runtime.grid_size_m, sensor_z=runtime.sensor_height_m)
    sensors = [Sensor(pos=(row.x, row.y, row.z), dir=(0, 0, 1)) for row in grid.itertuples(index=False)]
    grid_label = f"ground_{runtime.grid_size_m:g}m_road_open_space"
    sensor_grid = SensorGrid(grid_label, sensors)
    grid.to_csv(validation / "sensor_points.csv", index=False, encoding="utf-8-sig")

    params: list[dict[str, object]] = []
    manifest: list[dict[str, str]] = []
    volumes: list[dict[str, object]] = []
    for _, row in sample.iterrows():
        pair = str(row["pair_key"])
        scenario = f"independent_{int(row['sample_order']):02d}_{pair.replace(',', '_')}_rule_flat"
        scen_dir = batch / scenario
        input_dir = scen_dir / "inputs"
        input_dir.mkdir(parents=True, exist_ok=True)
        definition = {"scenario": scenario, "pair": pair, "model_type": "rule_flat", "note": "frozen independent validation sample"}
        shades, volume_rows = building_shades(buildings, geom_by_id, definition)
        volumes.extend(volume_rows)
        model = Model(f"canonical_site_v2_{scenario}", orphaned_shades=shades, units="Meters", tolerance=0.01)
        model.properties.radiance.add_sensor_grid(sensor_grid)
        hbjson = input_dir / f"{scenario}.hbjson"
        model.to_hbjson(name=hbjson.name, folder=str(hbjson.parent), indent=2)
        wea = input_dir / "winter_solstice_30min.wea"
        write_wea(wea)
        input_json = input_dir / f"{scenario}_inputs.json"
        input_json.write_text(
            json.dumps(
                {
                    "model": str(hbjson),
                    "wea": str(wea),
                    "timestep": int(60 / runtime.timestep_minutes),
                    "grid-filter": "*",
                    "north": runtime.north_deg,
                    "min-sensor-count": 200,
                    "cpu-count": runtime.cpu_count,
                },
                ensure_ascii=True,
                indent=2,
            ),
            encoding="ascii",
        )
        selected_volume = sum(item["removed_volume_m3"] for item in volume_rows if item["selected"])
        params.append(
            {
                "scenario": scenario,
                "pair": pair,
                "pair_key": pair,
                "model_type": "rule_flat",
                "sample_order": int(row["sample_order"]),
                "stratum": row["stratum"],
                "sensor_count": len(grid),
                "intervention_volume_m3": selected_volume,
                "grid_size_m": runtime.grid_size_m,
                "sensor_height_m": runtime.sensor_height_m,
                "analysis_date": runtime.analysis_date,
            }
        )
        manifest.append({"scenario": scenario, "project_folder": str(scen_dir), "input_json": str(input_json), "debug_folder": str(scen_dir / "debug")})
    pd.DataFrame(params).to_csv(validation / "validation_scenario_parameters.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(volumes).to_csv(validation / "validation_volume_rows.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(manifest).to_csv(batch / "run_manifest.csv", index=False, encoding="utf-8-sig")
    write_run_metadata(
        runtime,
        stage="prepare_independent_validation",
        inputs=[validation / "VALIDATION_SAMPLE_FROZEN.csv", runtime.run_dir / "canonical_site_v2" / "canonical_site_v2.geojson"],
        extra={"sample_size": len(sample), "sensor_count": len(grid)},
    )
    print(batch / "run_manifest.csv")


if __name__ == "__main__":
    main()
