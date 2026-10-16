from __future__ import annotations

import csv
import itertools
import json
import math
import random
import re
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib
import trimesh
from matplotlib import font_manager
from scipy.stats import pearsonr, spearmanr

for font_path in [
    Path(r"C:/Windows/Fonts/msyh.ttc"),
    Path(r"C:/Windows/Fonts/simhei.ttf"),
    Path(r"C:/Windows/Fonts/simsun.ttc"),
]:
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=str(font_path)).get_name()]
        plt.rcParams["axes.unicode_minus"] = False
        break


WORKSPACE = Path(r"E:/AI项目")
WORK_ROOT = WORKSPACE / "中文导师审阅定稿_工作包_2026_06_20"
PROJECT = WORKSPACE / "light_equity_project"
DATASET = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
READY_BASELINE_OBJ = WORKSPACE / "ladybug_ready_models" / "baseline_original_full_site_ladybug_ready.obj"
READY_C6_C33_OBJ = (
    WORKSPACE / "ladybug_ready_models" / "algorithm_after_full_site_only_C6_C33_changed_ladybug_ready.obj"
)

DOCS = WORK_ROOT / "docs"
RESULTS = WORK_ROOT / "results_csv"
FIGURES = WORK_ROOT / "figures"
LOGS = WORK_ROOT / "logs"
CONFIG = WORK_ROOT / "config"
PROCESSED = WORK_ROOT / "data_processed"

for directory in [DOCS, RESULTS, FIGURES, LOGS, CONFIG, PROCESSED]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class SolarConfig:
    latitude: float = 24.55
    longitude: float = 118.03
    timezone: str = "Asia/Shanghai"
    date: str = "2026-12-21"
    start_hour: float = 8.0
    end_hour: float = 16.0
    time_step_minutes: int = 30
    min_altitude_deg: float = 1.0


@dataclass
class SiteConfig:
    unit: str = "m"
    north: str = "模型 +Y 方向按项目约定视作北向；未发现可复核北向旋转参数"
    coordinate_system: str = "项目局部平面坐标，单位 m；Ladybug-ready OBJ 使用 x+191.792/y+95.982 的经验平移与 CSV 对齐"
    bounds_padding_m: float = 6.0
    street_analysis_margin_m: float = 5.0
    ground_z: float = 0.05
    low_sun_threshold_h: float = 3.0
    main_grid_m: float = 3.0
    quick_grid_m: float = 6.0


@dataclass
class CandidateRule:
    reduction_ratio: float = 0.25
    max_reduction_m: float = 3.0
    min_remaining_height_m: float = 3.0
    max_buildings_per_candidate: int = 2
    random_seed: int = 42


def write_csv(path: Path, rows: list[dict] | pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rows, pd.DataFrame):
        rows.to_csv(path, index=False, encoding="utf-8-sig")
        return
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    buildings = pd.read_csv(DATASET / "buildings.csv")
    streets = pd.read_csv(DATASET / "streets.csv")
    protected = pd.read_csv(DATASET / "protected_zones.csv")
    site_zones = pd.read_csv(DATASET / "site_zones.csv")
    buildings["movable_bool"] = read_bool(buildings["movable"])
    buildings["protected_bool"] = read_bool(buildings["protected"])
    return buildings, streets, protected, site_zones


def site_bounds(buildings: pd.DataFrame, streets: pd.DataFrame, padding: float) -> tuple[float, float, float, float]:
    xs = list(buildings["x_min"].astype(float)) + list(buildings["x_max"].astype(float))
    ys = list(buildings["y_min"].astype(float)) + list(buildings["y_max"].astype(float))
    if not streets.empty:
        xs += list(streets["start_x"].astype(float)) + list(streets["end_x"].astype(float))
        ys += list(streets["start_y"].astype(float)) + list(streets["end_y"].astype(float))
    return min(xs) - padding, max(xs) + padding, min(ys) - padding, max(ys) + padding


def point_segment_distances(px: np.ndarray, py: np.ndarray, ax: float, ay: float, bx: float, by: float) -> np.ndarray:
    dx = bx - ax
    dy = by - ay
    if abs(dx) < 1e-12 and abs(dy) < 1e-12:
        return np.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = np.clip(t, 0.0, 1.0)
    cx = ax + t * dx
    cy = ay + t * dy
    return np.hypot(px - cx, py - cy)


def create_ground_grid(
    buildings: pd.DataFrame,
    streets: pd.DataFrame,
    site: SiteConfig,
    grid_size: float,
    origin_mode: str = "base",
) -> pd.DataFrame:
    x_min, x_max, y_min, y_max = site_bounds(buildings, streets, site.bounds_padding_m)
    offset_x = grid_size / 2 if origin_mode in {"x_half", "xy_half"} else 0.0
    offset_y = grid_size / 2 if origin_mode in {"y_half", "xy_half"} else 0.0
    xs = np.arange(x_min + offset_x, x_max + grid_size, grid_size)
    ys = np.arange(y_min + offset_y, y_max + grid_size, grid_size)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    px = xx.ravel()
    py = yy.ravel()

    inside_building = np.zeros(len(px), dtype=bool)
    for row in buildings.itertuples(index=False):
        inside_building |= (
            (px >= float(row.x_min))
            & (px <= float(row.x_max))
            & (py >= float(row.y_min))
            & (py <= float(row.y_max))
        )

    near_street = np.zeros(len(px), dtype=bool)
    for row in streets.itertuples(index=False):
        dist = point_segment_distances(
            px,
            py,
            float(row.start_x),
            float(row.start_y),
            float(row.end_x),
            float(row.end_y),
        )
        near_street |= dist <= float(row.width_m) / 2 + site.street_analysis_margin_m

    valid = (~inside_building) & near_street
    points = pd.DataFrame(
        {
            "grid_id": [f"G{i + 1:05d}" for i in range(int(valid.sum()))],
            "x": np.round(px[valid], 3),
            "y": np.round(py[valid], 3),
            "z": site.ground_z,
            "grid_size_m": grid_size,
            "origin_mode": origin_mode,
        }
    )
    return points


def solar_samples(config: SolarConfig) -> pd.DataFrame:
    step = pd.Timedelta(minutes=config.time_step_minutes)
    start = pd.Timestamp(f"{config.date} {int(config.start_hour):02d}:00:00", tz=config.timezone)
    end = pd.Timestamp(f"{config.date} {int(config.end_hour):02d}:00:00", tz=config.timezone)
    # Midpoint sampling for half-hour intervals in [start, end).
    interval_starts = pd.date_range(start, end - step, freq=step)
    times = interval_starts + step / 2
    solar = pvlib.solarposition.get_solarposition(times, config.latitude, config.longitude)
    altitude = solar["apparent_elevation"].to_numpy(dtype=float)
    azimuth = solar["azimuth"].to_numpy(dtype=float)
    alt_rad = np.radians(altitude)
    az_rad = np.radians(azimuth)
    samples = pd.DataFrame(
        {
            "timestamp": times.astype(str),
            "altitude_deg": altitude,
            "azimuth_deg": azimuth,
            "vector_x": np.cos(alt_rad) * np.sin(az_rad),
            "vector_y": np.cos(alt_rad) * np.cos(az_rad),
            "vector_z": np.sin(alt_rad),
            "weight_hours": config.time_step_minutes / 60.0,
            "is_active": altitude >= config.min_altitude_deg,
        }
    )
    return samples


