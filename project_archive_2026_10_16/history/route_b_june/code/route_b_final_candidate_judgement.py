from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
RESULTS = ROOT / "results_csv"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

for font_path in [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf"), Path(r"C:\Windows\Fonts\simsun.ttc")]:
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=str(font_path)).get_name()]
        plt.rcParams["axes.unicode_minus"] = False
        break


FINAL_PAIRS = ["C9,C15", "C9,C13", "C9,C24", "C13,C24", "C6,C33"]


def main():
    rule = pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv")
    summary = pd.read_csv(RESULTS / "131_HB_Radiance合并候选汇总结果.csv")
    design = summary[summary["model_type"] == "design_stepback"].copy()
    rows = []
    for pair in FINAL_PAIRS:
        r = rule[rule["pair_key"] == pair]
        d = design[design["pair_key"] == pair]
        if r.empty:
            continue
        rv = r.iloc[0]
        dv = d.iloc[0] if not d.empty else None
        if pair in {"C9,C15", "C9,C13"}:
            status = "优先候选区间"
            reason = "HB Pareto 成立，设计转译仍正向，且无新增低日照区和无恶化点。"
        elif pair == "C9,C24":
            status = "高收益复核候选"
            reason = "规则模型收益最高，但设计转译出现少量恶化点和新增低日照区，需进一步设计师复核。"
        elif pair == "C13,C24":
            status = "历史候选/对照"
            reason = "规则与设计转译均正向，但在追加 HB 复核集合中不在 Pareto 前沿，且设计转译出现新增低日照区。"
        else:
            status = "不作为最终推荐"
            reason = "正式三维复核收益很小，不能作为唯一最终方案。"
        rows.append(
            {
                "pair_key": pair,
                "final_status": status,
                "reason": reason,
                "rule_low_area_drop_h3_m2": rv["low_area_drop_h3_m2"],
                "rule_avg_gain_h": rv["avg_gain_vs_baseline_h"],
                "rule_intervention_volume_m3": rv["intervention_volume_m3"],
                "rule_hb_pareto": rv["is_hb_pareto_front"],
                "rule_hb_rank": rv["rank_hb_low_area_drop"],
                "design_low_area_drop_h3_m2": np.nan if dv is None else dv["low_area_drop_h3_m2"],
                "design_avg_gain_h": np.nan if dv is None else dv["avg_gain_vs_baseline_h"],
                "design_improved_point_count": np.nan if dv is None else dv["improved_point_count"],
                "design_worsened_point_count": np.nan if dv is None else dv["worsened_point_count"],
                "design_new_low_area_h3_m2": np.nan if dv is None else dv["new_low_area_h3_m2"],
                "design_validation_status": "已复算" if dv is not None else "未复算",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "138_最终候选规则与设计转译对比.csv", index=False, encoding="utf-8-sig")

    plot = out.copy()
    x = np.arange(len(plot))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5), dpi=180)
    ax.bar(x - width / 2, plot["rule_low_area_drop_h3_m2"], width, label="规则整体减高")
    ax.bar(x + width / 2, plot["design_low_area_drop_h3_m2"], width, label="设计退台转译")
    for i, row in plot.iterrows():
        if row["design_worsened_point_count"] > 0 or row["design_new_low_area_h3_m2"] > 0:
            ax.text(i + width / 2, row["design_low_area_drop_h3_m2"] + 8, "需复核", ha="center", fontsize=8, color="#b27900")
    ax.set_xticks(x)
    ax.set_xticklabels(plot["pair_key"], rotation=0)
    ax.set_ylabel("3 h 阈值低直射日照区面积下降 / m²")
    ax.set_title("最终候选规则模型与设计转译模型对比")
    ax.grid(axis="y", alpha=0.22)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "139_最终候选规则与设计转译对比图.png")
    plt.close(fig)

    md = [
        "# 140_最终候选判断说明",
        "",
        "## 结论",
        "",
        "本轮不再保留 C6/C33 作为唯一推荐方案，也不把 C13/C24 改写为新唯一最优方案。基于统一几何、2.5D 全候选枚举、HB-Radiance Top/Pareto 追加复核，以及最终设计转译复算，论文应收敛为“经正式三维复核的候选区间”。",
        "",
        "优先候选区间为：",
        "",
        "- C9/C15：HB-Radiance 3 h 低直射日照区面积下降 351 m²，设计转译后仍下降 342 m²，无新增低日照区，无恶化点。",
        "- C9/C13：HB-Radiance 3 h 低直射日照区面积下降 333 m²，设计转译后仍下降 333 m²，无新增低日照区，无恶化点。",
        "",
        "高收益但需重点复核候选为：",
        "",
        "- C9/C24：规则模型下降 396 m²，为已复核集合最高；设计转译后下降 342 m²，但出现 4 个恶化点和 9 m² 新增低日照区，不宜直接写成最终推荐。",
        "",
        "历史候选处理：",
        "",
        "- C13/C24：正式三维复核正向，但在追加候选集合中排名第 12，且不在 HB Pareto 前沿；可作为方法演进中的对照候选，不作为最终优先候选。",
        "- C6/C33：正式三维复核下 3 h 低直射日照区面积仅下降 9 m²，设计转译下降 18 m²，不能作为唯一最终方案。",
        "",
        "## 证据表",
        "",
        out.to_markdown(index=False, floatfmt=".3f"),
        "",
        "图表说明：`139_最终候选规则与设计转译对比图.png` 用于证明最终候选必须经设计转译复算后再判断，不能把规则整体减高模型的效果直接等同于建筑设计方案效果。",
    ]
    (DOCS / "140_最终候选判断说明.md").write_text("\n".join(md), encoding="utf-8")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
