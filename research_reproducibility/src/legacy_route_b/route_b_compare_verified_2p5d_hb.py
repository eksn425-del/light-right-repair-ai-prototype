from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
CODE = Path(__file__).resolve().parent
CANONICAL = ROOT / "canonical_site_v2"
RESULTS = RUNTIME.results_dir
FIGURES = RUNTIME.figures_dir
DOCS = RUNTIME.docs_dir

sys.path.insert(0, str(CODE))
from route_b_enumerate_2p5d_candidates import (  # noqa: E402
    hours_from_blocked,
    load_geometries,
    precompute_blockers,
    reduced_height,
    solar_samples,
)

plt.rcParams["axes.unicode_minus"] = False


def classification_metrics(pred_low: np.ndarray, true_low: np.ndarray) -> dict:
    tp = int((pred_low & true_low).sum())
    tn = int((~pred_low & ~true_low).sum())
    fp = int((pred_low & ~true_low).sum())
    fn = int((~pred_low & true_low).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "Accuracy": (tp + tn) / (tp + tn + fp + fn),
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
    }


def pair_to_ids(pair: str) -> tuple[str, str]:
    a, b = [p.strip() for p in str(pair).split(",")]
    return a, b


def main():
    buildings = pd.read_csv(CANONICAL / "canonical_buildings.csv")
    geoms = load_geometries()
    grid = pd.read_csv(RESULTS / "100_HB_Radiance传感点.csv")
    solar = solar_samples()
    orig, reduced = precompute_blockers(buildings, grid, geoms, solar)
    base_count = orig.sum(axis=0).astype(np.int16)
    py_baseline = hours_from_blocked(base_count > 0, len(grid), len(solar))

    idx_by_id = {bid: idx for idx, bid in enumerate(buildings["building_id"].tolist())}
    verified = pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv")
    hb_raw = pd.read_csv(RESULTS / "130_HB_Radiance合并原始点位结果.csv")
    hb_base = hb_raw[hb_raw["scenario"] == "baseline"].sort_values("grid_id")["direct_sun_hours"].to_numpy(float)

    point_rows = []
    metric_rows = []
    rank_rows = []
    for row in verified.itertuples(index=False):
        a, b = pair_to_ids(row.pair_key)
        ia, ib = idx_by_id[a], idx_by_id[b]
        blocked_count = base_count - orig[ia] - orig[ib] + reduced[ia] + reduced[ib]
        py_hours = hours_from_blocked(blocked_count > 0, len(grid), len(solar))
        hb = hb_raw[hb_raw["scenario"] == row.scenario].sort_values("grid_id")
        hb_hours = hb["direct_sun_hours"].to_numpy(float)
        delta_py = py_hours - py_baseline
        delta_hb = hb_hours - hb_base
        changed = (np.abs(delta_py) > 1e-9) | (np.abs(delta_hb) > 1e-9)
        direction_all = float((np.sign(delta_py) == np.sign(delta_hb)).mean())
        direction_changed = float((np.sign(delta_py[changed]) == np.sign(delta_hb[changed])).mean()) if changed.any() else 1.0
        rank_rows.append(
            {
                "pair_key": row.pair_key,
                "scenario": row.scenario,
                "python_low_area_drop_h3_m2": float(((py_baseline < RUNTIME.low_threshold_h).sum() - (py_hours < RUNTIME.low_threshold_h).sum()) * RUNTIME.grid_size_m ** 2),
                "hb_low_area_drop_h3_m2": row.low_area_drop_h3_m2,
                "python_avg_gain_h": float(delta_py.mean()),
                "hb_avg_gain_h": row.avg_gain_vs_baseline_h,
                "direction_consistency_all_points": direction_all,
                "direction_consistency_changed_points": direction_changed,
                "rank_2p5d_score": row.rank_2p5d_score,
                "rank_hb_low_area_drop": row.rank_hb_low_area_drop,
                "is_2p5d_pareto_front": row.is_2p5d_pareto_front,
                "is_hb_pareto_front": row.is_hb_pareto_front,
            }
        )
        for threshold in [2.0, RUNTIME.low_threshold_h, 4.0]:
            diff = py_hours - hb_hours
            cls = classification_metrics(py_hours < threshold, hb_hours < threshold)
            metric_rows.append(
                {
                    "pair_key": row.pair_key,
                    "scenario": row.scenario,
                    "threshold_h": threshold,
                    "MAE": float(np.mean(np.abs(diff))),
                    "RMSE": float(np.sqrt(np.mean(diff**2))),
                    "Pearson": float(pearsonr(py_hours, hb_hours)[0]),
                    "Spearman": float(spearmanr(py_hours, hb_hours).correlation),
                    "python_low_area_m2": float((py_hours < threshold).sum() * RUNTIME.grid_size_m ** 2),
                    "hb_low_area_m2": float((hb_hours < threshold).sum() * RUNTIME.grid_size_m ** 2),
                    **cls,
                }
            )
        pts = grid[["grid_id", "x", "y", "z"]].copy()
        pts["pair_key"] = row.pair_key
        pts["scenario"] = row.scenario
        pts["python_2p5d_hours"] = py_hours
        pts["hb_radiance_hours"] = hb_hours
        pts["hour_error_python_minus_hb"] = py_hours - hb_hours
        pts["delta_python"] = delta_py
        pts["delta_hb"] = delta_hb
        point_rows.append(pts)

    point_df = pd.concat(point_rows, ignore_index=True)
    metrics = pd.DataFrame(metric_rows)
    ranks = pd.DataFrame(rank_rows).sort_values("rank_hb_low_area_drop")

    topk = []
    for k in [3, 5, 10]:
        py_top = set(ranks.nsmallest(k, "rank_2p5d_score")["pair_key"])
        hb_top = set(ranks.nsmallest(k, "rank_hb_low_area_drop")["pair_key"])
        topk.append({"K": k, "topK_overlap_count": len(py_top & hb_top), "topK_recall": len(py_top & hb_top) / k})
    py_pareto = set(ranks[ranks["is_2p5d_pareto_front"] == True]["pair_key"])
    hb_pareto = set(ranks[ranks["is_hb_pareto_front"] == True]["pair_key"])
    topk.append(
        {
            "K": "Pareto",
            "topK_overlap_count": len(py_pareto & hb_pareto),
            "topK_recall": len(py_pareto & hb_pareto) / len(hb_pareto) if hb_pareto else np.nan,
        }
    )

    point_df.to_csv(RESULTS / "141_已复核候选Python与HB点位对齐结果.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(RESULTS / "142_已复核候选点位验证指标.csv", index=False, encoding="utf-8-sig")
    ranks.to_csv(RESULTS / "143_已复核候选排名一致性.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(topk).to_csv(RESULTS / "144_已复核TopK召回与Pareto重叠.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=180)
    sample = point_df.sample(min(20000, len(point_df)), random_state=RUNTIME.seed)
    axes[0].scatter(sample["python_2p5d_hours"], sample["hb_radiance_hours"], s=3, alpha=0.2)
    axes[0].plot([0, 8], [0, 8], color="black", linewidth=1)
    axes[0].set_xlabel("Python 2.5D / h")
    axes[0].set_ylabel("HB-Radiance / h")
    axes[0].set_title("点位直射日照时长对比")
    axes[1].scatter(ranks["python_low_area_drop_h3_m2"], ranks["hb_low_area_drop_h3_m2"], s=35)
    for _, r in ranks.head(10).iterrows():
        axes[1].text(r["python_low_area_drop_h3_m2"], r["hb_low_area_drop_h3_m2"], r["pair_key"], fontsize=8)
    axes[1].set_xlabel("2.5D 低日照面积下降 / m²")
    axes[1].set_ylabel("HB-Radiance 低日照面积下降 / m²")
    axes[1].set_title("已复核候选收益对比")
    for ax in axes:
        ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(FIGURES / "145_已复核模型分歧图组.png")
    plt.close(fig)

    rho, pval = spearmanr(ranks["rank_2p5d_score"], ranks["rank_hb_low_area_drop"])
    md = [
        "# 146_已复核模型分歧空间解释",
        "",
        "本文件基于 23 个已完成 HB-Radiance 复核的规则候选，重新评估 Python 2.5D 与正式三维参考结果的一致性。",
        "",
        f"- 候选排名 Spearman rho：{rho:.3f}，p={pval:.3g}",
        f"- HB Pareto 候选数：{len(hb_pareto)}",
        f"- 2.5D/HB Pareto 重叠数：{len(py_pareto & hb_pareto)}",
        "",
        "## Top-K 与 Pareto 重叠",
        "",
        pd.DataFrame(topk).to_markdown(index=False),
        "",
        "## 解释",
        "",
        "2.5D 与 HB-Radiance 在已复核候选集合中的排序相关性较高，说明规则模型可用于早期缩小候选范围。但点位层面仍存在系统误差，且 C9/C29、C9/C25 等低体量候选在 2.5D 总分排序中靠后但进入 HB Pareto，因此论文不得宣称 2.5D 可自动给出唯一最优方案。",
        "",
        "图表说明：`145_已复核模型分歧图组.png` 用于证明 2.5D 与 HB-Radiance 在空间诊断和候选收益排序上总体一致但仍有局部分歧。",
    ]
    (DOCS / "146_已复核模型分歧空间解释.md").write_text("\n".join(md), encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="compare_verified_2p5d_hb",
        inputs=[RESULTS / "130_HB_Radiance合并原始点位结果.csv", RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv"],
        extra={"verified_candidate_count": int(len(ranks)), "rank_spearman_rho": float(rho), "rank_spearman_p": float(pval)},
    )
    print(ranks[["pair_key", "python_low_area_drop_h3_m2", "hb_low_area_drop_h3_m2", "rank_2p5d_score", "rank_hb_low_area_drop"]].head(12).to_string(index=False))
    print(json.dumps({"rank_spearman_rho": float(rho), "rank_spearman_p": float(pval)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