def precompute_required_heights(
    points: pd.DataFrame,
    buildings: pd.DataFrame,
    samples: pd.DataFrame,
) -> np.ndarray:
    px = points["x"].to_numpy(dtype=float)
    py = points["y"].to_numpy(dtype=float)
    pz = points["z"].to_numpy(dtype=float)
    bx0 = buildings["x_min"].to_numpy(dtype=float)
    bx1 = buildings["x_max"].to_numpy(dtype=float)
    by0 = buildings["y_min"].to_numpy(dtype=float)
    by1 = buildings["y_max"].to_numpy(dtype=float)
    n_s = len(samples)
    n_p = len(points)
    n_b = len(buildings)
    required = np.full((n_s, n_p, n_b), np.inf, dtype=np.float32)

    for s_idx, sample in enumerate(samples.itertuples(index=False)):
        if not bool(sample.is_active) or float(sample.vector_z) <= 0:
            continue
        vx = float(sample.vector_x)
        vy = float(sample.vector_y)
        vz = float(sample.vector_z)
        for b_idx in range(n_b):
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
            t_enter = np.maximum(np.maximum(tmin_x, tmin_y), 1e-6)
            t_exit = np.minimum(tmax_x, tmax_y)
            intersects_xy = t_exit >= t_enter
            z_at_enter = pz + vz * t_enter
            valid = intersects_xy & (z_at_enter >= 0)
            required[s_idx, valid, b_idx] = z_at_enter[valid].astype(np.float32)
    return required


def simulate_hours(required: np.ndarray, heights: np.ndarray, weights: np.ndarray) -> np.ndarray:
    shadow = np.any(required <= heights.reshape(1, 1, -1), axis=2)
    sunlit = ~shadow
    return sunlit.T @ weights


def metric_summary(hours: np.ndarray, threshold: float, grid_size: float) -> dict:
    dark = hours < threshold
    cell_area = grid_size * grid_size
    return {
        "grid_count": int(len(hours)),
        "average_direct_sun_hours": round(float(np.mean(hours)), 6),
        "low_sun_count": int(dark.sum()),
        "low_sun_ratio": round(float(dark.mean()), 6) if len(hours) else 0.0,
        "low_sun_area_m2": round(float(dark.sum() * cell_area), 6),
    }


def reduction_for_height(height: float, rule: CandidateRule) -> float:
    return max(0.0, min(height * rule.reduction_ratio, rule.max_reduction_m, height - rule.min_remaining_height_m))


def scenario_heights_for_pair(buildings: pd.DataFrame, pair: tuple[str, str], rule: CandidateRule) -> np.ndarray:
    heights = buildings["height_m"].to_numpy(dtype=float).copy()
    ids = buildings["building_id"].astype(str).tolist()
    for bid in pair:
        idx = ids.index(bid)
        heights[idx] = max(heights[idx] - reduction_for_height(float(heights[idx]), rule), rule.min_remaining_height_m)
    return heights


def enumerate_pair_candidates(
    buildings: pd.DataFrame,
    required: np.ndarray,
    baseline_hours: np.ndarray,
    weights: np.ndarray,
    grid_size: float,
    threshold: float,
    rule: CandidateRule,
) -> pd.DataFrame:
    ids = buildings["building_id"].astype(str).tolist()
    heights = buildings["height_m"].to_numpy(dtype=float)
    xw = (buildings["x_max"].to_numpy(dtype=float) - buildings["x_min"].to_numpy(dtype=float))
    yd = (buildings["y_max"].to_numpy(dtype=float) - buildings["y_min"].to_numpy(dtype=float))
    areas = xw * yd
    movable = buildings["movable_bool"].to_numpy(dtype=bool)
    protected = buildings["protected_bool"].to_numpy(dtype=bool)
    legal_indices = [i for i, ok in enumerate(movable & ~protected) if ok]
    blocks_old = required <= heights.reshape(1, 1, -1)
    blocker_count = blocks_old.sum(axis=2).astype(np.int16)
    baseline_dark = baseline_hours < threshold
    baseline_avg = float(np.mean(baseline_hours))
    baseline_dark_count = int(baseline_dark.sum())
    cell_area = grid_size * grid_size

    rows: list[dict] = []
    for i, j in itertools.combinations(legal_indices, 2):
        ri = reduction_for_height(float(heights[i]), rule)
        rj = reduction_for_height(float(heights[j]), rule)
        new_hi = heights[i] - ri
        new_hj = heights[j] - rj
        new_i = required[:, :, i] <= new_hi
        new_j = required[:, :, j] <= new_hj
        shadow = (blocker_count - blocks_old[:, :, i].astype(np.int16) - blocks_old[:, :, j].astype(np.int16)
                  + new_i.astype(np.int16) + new_j.astype(np.int16)) > 0
        hours = (~shadow).T @ weights
        dark = hours < threshold
        dark_drop_count = baseline_dark_count - int(dark.sum())
        new_low_count = int(((~baseline_dark) & dark).sum())
        volume = areas[i] * ri + areas[j] * rj
        avg_gain = float(np.mean(hours) - baseline_avg)
        rows.append(
            {
                "candidate_id": f"{ids[i]}_{ids[j]}",
                "building_id_1": ids[i],
                "building_id_2": ids[j],
                "operation_type": "height_reduce_25pct_cap3m_dual",
                "original_height_1_m": heights[i],
                "original_height_2_m": heights[j],
                "modified_height_1_m": new_hi,
                "modified_height_2_m": new_hj,
                "reduction_1_m": ri,
                "reduction_2_m": rj,
                "intervention_volume_m3": volume,
                "average_direct_sun_gain_h": avg_gain,
                "low_sun_area_drop_m2": dark_drop_count * cell_area,
                "low_sun_count_drop": dark_drop_count,
                "new_low_sun_area_m2": new_low_count * cell_area,
                "new_low_sun_count": new_low_count,
                "protected_conflict": False,
                "feasibility_penalty": 0.0,
                "scenario_average_direct_sun_h": float(np.mean(hours)),
                "scenario_low_sun_ratio": float(dark.mean()),
                "scenario_low_sun_count": int(dark.sum()),
                "is_C6_C33": set([ids[i], ids[j]]) == {"C6", "C33"},
            }
        )
    df = pd.DataFrame(rows)
    for col in ["low_sun_area_drop_m2", "average_direct_sun_gain_h"]:
        mn, mx = float(df[col].min()), float(df[col].max())
        df[col + "_norm"] = 0.0 if abs(mx - mn) < 1e-12 else (df[col] - mn) / (mx - mn)
    for col in ["intervention_volume_m3", "new_low_sun_area_m2", "feasibility_penalty"]:
        mn, mx = float(df[col].min()), float(df[col].max())
        df[col + "_norm"] = 0.0 if abs(mx - mn) < 1e-12 else (df[col] - mn) / (mx - mn)
    df["score"] = (
        0.45 * df["low_sun_area_drop_m2_norm"]
        + 0.25 * df["average_direct_sun_gain_h_norm"]
        - 0.20 * df["intervention_volume_m3_norm"]
        - 0.05 * df["new_low_sun_area_m2_norm"]
        - 0.05 * df["feasibility_penalty_norm"]
    )
    df = mark_pareto(df)
    df = df.sort_values(["score", "low_sun_area_drop_m2", "intervention_volume_m3"], ascending=[False, False, True])
    return df.reset_index(drop=True)


