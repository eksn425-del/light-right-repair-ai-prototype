"""Classify final candidates from measured rule and design-translation outputs.

Candidate IDs are never used as classification rules. The output status is
derived from the measured evidence in the input tables.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, strict_bool, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
RESULTS = RUNTIME.results_dir
FIGURES = RUNTIME.figures_dir
DOCS = RUNTIME.docs_dir


def classify(rule_row: pd.Series, design_row: pd.Series | None) -> tuple[str, str]:
    """Return a data-driven status and reason for one candidate pair."""

    pair = str(rule_row["pair_key"])
    hb_pareto = strict_bool(rule_row["is_hb_pareto_front"], field=f"{pair}.is_hb_pareto_front")
    rule_gain = float(rule_row["low_area_drop_h3_m2"])
    if design_row is None:
        return "未完成复算", "缺少设计转译三维复算结果，不能形成最终判断。"

    design_gain = float(design_row["low_area_drop_h3_m2"])
    worsened = int(float(design_row["worsened_point_count"]))
    new_low = float(design_row["new_low_area_h3_m2"])
    adverse = worsened > 0 or new_low > 0

    if design_gain <= 0:
        return "不推荐", "设计转译后的低日照区面积未下降。"
    if adverse:
        return "高收益复核候选", f"设计转译仍有 {worsened} 个恶化点和 {new_low:g} m² 新增低日照区，需要人工复核。"
    if hb_pareto and rule_gain > 0:
        return "优先候选区间", "HB-Radiance Pareto 成立，设计转译正向且未观察到新增低日照区或恶化点。"
    return "正向候选/待复核", "设计转译正向，但未同时满足 HB-Radiance Pareto 与无副作用条件。"


def main() -> None:
    rule = pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv")
    summary = pd.read_csv(RESULTS / "131_HB_Radiance合并候选汇总结果.csv")
    required_rule = {"pair_key", "is_hb_pareto_front", "low_area_drop_h3_m2", "avg_gain_vs_baseline_h", "intervention_volume_m3", "rank_hb_low_area_drop"}
    missing = required_rule - set(rule.columns)
    if missing:
        raise ValueError(f"Missing rule columns: {sorted(missing)}")
    design = summary[summary["model_type"].astype(str).eq("design_stepback")].copy()
    design_by_pair = {str(row["pair_key"]): row for _, row in design.iterrows()}

    rows: list[dict[str, object]] = []
    for _, rv in rule.sort_values(["rank_hb_low_area_drop", "pair_key"]).iterrows():
        pair = str(rv["pair_key"])
        dv = design_by_pair.get(pair)
        status, reason = classify(rv, dv)
        rows.append(
            {
                "pair_key": pair,
                "final_status": status,
                "reason": reason,
                "rule_low_area_drop_h3_m2": float(rv["low_area_drop_h3_m2"]),
                "rule_avg_gain_h": float(rv["avg_gain_vs_baseline_h"]),
                "rule_intervention_volume_m3": float(rv["intervention_volume_m3"]),
                "rule_hb_pareto": strict_bool(rv["is_hb_pareto_front"], field=f"{pair}.is_hb_pareto_front"),
                "rule_hb_rank": int(float(rv["rank_hb_low_area_drop"])),
                "design_low_area_drop_h3_m2": np.nan if dv is None else float(dv["low_area_drop_h3_m2"]),
                "design_avg_gain_h": np.nan if dv is None else float(dv["avg_gain_vs_baseline_h"]),
                "design_improved_point_count": np.nan if dv is None else int(float(dv["improved_point_count"])),
                "design_worsened_point_count": np.nan if dv is None else int(float(dv["worsened_point_count"])),
                "design_new_low_area_h3_m2": np.nan if dv is None else float(dv["new_low_area_h3_m2"]),
                "design_validation_status": "已复算" if dv is not None else "未复算",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "138_最终候选规则与设计转译对比.csv", index=False, encoding="utf-8-sig")

    plot = out.head(15).copy()
    x = np.arange(len(plot))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11, 5), dpi=220)
    ax.bar(x - width / 2, plot["rule_low_area_drop_h3_m2"], width, label="Rule model")
    ax.bar(x + width / 2, plot["design_low_area_drop_h3_m2"], width, label="Design translation")
    for i, row in plot.reset_index(drop=True).iterrows():
        if row["design_worsened_point_count"] > 0 or row["design_new_low_area_h3_m2"] > 0:
            ax.text(i + width / 2, row["design_low_area_drop_h3_m2"] + 8, "review", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(plot["pair_key"], rotation=45, ha="right")
    ax.set_ylabel("Reduction of low-direct-sun area / m2")
    ax.set_title("Measured candidate classification inputs")
    ax.grid(axis="y", alpha=0.22)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "139_最终候选规则与设计转译对比图.png")
    plt.close(fig)

    priority = out[out["final_status"].eq("优先候选区间")]["pair_key"].tolist()
    review = out[out["final_status"].eq("高收益复核候选")]["pair_key"].tolist()
    md = [
        "# Candidate judgement",
        "",
        "Candidate status is derived from the measured HB-Radiance and design-translation columns. Candidate IDs are not used as hidden rules.",
        "",
        f"- Priority candidate interval: {', '.join(priority) if priority else 'none'}",
        f"- High-yield review candidates: {', '.join(review) if review else 'none'}",
        "- A missing design-translation row is reported as 未完成复算 and is never promoted to a recommendation.",
        "",
        out.to_markdown(index=False, floatfmt=".3f"),
    ]
    (DOCS / "140_最终候选判断说明.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="final_candidate_judgement",
        inputs=[RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv", RESULTS / "131_HB_Radiance合并候选汇总结果.csv"],
        extra={"candidate_count": int(len(out)), "priority_pairs": priority, "review_pairs": review},
    )
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
