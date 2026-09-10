from __future__ import annotations

import itertools
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
from shapely.geometry import LineString, Point, shape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_runtime import load_runtime, write_run_metadata  # noqa: E402


RUNTIME = load_runtime()
ROOT = RUNTIME.run_dir
CANONICAL = ROOT / "canonical_site_v2"
RESULTS = RUNTIME.results_dir
FIGURES = RUNTIME.figures_dir
DOCS = RUNTIME.docs_dir

GRID_CSV = RESULTS / "100_HB_Radiance传感点.csv"
BUILDINGS_CSV = CANONICAL / "canonical_buildings.csv"
GEOJSON = CANONICAL / "canonical_site_v2.geojson"

SENSOR_HEIGHT_M = RUNTIME.sensor_height_m
LOW_THRESHOLD_H = RUNTIME.low_threshold_h
CELL_AREA_M2 = RUNTIME.grid_size_m ** 2
RANDOM_SEED = RUNTIME.seed

plt.rcParams["axes.unicode_minus"] = False


def boolish(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def reduced_height(height_m: float) -> float:
    return max(3.0, height_m - min(3.0, height_m * 0.25))


def solar_samples() -> pd.DataFrame:
    times = pd.date_range(
        f"{RUNTIME.analysis_date} {RUNTIME.start_time}",
        f"{RUNTIME.analysis_date} {RUNTIME.end_time}",
        freq=f"{RUNTIME.timestep_minutes}min",
        tz="Asia/Shanghai",
    )
    solar = pvlib.solarposition.get_solarposition(times, RUNTIME.latitude, RUNTIME.longitude)
    alt = solar["apparent_elevation"].to_numpy(float)
    az = solar["azimuth"].to_numpy(float)
    return pd.DataFrame(
        {
            "time": [t.isoformat() for t in times],
            "apparent_elevation_deg": alt,
            "azimuth_deg": az,
            "dx": np.sin(np.radians(az)),
            "dy": np.cos(np.radians(az)),
            "tan_altitude": np.tan(np.radians(alt)),
        }
    )


def load_geometries() -> dict[str, object]:
    data = json.loads(GEOJSON.read_text(encoding="utf-8"))
    out = {}
    for feature in data["features"]:
        bid = feature["properties"]["building_id"]
        out[bid] = shape(feature["geometry"])
    return out


def min_projected_distance(intersection, origin: Point, dx: float, dy: float) -> float | None:
    if intersection.is_empty:
        return None
    coords = []
    geom_type = intersection.geom_type
    if geom_type == "Point":
        coords = [(intersection.x, intersection.y)]
    elif geom_type == "MultiPoint":
        coords = [(g.x, g.y) for g in intersection.geoms]
    elif geom_type in {"LineString", "LinearRing"}:
        coords = list(intersection.coords)
    elif geom_type == "MultiLineString":
        for geom in intersection.geoms:
            coords.extend(list(geom.coords))
    elif geom_type == "GeometryCollection":
        distances = [min_projected_distance(g, origin, dx, dy) for g in intersection.geoms]
        distances = [d for d in distances if d is not None]
        return min(distances) if distances else None
    else:
        return None
    distances = []
    for x, y in coords:
        d = (x - origin.x) * dx + (y - origin.y) * dy
        if d > 1e-7:
            distances.append(d)
    return min(distances) if distances else None


def precompute_blockers(buildings: pd.DataFrame, grid: pd.DataFrame, geoms: dict[str, object], solar: pd.DataFrame):
    n_buildings = len(buildings)
    n_obs = len(grid) * len(solar)
    orig = np.zeros((n_buildings, n_obs), dtype=np.uint8)
    reduced = np.zeros((n_buildings, n_obs), dtype=np.uint8)

    minx, miny, maxx, maxy = geoms_unary_bounds(geoms)
    ray_len = math.hypot(maxx - minx, maxy - miny) + 100.0

    obs_index = 0
    for _, sensor in grid.iterrows():
        origin = Point(float(sensor["x"]), float(sensor["y"]))
        for _, sun in solar.iterrows():
            if float(sun["apparent_elevation_deg"]) <= 0:
                obs_index += 1
                continue
            dx, dy = float(sun["dx"]), float(sun["dy"])
            ray = LineString([(origin.x, origin.y), (origin.x + dx * ray_len, origin.y + dy * ray_len)])
            tan_alt = float(sun["tan_altitude"])
            for b_idx, b in enumerate(buildings.itertuples(index=False)):
                geom = geoms[b.building_id]
                if geom.contains(origin):
                    continue
                inter = ray.intersection(geom)
                horizontal_distance = min_projected_distance(inter, origin, dx, dy)
                if horizontal_distance is None:
                    continue
                ray_height = SENSOR_HEIGHT_M + tan_alt * horizontal_distance
                if ray_height <= float(b.height_m) + 1e-9:
                    orig[b_idx, obs_index] = 1
                if ray_height <= reduced_height(float(b.height_m)) + 1e-9:
                    reduced[b_idx, obs_index] = 1
            obs_index += 1
    return orig, reduced


def geoms_unary_bounds(geoms: dict[str, object]):
    bounds = np.array([g.bounds for g in geoms.values()], dtype=float)
    return bounds[:, 0].min(), bounds[:, 1].min(), bounds[:, 2].max(), bounds[:, 3].max()


def hours_from_blocked(blocked: np.ndarray, sensor_count: int, sun_count: int) -> np.ndarray:
    visible = (~blocked.reshape(sensor_count, sun_count)).sum(axis=1)
    return visible * 0.5


def low_area(hours: np.ndarray, threshold_h: float = LOW_THRESHOLD_H) -> float:
    return float((hours < threshold_h).sum() * CELL_AREA_M2)


def candidate_metrics():
    buildings = pd.read_csv(BUILDINGS_CSV)
    buildings["movable_bool"] = buildings["movable"].map(boolish)
    buildings["protected_bool"] = buildings["protected"].map(boolish)
    geoms = load_geometries()
    grid = pd.read_csv(GRID_CSV)
    solar = solar_samples()
    solar.to_csv(RESULTS / "100_统一太阳时刻表.csv", index=False, encoding="utf-8-sig")

    legal = buildings[(buildings["movable_bool"]) & (~buildings["protected_bool"])].copy()
    legal = legal[legal["height_m"].astype(float) > 3.0].copy()
    legal_ids = legal["building_id"].tolist()

    orig, reduced = precompute_blockers(buildings, grid, geoms, solar)
    base_count = orig.sum(axis=0).astype(np.int16)
    baseline_blocked = base_count > 0
    baseline_hours = hours_from_blocked(baseline_blocked, len(grid), len(solar))
    baseline_low = low_area(baseline_hours)
    baseline_mean = float(baseline_hours.mean())

    idx_by_id = {bid: idx for idx, bid in enumerate(buildings["building_id"].tolist())}
    rows = []
    point_rows = []
    pair_no = 1
    for a, b in itertools.combinations(legal_ids, 2):
        ia, ib = idx_by_id[a], idx_by_id[b]
        blocked_count = base_count - orig[ia] - orig[ib] + reduced[ia] + reduced[ib]
        blocked = blocked_count > 0
        hours = hours_from_blocked(blocked, len(grid), len(solar))
        delta = hours - baseline_hours
        a_row = buildings.iloc[ia]
        b_row = buildings.iloc[ib]
        vol_a = float(a_row["canonical_area_m2"]) * (float(a_row["height_m"]) - reduced_height(float(a_row["height_m"])))
        vol_b = float(b_row["canonical_area_m2"]) * (float(b_row["height_m"]) - reduced_height(float(b_row["height_m"])))
        low = low_area(hours)
        low_drop = baseline_low - low
        new_low = float(((baseline_hours >= LOW_THRESHOLD_H) & (hours < LOW_THRESHOLD_H)).sum() * CELL_AREA_M2)
        rows.append(
            {
                "candidate_id": f"P{pair_no:03d}",
                "building_ids": f"{a},{b}",
                "operation_type": "双建筑整体减高",
                "height_rule": "new_h=max(3m, h-min(3m, 25%h))",
                "original_heights_m": f"{float(a_row['height_m']):.3f},{float(b_row['height_m']):.3f}",
                "modified_heights_m": f"{reduced_height(float(a_row['height_m'])):.3f},{reduced_height(float(b_row['height_m'])):.3f}",
                "intervention_volume_m3": vol_a + vol_b,
                "mean_direct_sun_hours": float(hours.mean()),
                "avg_gain_vs_baseline_h": float(delta.mean()),
                "low_area_h3_m2": low,
                "low_area_drop_h3_m2": low_drop,
                "new_low_area_h3_m2": new_low,
                "improved_point_count": int((delta > 1e-9).sum()),
                "worsened_point_count": int((delta < -1e-9).sum()),
                "unit_low_area_drop_per_1000m3": float(low_drop / (vol_a + vol_b) * 1000) if vol_a + vol_b > 0 else 0.0,
            }
        )
        pair_no += 1

    df = pd.DataFrame(rows)
    # Conservative scoring is only for pre-screening: low-area drop first, then lower new low area, then smaller volume.
    for col in ["low_area_drop_h3_m2", "avg_gain_vs_baseline_h", "intervention_volume_m3", "new_low_area_h3_m2"]:
        lo, hi = df[col].min(), df[col].max()
        if abs(hi - lo) < 1e-12:
            df[f"{col}_norm"] = 0.0
        else:
            df[f"{col}_norm"] = (df[col] - lo) / (hi - lo)
    df["score"] = (
        0.45 * df["low_area_drop_h3_m2_norm"]
        + 0.35 * df["avg_gain_vs_baseline_h_norm"]
        + 0.15 * (1 - df["intervention_volume_m3_norm"])
        + 0.05 * (1 - df["new_low_area_h3_m2_norm"])
    )

    pareto = []
    for i, r in df.iterrows():
        dominated = (
            (df["intervention_volume_m3"] <= r["intervention_volume_m3"])
            & (df["low_area_drop_h3_m2"] >= r["low_area_drop_h3_m2"])
            & (
                (df["intervention_volume_m3"] < r["intervention_volume_m3"])
                | (df["low_area_drop_h3_m2"] > r["low_area_drop_h3_m2"])
            )
        ).any()
        pareto.append(not bool(dominated))
    df["is_pareto_front"] = pareto
    df = df.sort_values(["score", "low_area_drop_h3_m2", "avg_gain_vs_baseline_h"], ascending=[False, False, False]).reset_index(drop=True)
    df["rank_2p5d_score"] = np.arange(1, len(df) + 1)

    top10 = df[(df["low_area_drop_h3_m2"] > 0)].head(10).copy()
    pareto_nonzero = df[(df["is_pareto_front"]) & (df["low_area_drop_h3_m2"] > 0)].copy()
    must_hb = pd.concat([top10, pareto_nonzero, df[df["building_ids"].isin(["C6,C33", "C13,C24", "C3,C19", "C26,C35"])]], ignore_index=True)
    must_hb = must_hb.drop_duplicates(subset=["building_ids"]).sort_values(["rank_2p5d_score", "building_ids"]).reset_index(drop=True)

    df.to_csv(RESULTS / "120_canonical_2p5D完整双建筑候选排名.csv", index=False, encoding="utf-8-sig")
    top10.to_csv(RESULTS / "121_canonical_2p5D_Top10候选.csv", index=False, encoding="utf-8-sig")
    pareto_nonzero.to_csv(RESULTS / "122_canonical_2p5D_非零Pareto候选.csv", index=False, encoding="utf-8-sig")
    must_hb.to_csv(RESULTS / "123_需追加HB_Radiance复核候选清单.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8, 5), dpi=180)
    ax.scatter(df["intervention_volume_m3"], df["low_area_drop_h3_m2"], s=10, alpha=0.35, label="全部合法双建筑候选")
    p = df[df["is_pareto_front"]]
    ax.scatter(p["intervention_volume_m3"], p["low_area_drop_h3_m2"], s=24, color="#e45756", label="2.5D Pareto 前沿")
    for label in ["C6,C33", "C13,C24", "C3,C19", "C26,C35"]:
        sub = df[df["building_ids"] == label]
        if not sub.empty:
            ax.scatter(sub["intervention_volume_m3"], sub["low_area_drop_h3_m2"], s=70, edgecolor="black", facecolor="none")
            ax.text(float(sub.iloc[0]["intervention_volume_m3"]), float(sub.iloc[0]["low_area_drop_h3_m2"]), label, fontsize=8)
    ax.set_xlabel("干预体量 / m³")
    ax.set_ylabel("低直射日照区面积下降 / m²")
    ax.set_title("canonical_site_v2 规则模型候选分布")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "124_canonical_2p5D候选Pareto图.png")
    plt.close(fig)

    summary = {
        "generated_candidate_count": int(len(df)),
        "legal_building_count": int(len(legal_ids)),
        "baseline_low_area_h3_m2": baseline_low,
        "baseline_mean_direct_sun_hours": baseline_mean,
        "top10_count": int(len(top10)),
        "pareto_nonzero_count": int(len(pareto_nonzero)),
        "must_hb_unique_count": int(len(must_hb)),
        "random_seed_for_future_sampling": RANDOM_SEED,
    }
    (ROOT / "logs" / "120_canonical_2p5D_candidate_enumeration_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# 120_canonical_2p5D候选枚举说明",
        "",
        "本轮基于 `canonical_site_v2`、HB-Radiance 同一 3 m 传感点和同一冬至 08:15-15:45、30 分钟时刻表，枚举合法双建筑整体减高候选。",
        "",
        "评分仅用于 2.5D 初筛，不作为最终推荐依据。最终候选必须以 HB-Radiance 正式三维复核结果为更高证据等级。",
        "",
        f"- 合法可减高建筑数：{len(legal_ids)}",
        f"- 双建筑候选数：{len(df)}",
        f"- 现状 3 h 阈值低直射日照区面积：{baseline_low:.1f} m²",
        f"- 非零 Top10 数：{len(top10)}",
        f"- 非零 Pareto 候选数：{len(pareto_nonzero)}",
        f"- 需追加 HB-Radiance 复核的去重候选数：{len(must_hb)}",
        "",
        "图表说明：`124_canonical_2p5D候选Pareto图.png` 用于证明规则模型中候选收益与干预体量之间的初筛分布，并标出 C6/C33、C13/C24 及公平基线位置。",
    ]
    (DOCS / "120_canonical_2p5D候选枚举说明.md").write_text("\n".join(md), encoding="utf-8")
    write_run_metadata(
        RUNTIME,
        stage="enumerate_2p5d",
        inputs=[BUILDINGS_CSV, GEOJSON, GRID_CSV],
        extra={
            "eligible_building_count": len(legal_ids),
            "candidate_count": len(df),
            "cell_area_m2": CELL_AREA_M2,
            "seed": RANDOM_SEED,
        },
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(must_hb[["building_ids", "rank_2p5d_score", "low_area_drop_h3_m2", "intervention_volume_m3", "is_pareto_front"]].to_string(index=False))


if __name__ == "__main__":
    candidate_metrics()