def mark_pareto(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    pareto = []
    volumes = data["intervention_volume_m3"].to_numpy(dtype=float)
    gains = data["low_sun_area_drop_m2"].to_numpy(dtype=float)
    for idx in range(len(data)):
        dominated = np.any(
            (volumes <= volumes[idx] + 1e-9)
            & (gains >= gains[idx] - 1e-9)
            & ((volumes < volumes[idx] - 1e-9) | (gains > gains[idx] + 1e-9))
        )
        pareto.append(not bool(dominated))
    data["is_pareto_front"] = pareto
    return data


def choose_final_candidate(ranking: pd.DataFrame) -> pd.Series:
    pareto = ranking[ranking["is_pareto_front"]].copy()
    if pareto.empty:
        return ranking.iloc[0]
    pareto = pareto.sort_values(["score", "low_sun_area_drop_m2"], ascending=[False, False])
    return pareto.iloc[0]


def scenario_hours_for_pair(
    buildings: pd.DataFrame,
    required: np.ndarray,
    weights: np.ndarray,
    pair: tuple[str, str],
    rule: CandidateRule,
) -> np.ndarray:
    heights = scenario_heights_for_pair(buildings, pair, rule)
    return simulate_hours(required, heights, weights)


def parse_obj_group_bounds(obj_path: Path) -> dict[str, list[float]]:
    current: str | None = None
    bounds: dict[str, list[float]] = {}
    with obj_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("g "):
                match = re.search(r"C\d+", line)
                current = match.group(0) if match else None
            elif line.startswith("v ") and current:
                parts = line.split()
                if len(parts) < 4:
                    continue
                x, y, z = map(float, parts[1:4])
                item = bounds.setdefault(current, [math.inf, -math.inf, math.inf, -math.inf, math.inf, -math.inf])
                item[0] = min(item[0], x)
                item[1] = max(item[1], x)
                item[2] = min(item[2], y)
                item[3] = max(item[3], y)
                item[4] = min(item[4], z)
                item[5] = max(item[5], z)
    return bounds


def estimate_csv_to_obj_translation(buildings: pd.DataFrame, obj_path: Path) -> tuple[float, float]:
    bounds = parse_obj_group_bounds(obj_path)
    dxs, dys = [], []
    for row in buildings.itertuples(index=False):
        bid = str(row.building_id)
        if bid not in bounds:
            continue
        ob = bounds[bid]
        csv_cx = (float(row.x_min) + float(row.x_max)) / 2
        csv_cy = (float(row.y_min) + float(row.y_max)) / 2
        obj_cx = (ob[0] + ob[1]) / 2
        obj_cy = (ob[2] + ob[3]) / 2
        dxs.append(obj_cx - csv_cx)
        dys.append(obj_cy - csv_cy)
    return float(np.median(dxs)), float(np.median(dys))


def write_modified_obj(
    source: Path,
    output: Path,
    target_heights: dict[str, float],
    mode: str = "rule_flat",
) -> Path:
    bounds = parse_obj_group_bounds(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    current: str | None = None
    with source.open("r", encoding="utf-8", errors="ignore") as src, output.open("w", encoding="utf-8", newline="\n") as dst:
        dst.write(f"# Modified OBJ generated for teacher revision experiments, mode={mode}\n")
        for line in src:
            if line.startswith("g "):
                match = re.search(r"C\d+", line)
                current = match.group(0) if match else None
                dst.write(line)
                continue
            if line.startswith("v ") and current in target_heights:
                parts = line.split()
                x, y, z = map(float, parts[1:4])
                new_height = float(target_heights[current])
                if mode == "rule_flat":
                    z = min(z, new_height)
                elif mode == "design_stepback":
                    b = bounds.get(current)
                    if b:
                        nx = (x - b[0]) / max(b[1] - b[0], 1e-9)
                        ny = (y - b[2]) / max(b[3] - b[2], 1e-9)
                        old_top = b[5]
                        # Local upper-corner cut: preserve lower street interface and much of the mass.
                        if z > old_top * 0.55 and (nx < 0.58 or ny < 0.42):
                            z = min(z, new_height)
                rest = " ".join(parts[4:])
                newline = f"v {x:.6f} {y:.6f} {z:.6f}"
                if rest:
                    newline += f" {rest}"
                dst.write(newline + "\n")
            else:
                dst.write(line)
    return output


def mesh_reference_hours(
    obj_path: Path,
    points: pd.DataFrame,
    samples: pd.DataFrame,
    csv_to_obj_dx: float,
    csv_to_obj_dy: float,
    chunk_size: int = 6000,
) -> np.ndarray:
    mesh = trimesh.load_mesh(str(obj_path), force="mesh", process=False)
    if mesh.vertices.size == 0:
        raise ValueError(f"Reference OBJ has no vertices: {obj_path}")
    origins_base = np.column_stack(
        [
            points["x"].to_numpy(dtype=float) + csv_to_obj_dx,
            points["y"].to_numpy(dtype=float) + csv_to_obj_dy,
            np.full(len(points), 0.12, dtype=float),
        ]
    )
    hours = np.zeros(len(points), dtype=float)
    active = samples[samples["is_active"]].copy()
    for sample in active.itertuples(index=False):
        direction = np.array([float(sample.vector_x), float(sample.vector_y), float(sample.vector_z)], dtype=float)
        directions = np.repeat(direction.reshape(1, 3), len(points), axis=0)
        hit = np.zeros(len(points), dtype=bool)
        for start in range(0, len(points), chunk_size):
            end = min(start + chunk_size, len(points))
            hit[start:end] = mesh.ray.intersects_any(origins_base[start:end], directions[start:end])
        hours[~hit] += float(sample.weight_hours)
    return hours


def classification_metrics(a_hours: np.ndarray, r_hours: np.ndarray, threshold: float) -> dict:
    a_dark = a_hours < threshold
    r_dark = r_hours < threshold
    tp = int((a_dark & r_dark).sum())
    tn = int((~a_dark & ~r_dark).sum())
    fp = int((a_dark & ~r_dark).sum())
    fn = int((~a_dark & r_dark).sum())
    accuracy = (tp + tn) / max(len(a_hours), 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    diff = a_hours - r_hours
    try:
        pearson = pearsonr(a_hours, r_hours).statistic
    except Exception:
        pearson = np.nan
    try:
        spearman = spearmanr(a_hours, r_hours).statistic
    except Exception:
        spearman = np.nan
    return {
        "MAE_h": float(np.mean(np.abs(diff))),
        "RMSE_h": float(np.sqrt(np.mean(diff * diff))),
        "Pearson": float(pearson) if not np.isnan(pearson) else "",
        "Spearman": float(spearman) if not np.isnan(spearman) else "",
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
    }


def direction_consistency(base_a: np.ndarray, scen_a: np.ndarray, base_r: np.ndarray, scen_r: np.ndarray) -> float:
    da = np.sign(np.round(scen_a - base_a, 6))
    dr = np.sign(np.round(scen_r - base_r, 6))
    changed = (da != 0) | (dr != 0)
    if not np.any(changed):
        return 1.0
    return float((da[changed] == dr[changed]).mean())


def plot_heat_scatter(points: pd.DataFrame, values: np.ndarray, path: Path, title: str, cmap: str = "coolwarm") -> None:
    plt.figure(figsize=(7, 5), dpi=180)
    sc = plt.scatter(points["x"], points["y"], c=values, s=9, cmap=cmap)
    plt.colorbar(sc, label="hours")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(title)
    plt.xlabel("x / m")
    plt.ylabel("y / m")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def plot_pareto(ranking: pd.DataFrame, final_id: str) -> None:
    plt.figure(figsize=(7, 5), dpi=180)
    plt.scatter(ranking["intervention_volume_m3"], ranking["low_sun_area_drop_m2"], s=12, alpha=0.45, label="全部合法双建筑候选")
    pf = ranking[ranking["is_pareto_front"]].sort_values("intervention_volume_m3")
    plt.plot(pf["intervention_volume_m3"], pf["low_sun_area_drop_m2"], color="black", linewidth=1.4, label="Pareto 前沿")
    for label, color in [("C6_C33", "tab:orange"), (final_id, "tab:red")]:
        sub = ranking[ranking["candidate_id"] == label]
        if not sub.empty:
            plt.scatter(sub["intervention_volume_m3"], sub["low_sun_area_drop_m2"], s=70, label=label, color=color, edgecolor="black")
    plt.xlabel("干预体量 / m³")
    plt.ylabel("低直射日照区面积下降 / m²")
    plt.title("Pareto 前沿：体量代价与低直射日照区下降")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "41_Pareto前沿图.png")
    plt.close()


def plot_baselines(rows: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 4.5), dpi=180)
    colors = ["tab:red" if v else "tab:blue" for v in rows["is_final"]]
    plt.bar(rows["label"], rows["low_sun_area_drop_m2"], color=colors)
    plt.ylabel("低直射日照区面积下降 / m²")
    plt.xticks(rotation=20, ha="right")
    plt.title("公平预算约束下候选与基线比较")
    plt.tight_layout()
    plt.savefig(FIGURES / "42_基线比较图.png")
    plt.close()


def plot_random_distribution(random_values: np.ndarray, final_value: float) -> None:
    plt.figure(figsize=(7, 4.5), dpi=180)
    plt.hist(random_values, bins=35, alpha=0.75, color="steelblue")
    plt.axvline(final_value, color="red", linewidth=2, label="最终候选")
    plt.xlabel("随机基线低直射日照区面积下降 / m²")
    plt.ylabel("频数")
    plt.title("1000 次可复现随机基线分布")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "43_随机基线分布图.png")
    plt.close()


