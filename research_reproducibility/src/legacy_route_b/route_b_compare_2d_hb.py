from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib
from scipy.stats import pearsonr, spearmanr
from shapely.geometry import shape
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, strict_bool, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
RESULTS = RUNTIME.results_dir
FIGURES = RUNTIME.figures_dir
DOCS = RUNTIME.docs_dir
CANONICAL = ROOT / "canonical_site_v2"


plt.rcParams["axes.unicode_minus"] = False


SCENARIO_PAIRS = {
    "baseline": (),
    "C6_C33_rule_flat": ("C6", "C33"),
    "C13_C24_rule_flat": ("C13", "C24"),
    "height_priority_C3_C19": ("C3", "C19"),
    "low_sun_nearest_C26_C35": ("C26", "C35"),
}


def reduced_height(h):
    """Apply the same configured height rule as production screening."""

    return RUNTIME.reduced_height(h)


def solar_samples():
    times = pd.date_range(
        f"{RUNTIME.analysis_date} {RUNTIME.start_time}",
        f"{RUNTIME.analysis_date} {RUNTIME.end_time}",
        freq=f"{RUNTIME.timestep_minutes}min",
        tz=RUNTIME.timezone,
    )
    solar = pvlib.solarposition.get_solarposition(times, RUNTIME.latitude, RUNTIME.longitude)
    alt = solar["apparent_elevation"].to_numpy(float)
    az = solar["azimuth"].to_numpy(float)
    alt_r = np.radians(alt)
    az_r = np.radians(az)
    return pd.DataFrame(
        {
            "time": times.astype(str),
            "altitude_deg": alt,
            "azimuth_deg": az,
            "vx": np.cos(alt_r) * np.sin(az_r),
            "vy": np.cos(alt_r) * np.cos(az_r),
            "vz": np.sin(alt_r),
            "weight_h": RUNTIME.timestep_hours,
            "active": alt > 1.0,
        }
    )


def load_building_bounds():
    buildings = pd.read_csv(CANONICAL / "canonical_buildings.csv")
    geo = json.loads((CANONICAL / "canonical_site_v2.geojson").read_text(encoding="utf-8"))
    bounds = {}
    for feat in geo["features"]:
        bid = feat["properties"]["building_id"]
        geom = shape(feat["geometry"])
        bounds[bid] = geom.bounds
    rows = []
    for _, row in buildings.iterrows():
        bid = row.building_id
        minx, miny, maxx, maxy = bounds[bid]
        rows.append(
            {
                "building_id": bid,
                "x_min": minx,
                "x_max": maxx,
                "y_min": miny,
                "y_max": maxy,
                "height_m": float(row.height_m),
                "movable": strict_bool(row.movable, field=f"{bid}.movable"),
                "protected": strict_bool(row.protected, field=f"{bid}.protected"),
            }
        )
    return pd.DataFrame(rows)


def precompute_required(points, buildings, samples):
    px = points["x"].to_numpy(float)
    py = points["y"].to_numpy(float)
    pz = points["z"].to_numpy(float)
    bx0 = buildings["x_min"].to_numpy(float)
    bx1 = buildings["x_max"].to_numpy(float)
    by0 = buildings["y_min"].to_numpy(float)
    by1 = buildings["y_max"].to_numpy(float)
    required = np.full((len(samples), len(points), len(buildings)), np.inf, dtype=np.float32)
    for s_idx, s in enumerate(samples.itertuples(index=False)):
        if not bool(s.active) or float(s.vz) <= 0:
            continue
        vx, vy, vz = float(s.vx), float(s.vy), float(s.vz)
        for b_idx in range(len(buildings)):
            if abs(vx) < 1e-12:
                inside_x = (px >= bx0[b_idx]) & (px <= bx1[b_idx])
                tmin_x = np.where(inside_x, -np.inf, np.inf)
                tmax_x = np.where(inside_x, np.inf, -np.inf)
            else:
                tx1 = (bx0[b_idx] - px) / vx
                tx2 = (bx1[b_idx] - px) / vx
                tmin_x = np.minimum(tx1, tx2)
                tmax_x = np.maximum(tx1, tx2)
            if abs(vy) < 1e-12:
                inside_y = (py >= by0[b_idx]) & (py <= by1[b_idx])
                tmin_y = np.where(inside_y, -np.inf, np.inf)
                tmax_y = np.where(inside_y, np.inf, -np.inf)
            else:
                ty1 = (by0[b_idx] - py) / vy
                ty2 = (by1[b_idx] - py) / vy
                tmin_y = np.minimum(ty1, ty2)
                tmax_y = np.maximum(ty1, ty2)
            t_enter = np.maximum(tmin_x, tmin_y)
            t_exit = np.minimum(tmax_x, tmax_y)
            hit = (t_exit >= np.maximum(t_enter, 1e-6))
            req_h = pz + np.maximum(t_enter, 1e-6) * vz
            required[s_idx, :, b_idx] = np.where(hit, req_h, np.inf)
    return required


