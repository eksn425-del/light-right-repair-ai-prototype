from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "light_equity_project"
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from src.algorithm_a_diagnosis.run_diagnosis import BUILDING_COLUMNS, STREET_COLUMNS  # noqa: E402
from src.geometry.voxelizer import create_ground_grid, estimate_site_diagonal  # noqa: E402
from src.io.export_results import ensure_dir, write_csv, write_json  # noqa: E402
from src.io.load_tables import normalise_bool_columns, read_config, read_table  # noqa: E402
from src.solar.sun_path import sample_sun_path  # noqa: E402
from src.solar.sunlight_simulator import _apply_subtractive_height_changes  # noqa: E402


DATASET_DIR = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
INTERVENTIONS_CSV = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "conservative"
    / "B_candidates"
    / "interventions.csv"
)
CASES = [
    {
        "grid_size_m": 6.0,
        "config_dir": PROJECT / "outputs" / "light_product_2026_06_02" / "strategy_comparison_postsim" / "_configs" / "conservative",
        "baseline_csv": PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis" / "sunlight_hours.csv",
        "baseline_summary": PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis" / "A_summary.json",
    },
    {
        "grid_size_m": 3.0,
        "config_dir": PROJECT / "outputs" / "light_product_2026_06_03" / "grid_sensitivity" / "grid_3m" / "config_grid_3m",
        "baseline_csv": PROJECT / "outputs" / "light_product_2026_06_03" / "grid_sensitivity" / "grid_3m" / "A_diagnosis" / "sunlight_hours.csv",
        "baseline_summary": PROJECT / "outputs" / "light_product_2026_06_03" / "grid_sensitivity" / "grid_3m" / "A_diagnosis" / "A_summary.json",
    },
]
OUTPUT_DIR = ROOT / "paper_revision_work_2026_06_14" / "c6_c33_same_scheme_grid_fast"
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")
PROP = FontProperties(fname=str(FONT_PATH)) if FONT_PATH.exists() else None
PROP_BOLD = FontProperties(fname=str(Path("C:/Windows/Fonts/msyhbd.ttc"))) if Path("C:/Windows/Fonts/msyhbd.ttc").exists() else PROP


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


def fast_simulate(
    ground_grid: pd.DataFrame,
    buildings: pd.DataFrame,
    sun_samples: list[dict],
    site_config: dict,
    solar_config: dict,
    max_ray_distance: float,
    interventions: pd.DataFrame,
) -> pd.DataFrame:
    """Vectorized reproduction of the project 2.5D effective-height subtraction model."""
    scenario = _apply_subtractive_height_changes(buildings, interventions, site_config)
    x_min = scenario["x_min"].astype(float).to_numpy()
    x_max = scenario["x_max"].astype(float).to_numpy()
    y_min = scenario["y_min"].astype(float).to_numpy()
    y_max = scenario["y_max"].astype(float).to_numpy()
    heights = scenario["height_m"].astype(float).to_numpy()
    max_height = float(np.max(heights))
    ray_step = float(solar_config.get("shadow_ray_step_m", 2.0))
    dark_threshold = float(site_config.get("dark_sunlight_threshold_hours", 3.0))
    distances_all = np.arange(ray_step, max_ray_distance + ray_step, ray_step)
    active_hours = sum(float(sample["weight_hours"]) for sample in sun_samples if sample.get("is_active", True))

    rows = []
    for _, point in ground_grid.iterrows():
        px = float(point["x"])
        py = float(point["y"])
        pz = float(point["z"])
        sunlight_hours = 0.0
        for sample in sun_samples:
            if not sample.get("is_active", True):
                continue
            vx = float(sample["vector_x"])
            vy = float(sample["vector_y"])
            vz = float(sample["vector_z"])
            if vz <= 0:
                shadowed = True
            else:
                rz = pz + vz * distances_all
                active = rz <= max_height + 5.0
                if not np.any(active):
                    shadowed = False
                else:
                    d = distances_all[active]
                    rz = rz[active]
                    rx = px + vx * d
                    ry = py + vy * d
                    inside = (
                        (rx[:, None] >= x_min[None, :])
                        & (rx[:, None] <= x_max[None, :])
                        & (ry[:, None] >= y_min[None, :])
                        & (ry[:, None] <= y_max[None, :])
                        & (rz[:, None] <= heights[None, :])
                    )
                    shadowed = bool(np.any(inside))
            if not shadowed:
                sunlight_hours += float(sample["weight_hours"])
        rows.append(
            {
                "grid_id": point["grid_id"],
                "x": point["x"],
                "y": point["y"],
                "sunlight_hours": round(sunlight_hours, 3),
                "shadow_hours": round(max(active_hours - sunlight_hours, 0.0), 3),
                "is_dark_zone": sunlight_hours < dark_threshold,
            }
        )
    return pd.DataFrame(rows)