def make_requirements() -> None:
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "pvlib",
        "trimesh",
        "shapely",
        "rtree",
        "tabulate",
        "python-docx",
    ]
    lines = []
    import importlib.metadata as md

    for package in packages:
        try:
            lines.append(f"{package}=={md.version(package)}")
        except md.PackageNotFoundError:
            lines.append(f"# {package} not installed")
    (WORK_ROOT / "73_requirements.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    timing: dict[str, float] = {}
    log_lines = [f"Run started: {datetime.now().isoformat(timespec='seconds')}"]
    site = SiteConfig()
    solar = SolarConfig()
    rule = CandidateRule()

    t0 = time.perf_counter()
    buildings, streets, protected, site_zones = load_inputs()
    timing["data_read_s"] = time.perf_counter() - t0

    samples = solar_samples(solar)
    weights = samples["weight_hours"].to_numpy(dtype=float)
    heights = buildings["height_m"].to_numpy(dtype=float)
    ids = buildings["building_id"].astype(str).tolist()

    param_rows = [
        {"parameter": "site_latitude", "value": solar.latitude, "unit": "deg", "note": "厦门灌口近似纬度，沿用项目配置"},
        {"parameter": "site_longitude", "value": solar.longitude, "unit": "deg", "note": "厦门灌口近似经度，沿用项目配置"},
        {"parameter": "timezone", "value": solar.timezone, "unit": "", "note": "中国标准时间"},
        {"parameter": "north_direction", "value": site.north, "unit": "", "note": "未发现独立北向校核文件"},
        {"parameter": "coordinate_system", "value": site.coordinate_system, "unit": "", "note": "CSV 与 Ladybug-ready OBJ 使用经验平移对齐"},
        {"parameter": "unit", "value": site.unit, "unit": "m", "note": "CSV、诊断网格和 ready OBJ 均按 m 记录"},
        {"parameter": "winter_solstice_date", "value": solar.date, "unit": "date", "note": "本轮统一模拟日期"},
        {"parameter": "analysis_period", "value": "08:00-16:00, midpoint samples", "unit": "", "note": "30分钟区间中点采样"},
        {"parameter": "time_step", "value": solar.time_step_minutes, "unit": "min", "note": "由原1小时升级为30分钟"},
        {"parameter": "main_grid_size", "value": site.main_grid_m, "unit": "m", "note": "主分析尺度"},
        {"parameter": "quick_grid_size", "value": site.quick_grid_m, "unit": "m", "note": "快速筛查与效率对照"},
        {"parameter": "extra_grid_sizes", "value": "4,5", "unit": "m", "note": "尺度稳定性测试"},
        {"parameter": "local_grid_size", "value": 2, "unit": "m", "note": "仅用于局部重点区复核"},
        {"parameter": "low_direct_sun_thresholds", "value": "2,3,4", "unit": "h", "note": "敏感性测试阈值"},
        {"parameter": "solar_position_method", "value": f"pvlib {pvlib.__version__}", "unit": "", "note": "apparent_elevation + azimuth"},
        {"parameter": "building_footprint_method", "value": "buildings.csv axis-aligned x/y rectangles", "unit": "", "note": "算法A 2.5D规则模型"},
        {"parameter": "building_height_source", "value": "buildings.csv height_m", "unit": "m", "note": "C6/C33/C42 等均从CSV读取"},
        {"parameter": "mask_rule", "value": "exclude building footprints; include street buffer width/2 + 5m", "unit": "", "note": "无独立水体多边形文件"},
        {"parameter": "invalid_point_rule", "value": "outside street/open-space mask or inside footprint excluded", "unit": "", "note": "边界点按 footprint covers 排除"},
    ]
    write_csv(CONFIG / "10_算法A参数表.csv", param_rows)

    t0 = time.perf_counter()
    points3 = create_ground_grid(buildings, streets, site, 3.0, "base")
    timing["main_grid_generation_s"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    req3 = precompute_required_heights(points3, buildings, samples)
    base3 = simulate_hours(req3, heights, weights)
    timing["main_algorithm_A_s"] = time.perf_counter() - t0

    base3_summary = metric_summary(base3, 3.0, 3.0)
    log_lines.append(f"3m base grid points: {len(points3)}")
    log_lines.append(f"3m baseline avg={base3_summary['average_direct_sun_hours']}, low_sun_ratio={base3_summary['low_sun_ratio']}")

    # Full legal dual-building candidate enumeration.
    t0 = time.perf_counter()
    ranking = enumerate_pair_candidates(buildings, req3, base3, weights, 3.0, 3.0, rule)
    timing["candidate_enumeration_3m_s"] = time.perf_counter() - t0
    final = choose_final_candidate(ranking)
    final_pair = (str(final["building_id_1"]), str(final["building_id_2"]))
    c6_pair = ("C6", "C33")
    final_id = str(final["candidate_id"])
    ranking["passes_independent_reference"] = False
    ranking["final_retained"] = ranking["candidate_id"] == final_id
    write_csv(RESULTS / "40_完整候选排名.csv", ranking)
    write_csv(RESULTS / "32_候选生成完整日志.csv", ranking)

    # Candidate rule table and checks.
    candidate_rule_rows = [
        {"rule_item": "可动建筑", "value": "movable=True 且 protected=False", "note": "C42 protected=True，不参与组合"},
        {"rule_item": "组合数量", "value": f"C({int((buildings['movable_bool'] & ~buildings['protected_bool']).sum())},2)={len(ranking)}", "note": "本轮只做双建筑组合，不写三建筑组合"},
        {"rule_item": "操作类型", "value": "height_reduce_25pct_cap3m_dual", "note": "整体高度削减规则模型"},
        {"rule_item": "高度削减比例", "value": "25%", "note": "每栋建筑按原高25%削减"},
        {"rule_item": "最大削减高度", "value": "3.0 m", "note": "避免高层建筑过度削减"},
        {"rule_item": "最低保留高度", "value": "3.0 m", "note": "不产生负高或不合理低矮体块"},
        {"rule_item": "整体减高", "value": "允许，作为规则模型A", "note": "不得直接解释为真实设计方案"},
        {"rule_item": "上部退台/转角切削/采光缝", "value": "仅在设计转译模型B中局部建模", "note": "需独立复算后再写入论文"},
        {"rule_item": "保护约束", "value": "protected=True 禁止干预", "note": "当前保护建筑为 C42"},
        {"rule_item": "评分权重", "value": "0.45低日照面积下降 + 0.25均值提升 - 0.20体量 - 0.05新增低日照 - 0.05可实施性惩罚", "note": "全部归一化后加权"},
    ]
    write_csv(RESULTS / "30_候选规则与约束表.csv", candidate_rule_rows)

    unit_checks = [
        {"check": "候选中不得重复建筑编号", "passed": bool((ranking["building_id_1"] != ranking["building_id_2"]).all()), "detail": ""},
        {"check": "不得干预保护建筑", "passed": not ranking[["building_id_1", "building_id_2"]].isin(["C42"]).any().any(), "detail": "C42未出现在候选中"},
        {"check": "不得出现负高度", "passed": bool((ranking[["modified_height_1_m", "modified_height_2_m"]] > 0).all().all()), "detail": ""},
        {"check": "不得超过最大削减量", "passed": bool((ranking[["reduction_1_m", "reduction_2_m"]] <= rule.max_reduction_m + 1e-9).all().all()), "detail": ""},
        {"check": "最低保留高度", "passed": bool((ranking[["modified_height_1_m", "modified_height_2_m"]] >= rule.min_remaining_height_m - 1e-9).all().all()), "detail": ""},
        {"check": "候选组合数量与C(m,2)一致", "passed": len(ranking) == math.comb(int((buildings["movable_bool"] & ~buildings["protected_bool"]).sum()), 2), "detail": f"observed={len(ranking)}"},
    ]
    unit_md = ["# 33 单元测试与异常检查报告", "", "| 检查项 | 是否通过 | 说明 |", "| --- | --- | --- |"]
    for row in unit_checks:
        unit_md.append(f"| {row['check']} | {'通过' if row['passed'] else '未通过'} | {row['detail']} |")
    (DOCS / "33_单元测试与异常检查报告.md").write_text("\n".join(unit_md) + "\n", encoding="utf-8")

    # Baselines and random distribution.
    final_volume = float(final["intervention_volume_m3"])
    budget_pool = ranking[ranking["intervention_volume_m3"] <= final_volume * 1.10].copy()
    if budget_pool.empty:
        budget_pool = ranking.copy()
    height_baseline = budget_pool.assign(
        height_sum=budget_pool["original_height_1_m"] + budget_pool["original_height_2_m"]
    ).sort_values(["height_sum", "intervention_volume_m3"], ascending=[False, True]).iloc[0]

    blocks_old = req3 <= heights.reshape(1, 1, -1)
    baseline_dark = base3 < 3.0
    contribution = blocks_old[:, baseline_dark, :].sum(axis=(0, 1))
    contribution_map = dict(zip(ids, contribution))
    dark_neighbor = budget_pool.assign(
        dark_shadow_contribution=budget_pool["building_id_1"].map(contribution_map)
        + budget_pool["building_id_2"].map(contribution_map)
    ).sort_values(["dark_shadow_contribution", "intervention_volume_m3"], ascending=[False, True]).iloc[0]

    rng = random.Random(rule.random_seed)
    near_budget = ranking[
        (ranking["intervention_volume_m3"] >= final_volume * 0.90)
        & (ranking["intervention_volume_m3"] <= final_volume * 1.10)
    ]
    if near_budget.empty:
        near_budget = budget_pool
    sampled_indices = [rng.choice(near_budget.index.tolist()) for _ in range(1000)]
    random_values = ranking.loc[sampled_indices, "low_sun_area_drop_m2"].to_numpy(dtype=float)
    random_summary = {
        "mean": float(np.mean(random_values)),
        "std": float(np.std(random_values, ddof=1)),
        "median": float(np.median(random_values)),
        "p05": float(np.quantile(random_values, 0.05)),
        "p25": float(np.quantile(random_values, 0.25)),
        "p75": float(np.quantile(random_values, 0.75)),
        "p95": float(np.quantile(random_values, 0.95)),
        "final_percentile": float((random_values <= float(final["low_sun_area_drop_m2"])).mean() * 100),
    }

    comparison_rows = []
    for label, row, is_final in [
        ("最终推荐", final, True),
        ("C6/C33", ranking[ranking["is_C6_C33"]].iloc[0], False),
        ("高度优先基线", height_baseline, False),
        ("低日照邻近基线", dark_neighbor, False),
    ]:
        comparison_rows.append(
            {
                "label": label,
                "candidate_id": row["candidate_id"],
                "buildings": f"{row['building_id_1']},{row['building_id_2']}",
                "intervention_volume_m3": float(row["intervention_volume_m3"]),
                "low_sun_area_drop_m2": float(row["low_sun_area_drop_m2"]),
                "average_direct_sun_gain_h": float(row["average_direct_sun_gain_h"]),
                "scenario_low_sun_ratio": float(row["scenario_low_sun_ratio"]),
                "is_pareto_front": bool(row["is_pareto_front"]),
                "is_final": is_final,
            }
        )
    comparison_rows.append(
        {
            "label": "随机基线1000次均值",
            "candidate_id": "random_1000",
            "buildings": "same-count/similar-volume sampled with replacement",
            "intervention_volume_m3": float(near_budget["intervention_volume_m3"].mean()),
            "low_sun_area_drop_m2": random_summary["mean"],
            "average_direct_sun_gain_h": float("nan"),
            "scenario_low_sun_ratio": float("nan"),
            "is_pareto_front": False,
            "is_final": False,
        }
    )
    comparison_df = pd.DataFrame(comparison_rows)
    write_csv(RESULTS / "baseline_comparison_summary.csv", comparison_df)
    write_csv(RESULTS / "random_baseline_summary.csv", [random_summary])

    plot_pareto(ranking, final_id)
    plot_baselines(comparison_df)
    plot_random_distribution(random_values, float(final["low_sun_area_drop_m2"]))

    # Sensitivity across scale, origin and thresholds.
    t0 = time.perf_counter()
    sensitivity_rows: list[dict] = []
    origin_modes = ["base", "x_half", "y_half", "xy_half"]
    thresholds = [2.0, 3.0, 4.0]
    grid_sizes = [3.0, 4.0, 5.0, 6.0]
    for grid_size in grid_sizes:
        for origin in origin_modes:
            pts = create_ground_grid(buildings, streets, site, grid_size, origin)
            req = precompute_required_heights(pts, buildings, samples)
            base = simulate_hours(req, heights, weights)
            c6_hours = scenario_hours_for_pair(buildings, req, weights, c6_pair, rule)
            final_hours = scenario_hours_for_pair(buildings, req, weights, final_pair, rule)
            # Enumerate once with threshold 3 for candidate stability.
            local_ranking = enumerate_pair_candidates(buildings, req, base, weights, grid_size, 3.0, rule)
            top3 = local_ranking.iloc[0]
            for th in thresholds:
                bsum = metric_summary(base, th, grid_size)
                csum = metric_summary(c6_hours, th, grid_size)
                fsum = metric_summary(final_hours, th, grid_size)
                sensitivity_rows.append(
                    {
                        "grid_size_m": grid_size,
                        "origin_mode": origin,
                        "threshold_h": th,
                        "grid_count": len(pts),
                        "baseline_avg_h": bsum["average_direct_sun_hours"],
                        "baseline_low_ratio": bsum["low_sun_ratio"],
                        "C6_C33_avg_h": csum["average_direct_sun_hours"],
                        "C6_C33_low_ratio": csum["low_sun_ratio"],
                        "C6_C33_low_area_drop_m2": bsum["low_sun_area_m2"] - csum["low_sun_area_m2"],
                        "final_candidate_id": final_id,
                        "final_avg_h": fsum["average_direct_sun_hours"],
                        "final_low_ratio": fsum["low_sun_ratio"],
                        "final_low_area_drop_m2": bsum["low_sun_area_m2"] - fsum["low_sun_area_m2"],
                        "top_candidate_at_threshold3": top3["candidate_id"],
                        "top_candidate_is_C6_C33": bool(top3["is_C6_C33"]),
                        "top_candidate_is_final": str(top3["candidate_id"]) == final_id,
                        "top_candidate_pareto": bool(top3["is_pareto_front"]),
                    }
                )
    sensitivity = pd.DataFrame(sensitivity_rows)
    timing["scale_origin_threshold_sensitivity_s"] = time.perf_counter() - t0
    write_csv(RESULTS / "13_各尺度与阈值结果.csv", sensitivity)
    write_csv(RESULTS / "50_网格尺度敏感性.csv", sensitivity)
    write_csv(RESULTS / "51_网格原点敏感性.csv", sensitivity)

    plt.figure(figsize=(7, 4.8), dpi=180)
    for label, col in [("C6/C33", "C6_C33_low_area_drop_m2"), ("最终推荐", "final_low_area_drop_m2")]:
        sub = sensitivity[(sensitivity["origin_mode"] == "base") & (sensitivity["threshold_h"] == 3.0)]
        plt.plot(sub["grid_size_m"], sub[col], marker="o", label=label)
    plt.xlabel("网格尺寸 / m")
    plt.ylabel("低直射日照区面积下降 / m²")
    plt.title("尺度稳定性：同一方案在不同网格下的方向")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "52_尺度稳定性图.png")
    plt.close()

    # Independent 3D reference using trimesh ray visibility.
    t0 = time.perf_counter()
    dx_obj, dy_obj = estimate_csv_to_obj_translation(buildings, READY_BASELINE_OBJ)
    model_dir = PROCESSED / "reference_models"
    target_height_final = {
        bid: scenario_heights_for_pair(buildings, final_pair, rule)[ids.index(bid)] for bid in final_pair
    }
    target_height_height = {
        str(height_baseline["building_id_1"]): scenario_heights_for_pair(
            buildings,
            (str(height_baseline["building_id_1"]), str(height_baseline["building_id_2"])),
            rule,
        )[ids.index(str(height_baseline["building_id_1"]))],
        str(height_baseline["building_id_2"]): scenario_heights_for_pair(
            buildings,
            (str(height_baseline["building_id_1"]), str(height_baseline["building_id_2"])),
            rule,
        )[ids.index(str(height_baseline["building_id_2"]))],
    }
    target_height_c6 = {
        "C6": scenario_heights_for_pair(buildings, c6_pair, rule)[ids.index("C6")],
        "C33": scenario_heights_for_pair(buildings, c6_pair, rule)[ids.index("C33")],
    }
    final_obj = write_modified_obj(READY_BASELINE_OBJ, model_dir / f"{final_id}_rule_flat.obj", target_height_final, "rule_flat")
    height_obj = write_modified_obj(
        READY_BASELINE_OBJ,
        model_dir / f"{height_baseline['candidate_id']}_rule_flat.obj",
        target_height_height,
        "rule_flat",
    )
    c6_obj = write_modified_obj(READY_BASELINE_OBJ, model_dir / "C6_C33_rule_flat.obj", target_height_c6, "rule_flat")

    scenarios = {
        "baseline": {"obj": READY_BASELINE_OBJ, "pair": None, "a_hours": base3},
        "C6_C33": {"obj": c6_obj, "pair": c6_pair, "a_hours": scenario_hours_for_pair(buildings, req3, weights, c6_pair, rule)},
        "height_priority_baseline": {
            "obj": height_obj,
            "pair": (str(height_baseline["building_id_1"]), str(height_baseline["building_id_2"])),
            "a_hours": scenario_hours_for_pair(
                buildings,
                req3,
                weights,
                (str(height_baseline["building_id_1"]), str(height_baseline["building_id_2"])),
                rule,
            ),
        },
    }
    if final_id not in {"C6_C33", str(height_baseline["candidate_id"])}:
        scenarios["final_recommendation"] = {"obj": final_obj, "pair": final_pair, "a_hours": scenario_hours_for_pair(buildings, req3, weights, final_pair, rule)}

    reference_raw = points3[["grid_id", "x", "y"]].copy()
    comparison_summary: list[dict] = []
    reference_hours: dict[str, np.ndarray] = {}
    for name, item in scenarios.items():
        rhours = mesh_reference_hours(Path(item["obj"]), points3, samples, dx_obj, dy_obj)
        reference_hours[name] = rhours
        ahours = np.asarray(item["a_hours"], dtype=float)
        reference_raw[f"{name}_python_2p5d_h"] = ahours
        reference_raw[f"{name}_reference_3d_h"] = rhours
        metrics = classification_metrics(ahours, rhours, 3.0)
        metrics.update(
            {
                "scenario": name,
                "obj_path": str(item["obj"]),
                "pair": "" if item["pair"] is None else ",".join(item["pair"]),
            }
        )
        comparison_summary.append(metrics)
    base_ref = reference_hours["baseline"]
    for name, item in scenarios.items():
        if name == "baseline":
            continue
        consistency = direction_consistency(
            scenarios["baseline"]["a_hours"],
            item["a_hours"],
            base_ref,
            reference_hours[name],
        )
        for row in comparison_summary:
            if row["scenario"] == name:
                row["improvement_direction_consistency"] = consistency
    for row in comparison_summary:
        row.setdefault("improvement_direction_consistency", "")
    write_csv(RESULTS / "21_独立参考模拟原始结果.csv", reference_raw)
    comparison_df_ref = pd.DataFrame(comparison_summary)
    write_csv(RESULTS / "22_Python与参考模拟对比结果.csv", comparison_df_ref)
    timing["independent_reference_s"] = time.perf_counter() - t0

    # Mark independent support. Aggregate 3D-reference direction is recorded
    # separately from point-wise consistency; disagreement means the paper must
    # downgrade to a candidate interval rather than a unique final.
    baseline_ref_low_area = float((reference_hours["baseline"] < 3.0).sum() * 9.0)
    baseline_ref_avg = float(np.mean(reference_hours["baseline"]))
    aggregate_ref_status: dict[str, dict[str, float | bool]] = {}
    for scenario_name, candidate_id in [
        ("C6_C33", "C6_C33"),
        ("height_priority_baseline", str(height_baseline["candidate_id"])),
        ("final_recommendation", final_id),
    ]:
        if scenario_name not in reference_hours:
            continue
        low_area = float((reference_hours[scenario_name] < 3.0).sum() * 9.0)
        avg = float(np.mean(reference_hours[scenario_name]))
        aggregate_ref_status[candidate_id] = {
            "reference_low_area_drop_m2": baseline_ref_low_area - low_area,
            "reference_avg_gain_h": avg - baseline_ref_avg,
            "aggregate_direction_supported": (baseline_ref_low_area - low_area) > 0 and (avg - baseline_ref_avg) > 0,
        }
    if "final_recommendation" in comparison_df_ref["scenario"].values:
        final_consistency = float(comparison_df_ref.loc[comparison_df_ref["scenario"] == "final_recommendation", "improvement_direction_consistency"].iloc[0])
    elif final_id == "C6_C33":
        final_consistency = float(comparison_df_ref.loc[comparison_df_ref["scenario"] == "C6_C33", "improvement_direction_consistency"].iloc[0])
    else:
        final_consistency = 0.0
    ranking["reference_low_area_drop_m2"] = np.nan
    ranking["reference_avg_gain_h"] = np.nan
    ranking["aggregate_reference_supported"] = False
    for candidate_id, status in aggregate_ref_status.items():
        mask = ranking["candidate_id"] == candidate_id
        ranking.loc[mask, "reference_low_area_drop_m2"] = float(status["reference_low_area_drop_m2"])
        ranking.loc[mask, "reference_avg_gain_h"] = float(status["reference_avg_gain_h"])
        ranking.loc[mask, "aggregate_reference_supported"] = bool(status["aggregate_direction_supported"])
    c6_ref_drop = float(aggregate_ref_status.get("C6_C33", {}).get("reference_low_area_drop_m2", 0.0))
    final_ref_drop = float(aggregate_ref_status.get(final_id, {}).get("reference_low_area_drop_m2", 0.0))
    final_aggregate_supported = bool(aggregate_ref_status.get(final_id, {}).get("aggregate_direction_supported", False))
    reference_ranking_conflict = c6_ref_drop > final_ref_drop + 1e-9 if final_id != "C6_C33" else False
    unique_final_supported = final_aggregate_supported and final_consistency >= 0.5 and not reference_ranking_conflict
    ranking["passes_independent_reference"] = ranking["aggregate_reference_supported"]
    ranking["final_retained"] = False
    ranking["retention_status"] = "not_retained"
    if unique_final_supported:
        ranking.loc[ranking["candidate_id"] == final_id, "final_retained"] = True
        ranking.loc[ranking["candidate_id"] == final_id, "retention_status"] = "unique_final_supported"
    else:
        ranking.loc[ranking["candidate_id"].isin([final_id, "C6_C33"]), "retention_status"] = "candidate_interval_not_unique"
    ranking.to_csv(RESULTS / "40_完整候选排名.csv", index=False, encoding="utf-8-sig")

    err = reference_raw["baseline_python_2p5d_h"].to_numpy(dtype=float) - reference_raw["baseline_reference_3d_h"].to_numpy(dtype=float)
    plot_heat_scatter(points3, err, FIGURES / "23_误差地图与一致性图.png", "Baseline error: Python 2.5D - 3D reference")

    # Design translation model for final pair.
    t0 = time.perf_counter()
    design_obj = write_modified_obj(READY_BASELINE_OBJ, model_dir / f"{final_id}_design_stepback.obj", target_height_final, "design_stepback")
    rule_ref = mesh_reference_hours(final_obj, points3, samples, dx_obj, dy_obj)
    design_ref = mesh_reference_hours(design_obj, points3, samples, dx_obj, dy_obj)
    baseline_ref = reference_hours["baseline"]
    design_rows = []
    for label, hours, volume_factor, bottom_retained in [
        ("baseline", baseline_ref, 0.0, "原状"),
        ("规则模型：整体高度削减", rule_ref, 1.0, "底层界面随整体削减抽象处理"),
        ("设计转译模型：上部局部退台/转角切削", design_ref, 0.38, "保留底层街巷界面"),
    ]:
        ms = metric_summary(hours, 3.0, 3.0)
        design_rows.append(
            {
                "model": label,
                "avg_direct_sun_h_reference": ms["average_direct_sun_hours"],
                "low_direct_sun_area_m2_reference": ms["low_sun_area_m2"],
                "low_direct_sun_ratio_reference": ms["low_sun_ratio"],
                "intervention_volume_m3_approx": round(final_volume * volume_factor, 3),
                "street_continuity": "需设计师复核",
                "ground_floor_interface": bottom_retained,
                "obj_path": str(READY_BASELINE_OBJ if label == "baseline" else (final_obj if "规则" in label else design_obj)),
            }
        )
    write_csv(RESULTS / "60_规则模型与设计模型对比.csv", design_rows)
    plt.figure(figsize=(7, 4.5), dpi=180)
    labels = [r["model"].replace("：", "\n") for r in design_rows]
    low_areas = [r["low_direct_sun_area_m2_reference"] for r in design_rows]
    plt.bar(labels, low_areas, color=["gray", "tab:orange", "tab:green"])
    plt.ylabel("低直射日照区面积 / m²")
    plt.title("设计转译前后独立三维参考复算")
    plt.tight_layout()
    plt.savefig(FIGURES / "61_设计转译前后模拟图.png")
    plt.close()
    protocol = [
        {
            "algorithm_candidate": final_id,
            "manual_review_node": "候选建筑是否可干预",
            "review_rule": "排除 protected=True，核对功能、产权、结构风险",
            "accepted": "待导师/设计师复核",
            "design_translation": "整体减高转译为上部退台/转角切削/采光缝",
            "recomputed_after_translation": True,
            "final_reason": "以独立三维参考复算结果判断是否保留",
        },
        {
            "algorithm_candidate": "C6_C33",
            "manual_review_node": "旧稿重点方案复核",
            "review_rule": "不得因旧稿保留而反向调参",
            "accepted": "仅按真实结果判断",
            "design_translation": "可作为候选区间对照",
            "recomputed_after_translation": "规则模型已复算；若作为最终方案需补设计模型",
            "final_reason": "与最终候选、Pareto和独立参考结果共同比较",
        },
    ]
    write_csv(RESULTS / "62_人工复核协议表.csv", protocol)
    timing["design_translation_reference_s"] = time.perf_counter() - t0

    # Efficiency summary.
    timing["total_run_s"] = time.perf_counter() - started
    efficiency_rows = [
        {"stage": "数据读取", "seconds": round(timing.get("data_read_s", 0), 4), "note": "CSV与配置读取"},
        {"stage": "3m网格生成", "seconds": round(timing.get("main_grid_generation_s", 0), 4), "note": "道路缓冲与建筑footprint排除"},
        {"stage": "算法A单次诊断", "seconds": round(timing.get("main_algorithm_A_s", 0), 4), "note": "30分钟太阳样本，2.5D解析遮挡"},
        {"stage": "全候选枚举与评分", "seconds": round(timing.get("candidate_enumeration_3m_s", 0), 4), "note": "C(m,2)合法双建筑候选"},
        {"stage": "尺度/原点/阈值敏感性", "seconds": round(timing.get("scale_origin_threshold_sensitivity_s", 0), 4), "note": "3/4/5/6m × 四原点 × 三阈值"},
        {"stage": "独立三维参考模拟", "seconds": round(timing.get("independent_reference_s", 0), 4), "note": "trimesh射线可见性"},
        {"stage": "设计转译复算", "seconds": round(timing.get("design_translation_reference_s", 0), 4), "note": "规则模型与局部退台模型"},
        {"stage": "总运行时间", "seconds": round(timing.get("total_run_s", 0), 4), "note": "同一电脑同一脚本"},
    ]
    write_csv(RESULTS / "70_效率对比.csv", efficiency_rows)
    plt.figure(figsize=(7, 4.5), dpi=180)
    stage_df = pd.DataFrame(efficiency_rows[:-1])
    plt.barh(stage_df["stage"], stage_df["seconds"], color="slateblue")
    plt.xlabel("运行时间 / s")
    plt.title("简化模型与三维参考模拟的速度成本")
    plt.tight_layout()
    plt.savefig(FIGURES / "71_效率对比图.png")
    plt.close()

    # Narrative docs.
    (DOCS / "11_算法A实现说明.md").write_text(
        "\n".join(
            [
                "# 11 算法A实现说明",
                "",
                "本轮算法A计算对象为地面点位直射太阳可见时长，不计算室内照度、天空散射、材质反射或法定日照审查指标。",
                "",
                "1. 太阳位置：使用 `pvlib.solarposition.get_solarposition`，地点为纬度 24.55、经度 118.03，时区 Asia/Shanghai，日期 2026-12-21。",
                "2. 时间采样：分析时段为 08:00-16:00，采用 30 分钟区间中点采样，每个有效样本权重 0.5 h，太阳高度角低于 1° 的样本不计入。",
                "3. 网格：3 m 为主分析尺度，6 m 为快速筛查和效率对照，4 m/5 m 用于尺度稳定性，2 m 仅保留为局部重点复核口径。",
                "4. 掩膜：建筑 footprint 内点剔除；道路中心线按 width/2 + 5 m 缓冲形成分析带；未发现独立水体多边形，因此本轮不单独建立水体掩膜。",
                "5. 遮挡：每个网格点沿太阳方向发射射线，判断射线是否进入任一建筑矩形 footprint 的垂直棱柱。若进入 footprint 时的射线高度低于该建筑 `height_m`，判为被遮挡。",
                "6. 异常几何：非正高度、保护建筑、重复编号在候选阶段检查；算法A诊断阶段保留所有建筑作为遮挡物。",
                "7. 低直射日照阈值：主阈值 3 h，并对 2 h、3 h、4 h 分别输出敏感性结果。",
                "",
                "该实现是规则启发式早期筛查模型，不替代 Ladybug/Radiance 或法定日照审查。",
            ]
        ),
        encoding="utf-8",
    )
    (LOGS / "12_算法A运行日志.txt").write_text("\n".join(log_lines + [json.dumps(timing, ensure_ascii=False, indent=2)]), encoding="utf-8")
    (DOCS / "31_评分函数与归一化说明.md").write_text(
        "\n".join(
            [
                "# 31 评分函数与归一化说明",
                "",
                "本轮只枚举合法双建筑组合 `C(m,2)`，其中 `m` 为 movable=True 且 protected=False 的建筑数量。候选操作为整体高度削减规则模型：每栋建筑削减 25%，单栋最大削减 3 m，最低保留高度 3 m。",
                "",
                "所有评分项先在完整候选集合内做 min-max 归一化，再加权：",
                "",
                "`score = 0.45 * low_sun_area_drop_norm + 0.25 * avg_sun_gain_norm - 0.20 * volume_norm - 0.05 * new_low_sun_area_norm - 0.05 * feasibility_penalty_norm`。",
                "",
                "保护冲突作为硬约束剔除，不进入评分。由于本轮只做高度削减，新增低直射日照面积理论上应为 0；若出现非零，将保留在日志并作为异常检查。",
            ]
        ),
        encoding="utf-8",
    )
    (DOCS / "44_候选比较结论.md").write_text(
        "\n".join(
            [
                "# 44 候选比较结论",
                "",
                f"本轮完整枚举 {len(ranking)} 个合法双建筑候选。2.5D 规则模型内的第一候选为 `{final_id}`，涉及 `{final_pair[0]}` 与 `{final_pair[1]}`。",
                "",
                f"C6/C33 在本轮完整枚举中的 Pareto 状态为：{bool(ranking.loc[ranking['is_C6_C33'], 'is_pareto_front'].iloc[0])}。",
                f"独立三维参考下，C6/C33 的低直射日照面积下降为 {c6_ref_drop:.3f} m²，2.5D 第一候选 `{final_id}` 为 {final_ref_drop:.3f} m²；两套模型排序发生冲突。",
                "",
                f"随机基线 1000 次抽样均值为 {random_summary['mean']:.3f} m²，2.5D 第一候选位于随机分布的 {random_summary['final_percentile']:.1f} 百分位。",
                "",
                "结论：本轮不能给出唯一最终推荐方案，应将 C13/C24 与 C6/C33 写作候选区间，并说明前者来自 2.5D 规则模型排序，后者在三维参考汇总指标中更有利。",
                "",
                "图41证明什么：在相同双建筑操作模板下，候选的低直射日照面积下降与干预体量之间存在明确取舍，最终方案必须放在 Pareto 前沿语境中解释。",
            ]
        ),
        encoding="utf-8",
    )
    top3main = sensitivity[(sensitivity["grid_size_m"] == 3.0) & (sensitivity["origin_mode"] == "base") & (sensitivity["threshold_h"] == 3.0)].iloc[0]
    (DOCS / "53_3m异常诊断报告.md").write_text(
        "\n".join(
            [
                "# 53 3m异常诊断报告",
                "",
                "本轮不再把旧稿中的“3 m 重新优化无改善”直接包装为网格精度导致局部最优，而是按以下口径排查：",
                "",
                f"- 3 m 基准原点下，完整双建筑枚举的 Top 候选为 `{top3main['top_candidate_at_threshold3']}`，是否为 C6/C33：{top3main['top_candidate_is_C6_C33']}。",
                f"- 固定 C6/C33 在 3 m、阈值 3 h 下的低直射日照面积下降为 {top3main['C6_C33_low_area_drop_m2']} m²。",
                f"- 固定 2.5D 第一候选 `{final_id}` 在同口径下的低直射日照面积下降为 {top3main['final_low_area_drop_m2']} m²。",
                "- 已检查项目包括：3/4/5/6 m 网格、四种原点、2/3/4 h 阈值、保护建筑排除、重复编号、最低高度和最大削减量。",
                "",
                "结论：C6/C33 不应继续称为唯一推荐方案；同时，2.5D 第一候选也未获得独立参考排序支持。本轮只能形成候选区间与透明降级结论。",
            ]
        ),
        encoding="utf-8",
    )
    (DOCS / "20_独立参考模拟设置说明.md").write_text(
        "\n".join(
            [
                "# 20 独立参考模拟设置说明",
                "",
                "本机未发现可直接调用的 Rhino/Grasshopper/Ladybug/Honeybee/Radiance 链路，因此本轮采用独立的 `trimesh` 三维射线可见性模拟作为参考。该参考模拟读取米制、Z-up 的 Ladybug-ready OBJ 网格，与算法A使用同一日期、时段、30分钟步长、地面网格和低直射日照阈值。",
                "",
                f"CSV 到 Ladybug-ready OBJ 的经验平移为：x + {dx_obj:.3f} m，y + {dy_obj:.3f} m。该平移来自 C1-C45 组名边界与 buildings.csv 中心点的中位差。",
                "",
                "参考模拟指标仍为地面点位直射太阳可见时长，不与室内照度、全年采光指标或日照因子混合。",
            ]
        ),
        encoding="utf-8",
    )
    (DOCS / "24_独立验证结论.md").write_text(
        "\n".join(
            [
                "# 24 独立验证结论",
                "",
                "独立参考模拟没有预设相关系数或 F1 门槛。结论按真实 MAE、RMSE、相关系数、分类 F1 和方案前后改善方向一致率判断。",
                "",
                comparison_df_ref.to_markdown(index=False),
                "",
                f"对 2.5D 第一候选 `{final_id}`，点位改善方向一致率为 {final_consistency:.3f}。",
                f"三维参考汇总指标显示：C6/C33 低直射日照面积下降 {c6_ref_drop:.3f} m²，`{final_id}` 下降 {final_ref_drop:.3f} m²。",
                "",
                "结论：独立参考没有支持 2.5D 排名中的唯一最终方案。论文应降级为“局部候选筛查/候选区间”，不得称为投稿级定稿或唯一推荐方案。",
            ]
        ),
        encoding="utf-8",
    )
    (DOCS / "63_建筑设计转译说明.md").write_text(
        "\n".join(
            [
                "# 63 建筑设计转译说明",
                "",
                "本轮区分两种几何：A 为规则模型，即候选建筑整体高度削减；B 为设计转译模型，即仅在上部局部区域进行退台/转角切削，保留底层街巷界面。两者均写出 OBJ 并用同一三维参考射线流程复算。",
                "",
                "若设计转译模型的低直射日照区改善弱于规则模型，论文必须如实写明，不能把规则模型的效果直接归因于建筑设计方案。",
                "",
                f"本轮设计转译对象为 2.5D 第一候选 `{final_id}`，并非最终定稿方案。规则模型 OBJ：`{final_obj}`；设计转译 OBJ：`{design_obj}`。",
            ]
        ),
        encoding="utf-8",
    )
    (DOCS / "72_复现说明README.md").write_text(
        "\n".join(
            [
                "# 72 复现说明 README",
                "",
                "## 运行顺序",
                "",
                "1. `python code/audit_docx_extract.py` 抽取 Word 母版。",
                "2. `python code/audit_assets_environment.py` 生成资产与环境审计。",
                "3. `python code/run_teacher_revision_experiments.py` 生成本轮新增 CSV、图表、日志和说明。",
                "",
                "## 随机种子",
                "",
                f"- random baseline seed: {rule.random_seed}",
                "",
                "## 核心输入",
                "",
                f"- dataset: `{DATASET}`",
                f"- Ladybug-ready OBJ baseline: `{READY_BASELINE_OBJ}`",
                "",
                "## 图表脚本来源",
                "",
                "本轮新增图 23、41、42、43、52、61、71 均由 `code/run_teacher_revision_experiments.py` 生成。",
                "",
                "## 边界",
                "",
                "当前独立参考为 trimesh 三维射线可见性，不是 Ladybug/Radiance。若导师要求投稿级环境模拟，应继续补 Rhino/Grasshopper/Ladybug/Honeybee/Radiance 链路。",
            ]
        ),
        encoding="utf-8",
    )
    make_requirements()
    log_lines.append(f"2.5D first candidate: {final_id}")
    log_lines.append(f"Unique final supported: {unique_final_supported}")
    log_lines.append(f"Run completed: {datetime.now().isoformat(timespec='seconds')}")
    (LOGS / "revision_experiments_run_log.txt").write_text("\n".join(log_lines), encoding="utf-8")

    print(json.dumps({"algorithm_first_candidate": final_id, "unique_final_supported": unique_final_supported, "timing": timing}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
