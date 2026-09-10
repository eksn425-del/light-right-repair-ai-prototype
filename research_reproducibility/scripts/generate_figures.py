"""Generate paper-support figures from the current run outputs only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=320, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    import os
    os.environ["LIGHT_EQUITY_RUN_ID"] = run_dir.name
    os.environ["LIGHT_EQUITY_RUN_DIR"] = str(run_dir)
    runtime = load_runtime()
    figures = run_dir / "figures"
    results_csv = run_dir / "results_csv"
    results = run_dir / "results"

    # F01: the method is intentionally a schematic, not a result claim.
    fig, ax = plt.subplots(figsize=(12, 3.4), dpi=320)
    ax.axis("off")
    labels = ["Source audit\nCAD / OBJ / CSV", "Canonical geometry\n2.5D screening", "HB-Radiance\ncurated validation", "Independent sample\nerror and rank check", "Decision ledger\nfigures and handoff"]
    colors = ["#457b9d", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]
    xs = np.linspace(0.08, 0.92, len(labels))
    for x, label, color in zip(xs, labels, colors):
        patch = FancyBboxPatch((x - 0.085, 0.34), 0.17, 0.32, boxstyle="round,pad=0.02", fc=color, ec="white", lw=1.5, alpha=0.95, transform=ax.transAxes)
        ax.add_patch(patch)
        ax.text(x, 0.50, label, ha="center", va="center", color="white", fontsize=11, transform=ax.transAxes)
    for left, right in zip(xs[:-1], xs[1:]):
        ax.add_patch(FancyArrowPatch((left + 0.09, 0.50), (right - 0.09, 0.50), arrowstyle="-|>", mutation_scale=16, lw=1.4, color="#4d4d4d", transform=ax.transAxes))
    ax.set_title("F01. Reproducible solar-access screening workflow", fontsize=14, weight="bold")
    save(fig, figures / "F01_workflow.png")

    # F02: measured baseline sensor field. The configured timestep converts states to hours.
    sensors = pd.read_csv(results_csv / "100_HB_Radiance传感点.csv")
    ill_path = run_dir / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "direct_sun_hours" / "ground_3m_road_open_space.ill"
    baseline_hours = np.loadtxt(ill_path, ndmin=2).sum(axis=1) * runtime.timestep_hours
    sensors["baseline_hours"] = baseline_hours
    fig, ax = plt.subplots(figsize=(8, 6), dpi=320)
    scatter = ax.scatter(sensors["x"], sensors["y"], c=sensors["baseline_hours"], s=7, cmap="viridis", vmin=0, vmax=8)
    fig.colorbar(scatter, ax=ax, label="Direct sun hours")
    ax.set_aspect("equal")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title("F02. Baseline winter-solstice direct-sun field")
    ax.grid(alpha=0.15)
    save(fig, figures / "F02_baseline_field.png")

    # F03: independent high-fidelity rank agreement for the curated set.
    verified = pd.read_csv(results_csv / "132_HB_Radiance已复核候选排名与Pareto.csv")
    fig, ax = plt.subplots(figsize=(6.5, 6), dpi=320)
    ax.scatter(verified["low_area_drop_h3_m2_2p5d"], verified["low_area_drop_h3_m2"], c=verified["rank_hb_low_area_drop"], cmap="plasma", s=45, edgecolor="white")
    lo = min(verified["low_area_drop_h3_m2_2p5d"].min(), verified["low_area_drop_h3_m2"].min())
    hi = max(verified["low_area_drop_h3_m2_2p5d"].max(), verified["low_area_drop_h3_m2"].max())
    ax.plot([lo, hi], [lo, hi], "--", color="#555", lw=1)
    ax.set_xlabel("2.5D low-area drop / m²")
    ax.set_ylabel("HB-Radiance low-area drop / m²")
    ax.set_title("F03. Curated candidate agreement")
    ax.grid(alpha=0.18)
    save(fig, figures / "F03_curated_rank_agreement.png")

    # F04: rule model versus design translation for the actually rerun pairs.
    design = pd.read_csv(results_csv / "138_最终候选规则与设计转译对比.csv")
    design = design[design["design_low_area_drop_h3_m2"].notna()].copy()
    metrics = ["low_area_drop_h3_m2", "avg_gain_h"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), dpi=320)
    for ax, metric, label in zip(axes, metrics, ["Low-area drop / m²", "Average gain / h"]):
        x = np.arange(len(design))
        rule = design[f"rule_{metric}"]
        after = design[f"design_{metric}"]
        ax.bar(x - 0.18, rule, width=0.36, label="Rule model", color="#457b9d")
        ax.bar(x + 0.18, after, width=0.36, label="Design translation", color="#e9c46a")
        ax.set_xticks(x, design["pair_key"], rotation=25, ha="right")
        ax.set_ylabel(label)
        ax.grid(axis="y", alpha=0.18)
    axes[0].legend(frameon=False)
    fig.suptitle("F04. Verified rule model versus design translation", weight="bold")
    fig.tight_layout()
    save(fig, figures / "F04_design_translation_comparison.png")

    # F05: a point-level change map for one verified rule scenario.
    aligned = pd.read_csv(results_csv / "141_已复核候选Python与HB点位对齐结果.csv")
    aligned = aligned[aligned["pair_key"] == "C9,C24"]
    fig, ax = plt.subplots(figsize=(8, 6), dpi=320)
    delta = aligned["delta_hb"]
    scatter = ax.scatter(aligned["x"], aligned["y"], c=delta, s=12, cmap="coolwarm", vmin=-8, vmax=8)
    fig.colorbar(scatter, ax=ax, label="HB direct-sun change / h")
    ax.set_aspect("equal")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title("F05. Point-level change map: C9,C24 rule model")
    ax.grid(alpha=0.15)
    save(fig, figures / "F05_candidate_change_map.png")

    # F06: frozen independent validation sample.
    independent = pd.read_csv(results / "independent_validation_results.csv")
    fig, ax = plt.subplots(figsize=(6.5, 6), dpi=320)
    ax.scatter(independent["two_d_low_area_drop_h3_m2"], independent["hb_low_area_drop_h3_m2"], c=independent["stratum"].str[-1].astype(int), cmap="viridis", s=48, edgecolor="white")
    lo = min(independent["two_d_low_area_drop_h3_m2"].min(), independent["hb_low_area_drop_h3_m2"].min())
    hi = max(independent["two_d_low_area_drop_h3_m2"].max(), independent["hb_low_area_drop_h3_m2"].max())
    ax.plot([lo, hi], [lo, hi], "--", color="#555", lw=1)
    ax.set_xlabel("2.5D low-area drop / m²")
    ax.set_ylabel("HB-Radiance low-area drop / m²")
    ax.set_title("F06. Independent validation sample")
    ax.grid(alpha=0.18)
    save(fig, figures / "F06_independent_validation_scatter.png")

    # F07: measured runtime and clearly labelled serial-equivalent extrapolation.
    summary = pd.read_json(results / "runtime_summary_v2.json", typ="series")
    values = [float(summary["screening_median_seconds"]), float(summary["hb_median_seconds_per_scene"]), float(summary["serial_equivalent_hb_630_seconds"])]
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=320)
    bars = ax.bar(["2.5D median", "HB median", "HB 630 estimate"], values, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    ax.set_ylabel("Wall time / seconds")
    ax.set_title("F07. Measured and serial-equivalent computational cost")
    ax.grid(axis="y", alpha=0.18)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    save(fig, figures / "F07_runtime_comparison.png")

    # F08: rank robustness across deterministic and perturbed weights.
    stability = pd.read_csv(results / "candidate_rank_stability_v2.csv").head(20).sort_values("top10_selection_frequency")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=320)
    ax.barh(stability["candidate_id"], stability["top10_selection_frequency"], color="#457b9d")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Top-10 selection frequency")
    ax.set_title("F08. Candidate rank robustness under four-term weight perturbation")
    ax.grid(axis="x", alpha=0.18)
    save(fig, figures / "F08_weight_robustness.png")

    write_run_metadata(
        runtime,
        stage="paper_figures",
        inputs=[results / "independent_validation_metrics.csv", results_csv / "132_HB_Radiance已复核候选排名与Pareto.csv"],
        extra={"figure_count": 9, "dpi": 320, "composite_figure": "F09_independent_composite_ranking.png"},
    )

    print(f"Generated 9 paper-support figures in {figures} (F09 is generated by validate_independent_composite.py)")


if __name__ == "__main__":
    main()
