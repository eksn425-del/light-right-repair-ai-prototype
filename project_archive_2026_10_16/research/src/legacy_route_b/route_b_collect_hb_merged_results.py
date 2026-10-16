from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
RESULTS = RUNTIME.results_dir
FIGURES = RUNTIME.figures_dir
DOCS = RUNTIME.docs_dir
BATCH_INITIAL = ROOT / "hb_radiance_project_batch"
BATCH_EXTRA = ROOT / "hb_radiance_project_batch_extra"
BATCH_FINAL_DESIGN = ROOT / "hb_radiance_project_final_design"

SENSOR_FILE = RESULTS / "100_HB_Radiance传感点.csv"
GRID_NAME = f"ground_{RUNTIME.grid_size_m:g}m_road_open_space"
CELL_AREA_M2 = RUNTIME.grid_size_m ** 2

plt.rcParams["axes.unicode_minus"] = False


def read_values(path: Path) -> list[float]:
    return [float(x.strip()) for x in path.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]


def read_matrix(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            rows.append([float(x) for x in line.split()])
    return np.array(rows, dtype=float)


def pair_key(pair: str) -> str:
    ids = [p.strip() for p in str(pair).split(",") if p.strip()]
    ids.sort(key=lambda x: int(re.sub(r"\D", "", x) or 0))
    return ",".join(ids)


def is_canonical_rule_scenario(name: str) -> bool:
    return bool(re.fullmatch(r"C\d+_C\d+_rule_flat", str(name)))


def add_manifest_rows(manifest_path: Path, params_path: Path, source: str) -> list[dict]:
    manifest = pd.read_csv(manifest_path)
    params = pd.read_csv(params_path)
    params_by_scenario = params.set_index("scenario").to_dict(orient="index")
    rows = []
    for r in manifest.itertuples(index=False):
        scenario = r.scenario
        p = params_by_scenario[scenario]
        pair = "" if pd.isna(p.get("pair", "")) else str(p.get("pair", ""))
        rows.append(
            {
                "scenario": scenario,
                "project_folder": str(r.project_folder),
                "pair": pair,
                "pair_key": pair_key(pair),
                "model_type": p.get("model_type", ""),
                "intervention_volume_m3": float(p.get("intervention_volume_m3", 0.0)),
                "source": source,
                "source_rank_2p5d_score": p.get("source_rank_2p5d_score", np.nan),
                "source_is_pareto_front_2p5d": p.get("source_is_pareto_front_2p5d", np.nan),
            }
        )
    return rows


def compute_summary(raw: pd.DataFrame, scenario_meta: pd.DataFrame) -> pd.DataFrame:
    base = raw[raw["scenario"] == "baseline"].set_index("grid_id")["direct_sun_hours"]
    summaries = []
    for scenario, sub in raw.groupby("scenario", sort=False):
        meta = scenario_meta[scenario_meta["scenario"] == scenario].iloc[0].to_dict()
        direct = sub.set_index("grid_id")["direct_sun_hours"]
        delta = direct - base
        row = {
            **meta,
            "sensor_count": len(sub),
            "mean_direct_sun_hours": float(direct.mean()),
            "min_direct_sun_hours": float(direct.min()),
            "max_direct_sun_hours": float(direct.max()),
            "avg_gain_vs_baseline_h": float(delta.mean()),
            "improved_point_count": int((delta > 1e-9).sum()),
            "worsened_point_count": int((delta < -1e-9).sum()),
            "unchanged_point_count": int((abs(delta) <= 1e-9).sum()),
        }
        for threshold in [2.0, 3.0, 4.0]:
            low = direct < threshold
            base_low = base < threshold
            row[f"low_area_h{threshold:g}_m2"] = float(low.sum() * CELL_AREA_M2)
            row[f"low_area_drop_h{threshold:g}_m2"] = float((base_low.sum() - low.sum()) * CELL_AREA_M2)
            row[f"new_low_area_h{threshold:g}_m2"] = float(((~base_low) & low).sum() * CELL_AREA_M2)
        row["unit_low_area_drop_per_1000m3"] = (
            row["low_area_drop_h3_m2"] / row["intervention_volume_m3"] * 1000 if row["intervention_volume_m3"] > 0 else np.nan
        )
        summaries.append(row)
    return pd.DataFrame(summaries)


def pareto_flag(df: pd.DataFrame) -> list[bool]:
    flags = []
    for _, r in df.iterrows():
        dominated = (
            (df["intervention_volume_m3"] <= r["intervention_volume_m3"])
            & (df["low_area_drop_h3_m2"] >= r["low_area_drop_h3_m2"])
            & (
                (df["intervention_volume_m3"] < r["intervention_volume_m3"])
                | (df["low_area_drop_h3_m2"] > r["low_area_drop_h3_m2"])
            )
        ).any()
        flags.append(not bool(dominated))
    return flags


def main():
    sensors = pd.read_csv(SENSOR_FILE)
    rows = []
    rows.extend(add_manifest_rows(BATCH_INITIAL / "run_manifest.csv", RESULTS / "100_HB_Radiance场景参数表.csv", "initial"))
    rows.extend(add_manifest_rows(BATCH_EXTRA / "run_manifest.csv", RESULTS / "125_HB_Radiance追加场景参数表.csv", "extra_top_pareto"))
    if (BATCH_FINAL_DESIGN / "run_manifest.csv").exists():
        rows.extend(
            add_manifest_rows(
                BATCH_FINAL_DESIGN / "run_manifest.csv",
                RESULTS / "136_HB_Radiance最终候选设计转译场景参数表.csv",
                "final_design",
            )
        )
    meta = pd.DataFrame(rows)
    # For duplicated scenario names, keep the extra run. It was generated from the preregistered Top/Pareto list.
    meta["scenario_priority"] = meta["source"].map({"extra_top_pareto": 1, "initial": 0})
    meta = meta.sort_values(["scenario", "scenario_priority"]).drop_duplicates("scenario", keep="last").drop(columns=["scenario_priority"])

    all_rows = []
    hourly_cols = [f"step_{i+1:02d}" for i in range(16)]
    for r in meta.itertuples(index=False):
        folder = Path(r.project_folder) / "direct_sun_hours" / "results"
        cumulative = folder / "cumulative" / f"{GRID_NAME}.res"
        hourly = folder / "direct_sun_hours" / f"{GRID_NAME}.ill"
        if not cumulative.exists():
            raise FileNotFoundError(cumulative)
        vals = np.array(read_values(cumulative), dtype=float)
        mat = read_matrix(hourly)
        if len(vals) != len(sensors) or mat.shape[0] != len(sensors):
            raise ValueError(f"{r.scenario}: sensor count mismatch")
        df = sensors.copy()
        df["scenario"] = r.scenario
        df["direct_sun_hours"] = vals
        for i, col in enumerate(hourly_cols):
            df[col] = mat[:, i] if i < mat.shape[1] else np.nan
        all_rows.append(df)
    raw = pd.concat(all_rows, ignore_index=True)
    raw.to_csv(RESULTS / "130_HB_Radiance合并原始点位结果.csv", index=False, encoding="utf-8-sig")

    summary = compute_summary(raw, meta)
    summary.to_csv(RESULTS / "131_HB_Radiance合并候选汇总结果.csv", index=False, encoding="utf-8-sig")

    rule = summary[(summary["pair_key"] != "") & (summary["model_type"] == "rule_flat")].copy()
    rule["canonical_scenario"] = rule["scenario"].map(is_canonical_rule_scenario)
    rule = rule.sort_values(["pair_key", "canonical_scenario", "source"], ascending=[True, False, True])
    rule = rule.drop_duplicates("pair_key", keep="first").copy()
    rule["is_hb_pareto_front"] = pareto_flag(rule)
    rule = rule.sort_values(["low_area_drop_h3_m2", "avg_gain_vs_baseline_h", "intervention_volume_m3"], ascending=[False, False, True]).reset_index(drop=True)
    rule["rank_hb_low_area_drop"] = np.arange(1, len(rule) + 1)

    two_d = pd.read_csv(RESULTS / "120_canonical_2p5D完整双建筑候选排名.csv")
    two_d["pair_key"] = two_d["building_ids"].map(pair_key)
    rule = rule.merge(
        two_d[
            [
                "pair_key",
                "rank_2p5d_score",
                "score",
                "low_area_drop_h3_m2",
                "avg_gain_vs_baseline_h",
                "is_pareto_front",
            ]
        ].rename(
            columns={
                "low_area_drop_h3_m2": "low_area_drop_h3_m2_2p5d",
                "avg_gain_vs_baseline_h": "avg_gain_vs_baseline_h_2p5d",
                "is_pareto_front": "is_2p5d_pareto_front",
            }
        ),
        on="pair_key",
        how="left",
    )
    rule["rank_2p5d_within_verified"] = rule["rank_2p5d_score"].rank(method="min").astype(int)
    if len(rule) > 1:
        rho, pval = spearmanr(rule["rank_2p5d_score"], rule["rank_hb_low_area_drop"], nan_policy="omit")
    else:
        rho, pval = np.nan, np.nan
    rule.to_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    ax.scatter(rule["intervention_volume_m3"], rule["low_area_drop_h3_m2"], s=26, alpha=0.65, label="已完成 HB 复核候选")
    front = rule[rule["is_hb_pareto_front"]]
    ax.scatter(front["intervention_volume_m3"], front["low_area_drop_h3_m2"], s=55, color="#e45756", label="HB-Radiance Pareto 前沿")
    for label in ["C6,C33", "C13,C24", "C9,C24", "C9,C15", "C9,C13", "C9,C29"]:
        sub = rule[rule["pair_key"] == label]
        if not sub.empty:
            r = sub.iloc[0]
            ax.text(r["intervention_volume_m3"], r["low_area_drop_h3_m2"], label, fontsize=8)
    ax.set_xlabel("干预体量 / m³")
    ax.set_ylabel("低直射日照区面积下降 / m²")
    ax.set_title("已复核候选的 HB-Radiance Pareto 分布")
    ax.grid(alpha=0.22)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "133_HB_Radiance_Top候选Pareto图.png")
    plt.close(fig)

    top = rule.head(15).sort_values("low_area_drop_h3_m2")
    fig, ax = plt.subplots(figsize=(9, 6), dpi=180)
    ax.barh(top["pair_key"], top["low_area_drop_h3_m2"], color="#4c78a8")
    ax.set_xlabel("低直射日照区面积下降 / m²")
    ax.set_title("HB-Radiance 已复核候选 Top15")
    ax.grid(axis="x", alpha=0.22)
    fig.tight_layout()
    fig.savefig(FIGURES / "134_HB_Radiance候选排序对比图.png")
    plt.close(fig)

    top_rows = rule.head(10)[
        [
            "pair_key",
            "rank_hb_low_area_drop",
            "low_area_drop_h3_m2",
            "avg_gain_vs_baseline_h",
            "intervention_volume_m3",
            "unit_low_area_drop_per_1000m3",
            "improved_point_count",
            "worsened_point_count",
            "new_low_area_h3_m2",
            "is_hb_pareto_front",
            "rank_2p5d_score",
            "is_2p5d_pareto_front",
        ]
    ]
    design = summary[summary["model_type"] == "design_stepback"][
        [
            "scenario",
            "pair_key",
            "low_area_drop_h3_m2",
            "avg_gain_vs_baseline_h",
            "intervention_volume_m3",
            "improved_point_count",
            "worsened_point_count",
            "new_low_area_h3_m2",
        ]
    ]
    md = [
        "# 135_HB-Radiance追加复核结论",
        "",
        "本轮合并了初始 7 个 HB-Radiance 场景与根据 2.5D Top10/非零 Pareto 预注册清单追加的 23 个规则候选场景。合并排名按建筑组合去重，重复组合优先采用追加批次的规范命名场景。",
        "",
        f"- 已复核规则候选组合数：{len(rule)}",
        f"- 2.5D 排名与 HB-Radiance 低日照面积下降排名 Spearman rho：{rho:.3f}，p={pval:.3g}",
        f"- HB-Radiance 低日照面积下降第一名：{rule.iloc[0]['pair_key']}，下降 {rule.iloc[0]['low_area_drop_h3_m2']:.1f} m²，体量 {rule.iloc[0]['intervention_volume_m3']:.1f} m³。",
        "",
        "## HB-Radiance Top10",
        "",
        top_rows.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## 设计转译模型复核",
        "",
        design.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## 判断",
        "",
        "C6/C33 在正式三维复核集合中收益很小，不能继续作为唯一推荐。C13/C24 在初始关键场景中成立，但追加复核显示，若只看 3 h 低直射日照区面积下降，多个 C9 相关候选的 HB-Radiance 收益更高。因此论文应写为“经正式三维复核的候选区间”，并将最终推荐限定在已完成 HB-Radiance 复核的候选集合内。",
        "",
        "图表说明：`133_HB_Radiance_Top候选Pareto图.png` 用于证明已复核候选在干预体量与低直射日照区面积下降之间的三维 Pareto 关系；`134_HB_Radiance候选排序对比图.png` 用于展示正式三维复核下的收益排序。",
    ]
    (DOCS / "135_HB-Radiance追加复核结论.md").write_text("\n".join(md), encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="collect_hb",
        inputs=[SENSOR_FILE, RESULTS / "120_canonical_2p5D完整双建筑候选排名.csv"],
        extra={"verified_rule_candidates": int(len(rule)), "spearman_rho": float(rho), "spearman_p": float(pval)},
    )

    print(rule.head(15)[["pair_key", "rank_hb_low_area_drop", "low_area_drop_h3_m2", "avg_gain_vs_baseline_h", "intervention_volume_m3", "is_hb_pareto_front", "rank_2p5d_score"]].to_string(index=False))
    print(json.dumps({"verified_rule_candidates": int(len(rule)), "spearman_rho": float(rho), "spearman_p": float(pval)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