def run_case(case: dict, buildings: pd.DataFrame, streets: pd.DataFrame, interventions: pd.DataFrame) -> dict:
    grid_size = float(case["grid_size_m"])
    case_dir = ensure_dir(OUTPUT_DIR / f"grid_{grid_size:g}m_fixed_c6_c33")
    site_config = read_config(case["config_dir"] / "site_config.yaml")
    solar_config = read_config(case["config_dir"] / "solar_config.yaml")
    baseline = pd.read_csv(case["baseline_csv"])
    ground_grid = create_ground_grid(buildings, streets, site_config)
    sun_samples = sample_sun_path(site_config, solar_config)
    max_ray_distance = estimate_site_diagonal(buildings, streets, site_config)
    post = fast_simulate(
        ground_grid=ground_grid,
        buildings=buildings,
        sun_samples=sun_samples,
        site_config=site_config,
        solar_config=solar_config,
        max_ray_distance=max_ray_distance,
        interventions=interventions,
    )
    baseline_bool = bool_series(baseline["is_dark_zone"])
    post_bool = bool_series(post["is_dark_zone"])
    baseline_avg = float(baseline["sunlight_hours"].mean())
    post_avg = float(post["sunlight_hours"].mean())
    baseline_dark = float(baseline_bool.mean())
    post_dark = float(post_bool.mean())
    merged = baseline[["grid_id", "x", "y", "sunlight_hours", "is_dark_zone"]].merge(
        post[["grid_id", "sunlight_hours", "is_dark_zone"]],
        on="grid_id",
        suffixes=("_baseline", "_post"),
    )
    merged["sunlight_diff_h"] = merged["sunlight_hours_post"] - merged["sunlight_hours_baseline"]
    merged["dark_to_light"] = bool_series(merged["is_dark_zone_baseline"]) & ~bool_series(merged["is_dark_zone_post"])
    merged["light_to_dark"] = ~bool_series(merged["is_dark_zone_baseline"]) & bool_series(merged["is_dark_zone_post"])
    write_csv(post, case_dir / "c6_c33_fixed_post_sunlight_hours.csv")
    write_csv(merged, case_dir / "c6_c33_fixed_grid_diff.csv")

    result = {
        "grid_size_m": grid_size,
        "baseline_average_sunlight_hours": round(baseline_avg, 3),
        "post_average_sunlight_hours": round(post_avg, 3),
        "average_sunlight_gain_h": round(post_avg - baseline_avg, 3),
        "baseline_dark_zone_ratio": round(baseline_dark, 4),
        "post_dark_zone_ratio": round(post_dark, 4),
        "baseline_dark_zone_percent": round(baseline_dark * 100, 2),
        "post_dark_zone_percent": round(post_dark * 100, 2),
        "dark_zone_drop_percentage_points": round((baseline_dark - post_dark) * 100, 2),
        "relative_dark_zone_improvement": round((baseline_dark - post_dark) / baseline_dark, 4) if baseline_dark else 0.0,
        "baseline_dark_grid_count": int(baseline_bool.sum()),
        "post_dark_grid_count": int(post_bool.sum()),
        "total_grid_count": int(len(post)),
        "dark_to_light_grid_count": int(merged["dark_to_light"].sum()),
        "light_to_dark_grid_count": int(merged["light_to_dark"].sum()),
        "max_single_point_gain_h": round(float(merged["sunlight_diff_h"].max()), 3),
        "min_single_point_gain_h": round(float(merged["sunlight_diff_h"].min()), 3),
        "intervention_volume": round(float(interventions["volume_change"].abs().sum()), 3),
        "changed_building_ids": ";".join(interventions["target_building_id"].astype(str).tolist()),
        "case_output_dir": str(case_dir),
    }
    write_json(result, case_dir / "c6_c33_fixed_same_scheme_summary.json")
    return result