def hours_for_heights(required, heights, samples):
    blocked = required < heights.reshape(1, 1, -1)
    sun_blocked = blocked.any(axis=2)
    weights = samples["weight_h"].to_numpy(float).reshape(-1, 1)
    active = samples["active"].to_numpy(bool).reshape(-1, 1)
    return ((~sun_blocked) & active).astype(float).T.dot(weights).ravel()


def classification_metrics(a, b, th):
    pred = a < th
    true = b < th
    tp = int((pred & true).sum())
    tn = int((~pred & ~true).sum())
    fp = int((pred & ~true).sum())
    fn = int((~pred & true).sum())
    acc = (tp + tn) / len(a)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return acc, prec, rec, f1


def corr(x, y, method):
    try:
        return float((pearsonr if method == "pearson" else spearmanr)(x, y).statistic)
    except Exception:
        return float("nan")


def main():
    points = pd.read_csv(RESULTS / "100_HB_Radiance传感点.csv")
    hb_path = RESULTS / "101_HB_Radiance原始点位结果.csv"
    if not hb_path.exists():
        hb_path = RESULTS / "130_HB_Radiance合并原始点位结果.csv"
    hb = pd.read_csv(hb_path)
    buildings = load_building_bounds()
    samples = solar_samples()
    samples.to_csv(RESULTS / "100_统一太阳时刻表.csv", index=False, encoding="utf-8-sig")
    req = precompute_required(points, buildings, samples)
    ids = list(buildings["building_id"])
    base_heights = buildings["height_m"].to_numpy(float)
    rows = []
    point_rows = []
    for scenario, pair in SCENARIO_PAIRS.items():
        heights = base_heights.copy()
        for bid in pair:
            heights[ids.index(bid)] = reduced_height(heights[ids.index(bid)])
        h2d = hours_for_heights(req, heights, samples)
        s_points = points.copy()
        s_points["scenario"] = scenario
        s_points["python_2p5d_hours"] = h2d
        point_rows.append(s_points)
    pred_df = pd.concat(point_rows, ignore_index=True)
    pred_df.to_csv(RESULTS / "routeB_canonical_2p5D_point_results.csv", index=False, encoding="utf-8-sig")
    merged = hb.merge(pred_df[["grid_id", "scenario", "python_2p5d_hours"]], on=["grid_id", "scenario"], how="inner")
    for scenario, sub in merged.groupby("scenario", sort=False):
        a = sub["python_2p5d_hours"].to_numpy(float)
        b = sub["direct_sun_hours"].to_numpy(float)
        for th in [2.0, 3.0, 4.0]:
            acc, prec, rec, f1 = classification_metrics(a, b, th)
            rows.append(
                {
                    "scenario": scenario,
                    "threshold_h": th,
                    "MAE": float(np.mean(np.abs(a - b))),
                    "RMSE": float(np.sqrt(np.mean((a - b) ** 2))),
                    "Pearson": corr(a, b, "pearson"),
                    "Spearman": corr(a, b, "spearman"),
                    "Accuracy": acc,
                    "Precision": prec,
                    "Recall": rec,
                    "F1": f1,
                    "python_low_area_m2": float((a < th).sum() * RUNTIME.grid_size_m ** 2),
                    "hb_low_area_m2": float((b < th).sum() * RUNTIME.grid_size_m ** 2),
                }
            )
    pd.DataFrame(rows).to_csv(RESULTS / "109_点位验证指标.csv", index=False, encoding="utf-8-sig")

    base_hb = hb[hb["scenario"] == "baseline"].set_index("grid_id")["direct_sun_hours"]
    base_2d = pred_df[pred_df["scenario"] == "baseline"].set_index("grid_id")["python_2p5d_hours"]
    rank_rows = []
    for scenario in SCENARIO_PAIRS:
        if scenario == "baseline":
            continue
        hb_s = hb[hb["scenario"] == scenario].set_index("grid_id")["direct_sun_hours"]
        py_s = pred_df[pred_df["scenario"] == scenario].set_index("grid_id")["python_2p5d_hours"]
        rank_rows.append(
            {
                "scenario": scenario,
                "python_low_area_drop_h3_m2": float(((base_2d < RUNTIME.low_threshold_h).sum() - (py_s < RUNTIME.low_threshold_h).sum()) * RUNTIME.grid_size_m ** 2),
                "hb_low_area_drop_h3_m2": float(((base_hb < RUNTIME.low_threshold_h).sum() - (hb_s < RUNTIME.low_threshold_h).sum()) * RUNTIME.grid_size_m ** 2),
                "python_avg_gain_h": float((py_s - base_2d).mean()),
                "hb_avg_gain_h": float((hb_s - base_hb).mean()),
                "direction_consistency_all_points": float(np.mean(np.sign(py_s - base_2d) == np.sign(hb_s - base_hb))),
                "direction_consistency_changed_points": float(
                    np.mean(
                        (np.sign(py_s - base_2d) == np.sign(hb_s - base_hb))[
                            ((py_s - base_2d) != 0) | ((hb_s - base_hb) != 0)
                        ]
                    )
                ),
            }
        )
    rank = pd.DataFrame(rank_rows)
    rank["python_rank"] = rank["python_low_area_drop_h3_m2"].rank(ascending=False, method="min")
    rank["hb_rank"] = rank["hb_low_area_drop_h3_m2"].rank(ascending=False, method="min")
    rank.to_csv(RESULTS / "110_候选排名一致性.csv", index=False, encoding="utf-8-sig")
    topk = []
    for k in [1, 2, 3]:
        py_top = set(rank.nsmallest(k, "python_rank")["scenario"])
        hb_top = set(rank.nsmallest(k, "hb_rank")["scenario"])
        topk.append({"K": k, "topK_overlap_count": len(py_top & hb_top), "topK_recall": len(py_top & hb_top) / k})
    pd.DataFrame(topk).to_csv(RESULTS / "111_TopK召回与Pareto重叠.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=180)
    axes[0].scatter(merged["python_2p5d_hours"], merged["direct_sun_hours"], s=4, alpha=0.25)
    axes[0].set_xlabel("Python 2.5D / h")
    axes[0].set_ylabel("HB-Radiance / h")
    axes[0].set_title("点位层面时长对比")
    axes[0].grid(alpha=0.2)
    axes[1].scatter(rank["python_low_area_drop_h3_m2"], rank["hb_low_area_drop_h3_m2"], s=60)
    for _, r in rank.iterrows():
        axes[1].text(r["python_low_area_drop_h3_m2"], r["hb_low_area_drop_h3_m2"], r["scenario"], fontsize=7)
    axes[1].set_xlabel("2.5D 低日照面积下降 / m²")
    axes[1].set_ylabel("HB-Radiance 低日照面积下降 / m²")
    axes[1].set_title("候选层面分歧")
    axes[1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "113_模型分歧图组.png")
    plt.close(fig)

    md = [
        "# 112_模型分歧空间解释",
        "",
        "本轮比较使用同一 `canonical_site_v2`、同一 3 m 传感点、同一冬至 08:15-15:45 30 分钟时刻表。Python 2.5D 使用建筑平面 bbox 的竖向挤出遮挡近似；HB-Radiance 使用 Honeybee/LBT direct-sun-hours recipe 与 Radiance 6.0.2。",
        "",
        "## 候选层面排序",
        "",
        rank.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## 解释",
        "",
        "若 2.5D 与 HB-Radiance 在候选收益排序上不完全一致，应优先采用 HB-Radiance 作为更高证据等级；2.5D 可保留为早期筛查和候选缩小工具，而不能单独决定唯一方案。",
    ]
    (DOCS / "112_模型分歧空间解释.md").write_text("\n".join(md), encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="compare_2d_hb",
        inputs=[hb_path, RESULTS / "100_HB_Radiance传感点.csv"],
        extra={"scenario_count": len(SCENARIO_PAIRS) - 1},
    )
    print(rank.to_string(index=False))


if __name__ == "__main__":
    main()
