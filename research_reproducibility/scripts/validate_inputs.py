"""Validate the reproducibility-critical CSV contracts for one research run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REQUIRED_BUILDING_COLUMNS = {
    "building_id",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "height_m",
    "movable",
    "protected",
}
REQUIRED_CANDIDATE_COLUMNS = {
    "candidate_id",
    "building_ids",
    "intervention_volume_m3",
    "low_area_drop_h3_m2",
}
REQUIRED_SENSOR_COLUMNS = {"grid_id", "x", "y", "z"}


def strict_bool(value: object) -> bool:
    """Parse the boolean vocabulary allowed by the research data contract."""
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    buildings = pd.read_csv(run_dir / "canonical_site_v2" / "canonical_buildings.csv")
    check("building_rows", len(buildings) == 45, f"rows={len(buildings)}")
    check("building_id_unique", buildings["building_id"].is_unique, "building_id uniqueness")
    check("building_schema", REQUIRED_BUILDING_COLUMNS.issubset(buildings.columns), "required columns present")
    numeric = ["x_min", "x_max", "y_min", "y_max", "height_m"]
    numeric_ok = all(pd.to_numeric(buildings[column], errors="coerce").notna().all() for column in numeric)
    check("building_numeric_fields", numeric_ok, "geometry and height columns are numeric")
    bounds_ok = bool(
        (buildings["x_max"] > buildings["x_min"]).all()
        and (buildings["y_max"] > buildings["y_min"]).all()
        and (buildings["height_m"] > 0).all()
    )
    check("building_bounds", bounds_ok, "positive boxes and heights")
    movable = buildings["movable"].map(strict_bool)
    protected = buildings["protected"].map(strict_bool)
    eligible = buildings[movable & ~protected & (buildings["height_m"] > 3.0)]
    check("eligible_buildings", len(eligible) == 36, f"eligible={len(eligible)}")

    candidates = pd.read_csv(run_dir / "results_csv" / "120_canonical_2p5D完整双建筑候选排名.csv")
    check("candidate_schema", REQUIRED_CANDIDATE_COLUMNS.issubset(candidates.columns), "required columns present")
    check("candidate_count", len(candidates) == 630, f"rows={len(candidates)} expected=C(36,2)")
    check("candidate_id_unique", candidates["candidate_id"].is_unique, "candidate_id uniqueness")
    check("candidate_pair_unique", candidates["building_ids"].is_unique, "building pair uniqueness")
    check("nonnegative_geometry_metrics", bool((candidates["intervention_volume_m3"] >= 0).all()), "volume >= 0")

    sensors = pd.read_csv(run_dir / "results_csv" / "100_HB_Radiance传感点.csv")
    check("sensor_schema", REQUIRED_SENSOR_COLUMNS.issubset(sensors.columns), "required columns present")
    check("sensor_id_unique", sensors["grid_id"].is_unique, "grid_id uniqueness")
    check("sensor_count", len(sensors) == 2031, f"rows={len(sensors)}")

    hb = pd.read_csv(run_dir / "results_csv" / "131_HB_Radiance合并候选汇总结果.csv")
    hb_rule = hb[(hb["model_type"] == "rule_flat") & (hb["source"] == "extra_top_pareto")]
    check("hb_total_scenarios", len(hb) == 31, f"rows={len(hb)} including baseline, curated, design and independent-support scenes")
    check("hb_verified_rule_candidates", len(hb_rule) == 23, f"rows={len(hb_rule)}")
    check("hb_pair_unique", hb_rule["pair_key"].is_unique, "verified rule candidate pairs")

    passed = all(item["passed"] for item in checks)
    result = {"run_dir": str(run_dir), "passed": passed, "checks": checks}
    output = run_dir / "results" / "input_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