def make_chart(summary: pd.DataFrame, output_path: Path) -> Path:
    labels = [f"{value:g} m" for value in summary["grid_size_m"]]
    x = np.arange(len(labels))
    width = 0.35
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2), dpi=220)

    specs = [
        ("average", "平均采光小时 / h", "baseline_average_sunlight_hours", "post_average_sunlight_hours"),
        ("dark", "暗区比例 / %", "baseline_dark_zone_percent", "post_dark_zone_percent"),
        ("count", "暗区网格数", "baseline_dark_grid_count", "post_dark_grid_count"),
    ]
    for ax, (_, title, base_col, post_col) in zip(axes, specs):
        base = summary[base_col].to_numpy(dtype=float)
        post = summary[post_col].to_numpy(dtype=float)
        ax.bar(x - width / 2, base, width, label="现状", color="#4f7ccf", alpha=0.82)
        ax.bar(x + width / 2, post, width, label="固定 C6/C33 后", color="#f2a93b", alpha=0.88)
        for i, value in enumerate(base):
            ax.text(i - width / 2, value, f"{value:.2f}" if value < 100 else f"{value:.0f}", ha="center", va="bottom", fontsize=8)
        for i, value in enumerate(post):
            ax.text(i + width / 2, value, f"{value:.2f}" if value < 100 else f"{value:.0f}", ha="center", va="bottom", fontsize=8)
        ax.set_title(title, fontsize=11, fontproperties=PROP_BOLD)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontproperties=PROP)
        ax.grid(axis="y", color="#e5e7eb", lw=0.55)
    axes[0].legend(loc="upper left", frameon=False, fontsize=8, prop=PROP)
    fig.suptitle(
        "C6/C33 同一保守型方案在 6 m 与 3 m 网格下的复算结果",
        fontsize=13,
        fontproperties=PROP_BOLD,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    buildings = normalise_bool_columns(
        read_table(DATASET_DIR / "buildings.csv", BUILDING_COLUMNS),
        ["movable", "protected"],
    )
    streets = normalise_bool_columns(
        read_table(DATASET_DIR / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )
    interventions_all = pd.read_csv(INTERVENTIONS_CSV)
    interventions = interventions_all[interventions_all["candidate_id"].astype(str) == "candidate_01"].copy()
    interventions = interventions[interventions["target_building_id"].astype(str).isin(["C6", "C33"])].copy()

    rows = [run_case(case, buildings, streets, interventions) for case in CASES]
    summary = pd.DataFrame(rows)
    metrics_path = write_csv(summary, OUTPUT_DIR / "c6_c33_same_scheme_grid_metrics.csv")
    chart_path = make_chart(summary, OUTPUT_DIR / "c6_c33_same_scheme_grid_chart.png")
    report = {
        "metrics_csv": str(metrics_path),
        "chart": str(chart_path),
        "method": "Fixed C6/C33 candidate_01 intervention re-simulated at 6m and 3m using vectorized reproduction of the project simplified 2.5D effective-height subtraction model.",
        "caveat": "This is a same-scheme grid test, not a new 3m optimization. The 3m optimizer previously selected C28/C34/C38/C9; this test isolates whether C6/C33 remains directionally meaningful under a denser grid.",
        "rows": rows,
    }
    summary_path = write_json(report, OUTPUT_DIR / "c6_c33_same_scheme_grid_summary.json")
    print(json.dumps({"summary": str(summary_path), "metrics": str(metrics_path), "chart": str(chart_path), "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
