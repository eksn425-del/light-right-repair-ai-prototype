#!/usr/bin/env python3
"""Registered G3 ablation: fresh Shapely ray intersections versus blocker reuse.

This module never imports the legacy script (importing it loads private runtime
paths). Its actual ``min_projected_distance`` function is compiled from the
checked-in AST and called by the ONE intersection helper used by A and B.
A permits ordinary short-circuiting and shares ray/input preparation, but never
reuses any baseline/candidate blocker state to evaluate another candidate.
B computes original/reduced arrays once, then updates integer blocker counts.

The numerical API accepts synthetic fixtures ONLY for unit tests. The CLI has no
synthetic benchmark option; a verified real-input manifest is required before
it records timing or speedup. No raw geometry, sensor coordinates, or pointwise
visibility files are written. All CSVs carry the five required provenance keys.
Real-run scores always use the hash-verified frozen full630 reference ranges;
subset outcomes never refit them. Synthetic fixtures default to local ranges.

Manifest (paths relative to the manifest, SHA256 is over exact file bytes)::
  {"measurement_class":"REAL_SITE", "site":"Xiamen Guankou lakeside",
   "source_run":"baseline_20260909_clean", "units":"m", "north_deg":0,
   "coordinate_frame":"author's documented local metric frame",
   "private_runtime_authorized":true, "sensor_order_preserved":true,
   "solar_mode":"historical_verified", "solar_verified":true,
   "inputs":{"building_csv":{"path":"...", "sha256":"..."},
             "geometry_geojson":{"path":"...", "sha256":"..."},
             "sensors_csv":{"path":"...", "sha256":"..."},
             "solar_csv":{"path":"...", "sha256":"..."}}}

Historical solar CSV columns: time, apparent_elevation_deg, dx, dy,
 tan_altitude (azimuth_deg optional). Time must include a UTC offset.
Alternatively an explicitly new solar version can be registered with
solar_mode="new_pvlib_protocol", solar_version nonempty. It is NOT a verified
historical replay; a provided solar_csv is rejected for that mode to avoid
silently ignoring it. Sensor columns: sensor_id (or original grid_id), x,y,z.
The 45 canonical attributes must agree with the frozen table, and the original
2031 sensors retain unique IDs, coordinates, and order. Neither dimensions nor
an author's provenance declaration independently proves physical accuracy.

Usage:
  python matched_ablation.py --manifest /private/input_manifest.json
  python matched_ablation.py --write-blocked  # honest absent-input records

No change to production files or historical results is made.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
try:
    import resource
except ImportError:  # Windows has no Unix resource module.
    resource = None
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

# Set before importing numerical libraries in the CLI. There is no multiprocessing.
THREAD_ENV_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                   "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
if __name__ == "__main__":
    for _key in THREAD_ENV_KEYS:
        os.environ[_key] = "1"

import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point, shape

SPRINT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SPRINT_ROOT.parent
DEFAULT_PROTOCOL = SPRINT_ROOT / "configs/ICORES_PROTOCOL.json"
PRODUCTION_SOURCE = REPO_ROOT / "research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py"
CANONICAL_BUILDINGS = REPO_ROOT / "project_archive_2026_10_16/research/data/derived/canonical_site_v2/canonical_buildings.csv"
SOURCE_CODE_COMMIT = "ae7483ca493768e23a19cf402446c54d6f6c95ef"
PROVENANCE_KEYS = ("run_id", "config_hash", "code_commit", "input_hash", "measurement_class")
PHASES = ("load", "solar", "precompute", "evaluation", "ranking_pareto", "io", "end_to_end")
METRIC_COLUMNS = ("A", "H", "V", "N")
NORMALIZATION_SOURCE = "paper_assets/tables/table_03_candidate_universe.csv"
NORMALIZATION_COLUMNS = {"A": "low_area_drop_h3_m2", "H": "avg_gain_vs_baseline_h",
                         "V": "intervention_volume_m3", "N": "new_low_area_h3_m2"}
REAL_MEASUREMENT = "MEASURED_REAL_SITE"
SYNTHETIC_MEASUREMENT = "SYNTHETIC_UNIT_TEST_ONLY"


class ReadinessError(ValueError):
    """Missing, mismatched, or insufficiently attributed real-site inputs."""


@dataclass
class EvaluationResult:
    method: str
    baseline_hours: np.ndarray
    candidate_hours: np.ndarray
    metrics: pd.DataFrame
    phase_seconds: dict[str, float]
    primitive_calls: int
    measurement_class: str = SYNTHETIC_MEASUREMENT
    metadata: dict[str, Any] = field(default_factory=dict)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _json_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def load_production_primitive(path: str | Path | None = None) -> Callable:
    """Compile only the actual recursive primitive, without legacy runtime I/O."""
    source = Path(path or PRODUCTION_SOURCE)
    module = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    nodes = [node for node in module.body if isinstance(node, ast.FunctionDef)
             and node.name == "min_projected_distance"]
    if len(nodes) != 1:
        raise ReadinessError("Production min_projected_distance must occur exactly once")
    isolated = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(isolated)
    namespace: dict[str, Any] = {"Point": Point}
    exec(compile(isolated, str(source), "exec"), namespace)
    return namespace["min_projected_distance"]


def strict_bool(value: Any) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if value is None or pd.isna(value):
        raise ValueError("Missing boolean")
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y", "on"}:
        return True
    if text in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid strict boolean: {value!r}")


def _natural_key(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", str(value)))


def _pair_key(pair: Sequence[str]) -> tuple:
    return tuple(_natural_key(item) for item in pair)


def reduced_height(height: float, analysis: Mapping[str, Any]) -> float:
    return max(float(analysis["height_floor_m"]), float(height) -
               min(float(analysis["height_cap_m"]), float(analysis["height_fraction"]) * float(height)))


def _daylight(solar: pd.DataFrame) -> np.ndarray:
    elevation = solar["apparent_elevation_deg"].to_numpy(dtype=float)
    if not np.isfinite(elevation).all():
        raise ValueError("Solar elevation must be finite")
    return elevation > 0.0


def hours_from_blocked(blocked: np.ndarray, sensor_count: int,
                       solar: pd.DataFrame, timestep_minutes: float) -> np.ndarray:
    """Night is never visible, including the zero-blocker/all-clear case."""
    if not np.isfinite(timestep_minutes) or timestep_minutes <= 0:
        raise ValueError("timestep_minutes must be positive and finite")
    blocked = np.asarray(blocked, dtype=bool)
    if sensor_count <= 0 or len(solar) <= 0 or blocked.size != sensor_count * len(solar):
        raise ValueError("Blocked array does not match sensor and solar dimensions")
    visible = ~blocked.reshape(sensor_count, len(solar)) & _daylight(solar)[None, :]
    return visible.sum(axis=1).astype(float) * float(timestep_minutes) / 60.0


def _validate_frames(buildings: pd.DataFrame, grid: pd.DataFrame,
                     geoms: Mapping[str, Any], solar: pd.DataFrame) -> None:
    for frame, columns, name in (
        (buildings, ("building_id", "height_m", "canonical_area_m2"), "building"),
        (grid, ("sensor_id", "x", "y", "z"), "sensor"),
        (solar, ("apparent_elevation_deg", "dx", "dy", "tan_altitude"), "solar"),
    ):
        absent = sorted(set(columns) - set(frame.columns))
        if absent or frame.empty:
            raise ValueError(f"Invalid {name} table: missing columns {absent} or empty table")
    ids = buildings["building_id"].astype(str)
    if ids.duplicated().any() or buildings["building_id"].isna().any() or set(ids) != set(geoms):
        raise ValueError("Building IDs must be unique and match footprint IDs exactly")
    sid = grid["sensor_id"]
    if sid.isna().any() or sid.astype(str).str.strip().eq("").any() or sid.astype(str).duplicated().any():
        raise ValueError("Sensor IDs must be present and unique")
    xyz = grid[["x", "y", "z"]].to_numpy(float)
    if not np.isfinite(xyz).all() or grid[["x", "y", "z"]].duplicated().any():
        raise ValueError("Sensor coordinates must be finite and unambiguous")
    attrs = buildings[["height_m", "canonical_area_m2"]].to_numpy(float)
    if not np.isfinite(attrs).all() or (attrs[:, 0] < 0).any() or (attrs[:, 1] <= 0).any():
        raise ValueError("Heights must be nonnegative, and areas positive and finite")
    for bid, geom in geoms.items():
        if geom.geom_type not in {"Polygon", "MultiPolygon"} or geom.is_empty or not geom.is_valid:
            raise ValueError(f"Invalid polygonal footprint for building {bid}; no silent repair")
        if not np.isfinite(geom.bounds).all():
            raise ValueError(f"Nonfinite footprint for building {bid}")
    values = solar[["apparent_elevation_deg", "dx", "dy", "tan_altitude"]].to_numpy(float)
    if not np.isfinite(values).all():
        raise ValueError("Solar values must all be finite")
    daylight = _daylight(solar)
    if daylight.any():
        directions = values[daylight, 1:3]
        if not np.allclose(np.linalg.norm(directions, axis=1), 1.0, rtol=0, atol=1e-9):
            raise ValueError("Solar horizontal directions must be unit vectors")
        if (values[daylight, 3] <= 0).any():
            raise ValueError("Positive solar elevation requires positive tan_altitude")


def _prepare_rays(grid: pd.DataFrame, geoms: Mapping[str, Any], solar: pd.DataFrame) -> list:
    """Shared ray construction; no blocker state or intersections are cached."""
    bounds = np.asarray([geom.bounds for geom in geoms.values()], dtype=float)
    minx, miny = bounds[:, :2].min(axis=0)
    maxx, maxy = bounds[:, 2:].max(axis=0)
    # Exactly the production ray-length convention; do not silently change physics.
    ray_length = math.hypot(maxx - minx, maxy - miny) + 100.0
    observations = []
    for i, sensor in enumerate(grid.itertuples(index=False)):
        origin = Point(float(sensor.x), float(sensor.y))
        for j, sun in enumerate(solar.itertuples(index=False)):
            if float(sun.apparent_elevation_deg) <= 0:
                continue
            dx, dy = float(sun.dx), float(sun.dy)
            ray = LineString([(origin.x, origin.y),
                              (origin.x + dx * ray_length, origin.y + dy * ray_length)])
            observations.append((i * len(solar) + j, origin, ray, dx, dy,
                                 float(sun.tan_altitude), float(sensor.z)))
    return observations


def _ray_height(observation: tuple, geom: Any, primitive: Callable) -> tuple[float | None, int]:
    """The ONE Shapely intersection path used by both methods (legacy semantics)."""
    _, origin, ray, dx, dy, tan_altitude, z = observation
    if geom.contains(origin):
        return None, 0
    intersection = ray.intersection(geom)
    distance = primitive(intersection, origin, dx, dy)
    return (None if distance is None else z + tan_altitude * distance), 1


def _fresh_blocked(heights: np.ndarray, ordered_geoms: list, observations: list,
                   n_obs: int, primitive: Callable) -> tuple[np.ndarray, int]:
    blocked = np.zeros(n_obs, dtype=bool)
    calls = 0
    for observation in observations:
        for height, geom in zip(heights, ordered_geoms):
            ray_height, count = _ray_height(observation, geom, primitive)
            calls += count
            if ray_height is not None and ray_height <= height + 1e-9:
                blocked[observation[0]] = True
                break  # A retains its ordinary first-blocker short-circuit.
    return blocked, calls


def _precompute_blockers(heights: np.ndarray, reduced: np.ndarray, ordered_geoms: list,
                         observations: list, n_obs: int, primitive: Callable) -> tuple:
    original = np.zeros((len(heights), n_obs), dtype=np.uint8)
    lowered = np.zeros_like(original)
    calls = 0
    for observation in observations:
        for i, (height, low, geom) in enumerate(zip(heights, reduced, ordered_geoms)):
            ray_height, count = _ray_height(observation, geom, primitive)
            calls += count
            if ray_height is not None:
                original[i, observation[0]] = ray_height <= height + 1e-9
                lowered[i, observation[0]] = ray_height <= low + 1e-9
    return original, lowered, calls


def load_normalization_reference(protocol: Mapping[str, Any]) -> tuple[dict, dict]:
    """Read the immutable full630 scoring range once, never fit to a subset.

    Returned bounds are not clipped or adapted to newly observed outcomes.
    Reference table loading is run-level provenance preparation, outside the
    matched per-method measurements; both methods receive the same constants.
    """
    path = REPO_ROOT / NORMALIZATION_SOURCE
    expected = protocol.get("source_table_hashes", {}).get(NORMALIZATION_SOURCE)
    if not expected or not path.is_file():
        raise ReadinessError("Frozen full630 normalization source/hash unavailable or mismatched")
    actual_hash = sha256_file(path)
    if actual_hash != expected:
        amendment_path = SPRINT_ROOT / 'configs/LOCAL_INPUT_IDENTITY_AMENDMENT.json'
        if not amendment_path.is_file():
            raise ReadinessError("Frozen full630 normalization source/hash unavailable or mismatched")
        amendment = json.loads(amendment_path.read_text(encoding='utf-8'))
        entry = amendment.get('normalization_reference', {})
        if (amendment.get('protocol_sha256') != sha256_file(DEFAULT_PROTOCOL)
                or entry.get('registered_hash') != expected
                or entry.get('committed_file_sha256') != actual_hash
                or entry.get('path') != NORMALIZATION_SOURCE):
            raise ReadinessError('Normalization identity amendment does not authorize these exact bytes')
        reference_path = REPO_ROOT / entry['independent_frozen_reference_path']
        if sha256_file(reference_path) != entry['independent_frozen_reference_sha256']:
            raise ReadinessError('Independent frozen reference hash mismatch')
        left = pd.read_csv(path).set_index('building_ids').sort_index()
        right = pd.read_csv(reference_path).set_index('building_ids').sort_index()
        if not left.index.equals(right.index) or len(left) != 630:
            raise ReadinessError('Amended reference pair identities differ')
        for column in [*NORMALIZATION_COLUMNS.values(), 'score']:
            if not np.allclose(left[column].to_numpy(float), right[column].to_numpy(float),
                               rtol=0, atol=float(protocol['tolerances']['metric_abs'])):
                raise ReadinessError('Amended normalization reference differs from frozen values')
    frame = pd.read_csv(path)
    if len(frame) != 630 or "building_ids" not in frame:
        raise ReadinessError("Full630 normalization reference has invalid dimensions")
    pairs = [tuple(str(value).split(",")) for value in frame.building_ids]
    registered = [tuple(pair) for pair in protocol["benchmark"]["candidate_order"]]
    if len(set(pairs)) != 630 or set(pairs) != set(registered):
        raise ReadinessError("Full630 normalization reference pair universe differs from protocol")
    bounds = {}
    for metric, column in NORMALIZATION_COLUMNS.items():
        if column not in frame:
            raise ReadinessError(f"Frozen normalization reference lacks {column}")
        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ReadinessError("Frozen normalization reference has nonfinite metrics")
        bounds[metric] = (float(values.min()), float(values.max()))
    provenance = {"normalization_basis": "FROZEN_FULL630_REFERENCE",
                  "normalization_source": NORMALIZATION_SOURCE,
                  "normalization_source_sha256": actual_hash,
                  "protocol_registered_source_sha256": expected,
                  "normalization_identity_amendment": actual_hash != expected,
                  "normalization_bounds_json": json.dumps(bounds, sort_keys=True),
                  "normalization_bounds_sha256": _json_hash(bounds),
                  "normalization_out_of_range_policy": "No clipping or outcome-adaptive refitting"}
    return bounds, provenance


def _rank_metrics(metrics: pd.DataFrame, weights: Sequence[float],
                  normalization_bounds: Mapping[str, Sequence[float]] | None = None) -> pd.DataFrame:
    weights = np.asarray(weights, dtype=float)
    if weights.shape != (4,) or not np.isfinite(weights).all() or (weights < 0).any() or not np.isclose(weights.sum(), 1, atol=1e-9, rtol=0):
        raise ValueError("Four nonnegative production weights must sum to one")
    result = metrics.copy()
    if normalization_bounds is not None and set(normalization_bounds) != set(METRIC_COLUMNS):
        raise ValueError("Normalization bounds must provide exactly A, H, V, N")
    for column in METRIC_COLUMNS:
        low, high = (result[column].min(), result[column].max()) if normalization_bounds is None else normalization_bounds[column]
        if not np.isfinite([low, high]).all() or high < low:
            raise ValueError(f"Invalid fixed normalization bounds for {column}")
        result[column + "_norm"] = 0.0 if abs(high - low) < 1e-12 else (result[column] - low) / (high - low)
    # The cost complements are essential: the legacy score is not a signed sum.
    result["score"] = (weights[0] * result.A_norm + weights[1] * result.H_norm +
                       weights[2] * (1 - result.V_norm) + weights[3] * (1 - result.N_norm))
    result["is_pareto_front"] = [not (((result.V <= row.V) & (result.A >= row.A)) &
                                     ((result.V < row.V) | (result.A > row.A))).any()
                                  for row in result.itertuples(index=False)]
    order = sorted(range(len(result)), key=lambda i: (-float(result.iloc[i]["score"]),
                   _pair_key(str(result.iloc[i]["pair"]).split(","))))
    rank = np.empty(len(result), dtype=int)
    rank[order] = np.arange(1, len(result) + 1)
    result["rank"] = rank
    return result


def evaluate_method(method: str, buildings: pd.DataFrame, grid: pd.DataFrame,
                    geoms: Mapping[str, Any], solar: pd.DataFrame,
                    candidates: Sequence[Sequence[str]], analysis: Mapping[str, Any],
                    weights: Sequence[float] = (.45, .35, .15, .05),
                    normalization_bounds: Mapping[str, Sequence[float]] | None = None) -> EvaluationResult:
    """Numerical unit-test API. Results are always synthetic/unpublished here.

    Candidate rows retain the supplied order; `rank` uses descending score then
    natural numeric pair order. Pointwise DSH is returned only in memory.
    Real-input validation, file I/O and total timing are supplied by the CLI.
    The default normalization fits only this synthetic fixture. Real runs must
    supply the hash-verified fixed full630 reference bounds, shared by A and B.
    """
    if method not in {"A", "B"}:
        raise ValueError("method must be A or B")
    started = time.perf_counter()
    grid = grid.rename(columns={"grid_id": "sensor_id"}) if "sensor_id" not in grid else grid
    _validate_frames(buildings, grid, geoms, solar)
    heights = buildings.height_m.to_numpy(dtype=float)
    reduced = np.asarray([reduced_height(h, analysis) for h in heights])
    if (reduced > heights + 1e-9).any():
        # Noneligible buildings below the height floor are never modified.
        reduced = np.minimum(reduced, heights)
    areas = buildings.canonical_area_m2.to_numpy(dtype=float)
    ids = buildings.building_id.astype(str).tolist()
    indices = {bid: i for i, bid in enumerate(ids)}
    candidates = [tuple(str(v) for v in pair) for pair in candidates]
    if not candidates or any(len(p) != 2 or p[0] == p[1] for p in candidates):
        raise ValueError("Candidates must be nonempty two-distinct-building pairs")
    if len({frozenset(p) for p in candidates}) != len(candidates):
        raise ValueError("Candidate pairs must be unique")
    if any(bid not in indices for pair in candidates for bid in pair):
        raise ValueError("Candidate contains an unknown building")
    ordered_geoms = [geoms[bid] for bid in ids]
    primitive = load_production_primitive()
    phases = {phase: 0.0 for phase in PHASES}
    phases["load"] = time.perf_counter() - started
    phase_start = time.perf_counter()
    observations = _prepare_rays(grid, geoms, solar)
    phases["solar"] = time.perf_counter() - phase_start
    n_obs = len(grid) * len(solar)
    calls = 0
    phase_start = time.perf_counter()
    if method == "B":
        original, lowered, calls = _precompute_blockers(heights, reduced, ordered_geoms, observations, n_obs, primitive)
        base_count = original.sum(axis=0, dtype=np.int32)
        phases["precompute"] = time.perf_counter() - phase_start
        phase_start = time.perf_counter()
        baseline_blocked = base_count > 0
    else:
        baseline_blocked, count = _fresh_blocked(heights, ordered_geoms, observations, n_obs, primitive)
        calls += count
    baseline = hours_from_blocked(baseline_blocked, len(grid), solar, float(analysis["step_minutes"]))
    threshold = float(analysis["threshold_h"])
    cell_area = float(analysis["grid_m"]) ** 2
    baseline_low = float((baseline < threshold).sum() * cell_area)
    candidate_hours, rows = [], []
    for pair in candidates:
        ia, ib = (indices[bid] for bid in pair)
        if method == "A":
            modified = heights.copy()
            modified[[ia, ib]] = reduced[[ia, ib]]
            blocked, count = _fresh_blocked(modified, ordered_geoms, observations, n_obs, primitive)
            calls += count
        else:
            counts = base_count - original[ia] - original[ib] + lowered[ia] + lowered[ib]
            if (counts < 0).any():
                raise AssertionError("Negative blocker count")
            blocked = counts > 0
        hours = hours_from_blocked(blocked, len(grid), solar, float(analysis["step_minutes"]))
        candidate_hours.append(hours)
        rows.append({"pair": ",".join(pair),
                     "A": baseline_low - float((hours < threshold).sum() * cell_area),
                     "H": float((hours - baseline).mean()),
                     "V": float(sum(areas[i] * (heights[i] - reduced[i]) for i in (ia, ib))),
                     "N": float(((baseline >= threshold) & (hours < threshold)).sum() * cell_area)})
    phases["evaluation"] = time.perf_counter() - phase_start
    phase_start = time.perf_counter()
    metrics = _rank_metrics(pd.DataFrame(rows), weights, normalization_bounds)
    phases["ranking_pareto"] = time.perf_counter() - phase_start
    phases["end_to_end"] = time.perf_counter() - started
    return EvaluationResult(method, baseline, np.asarray(candidate_hours), metrics, phases, calls,
                            metadata={"ranking_ties": "descending score then natural numeric pair order",
                                      "normalization_basis": "SYNTHETIC_WITHIN_FIXTURE_ONLY" if normalization_bounds is None else "FIXED_REFERENCE_BOUNDS",
                                      "normalization_bounds": None if normalization_bounds is None else dict(normalization_bounds),
                                      "normalization_outside_reference": {} if normalization_bounds is None else
                                          {column: int(((metrics[column] < normalization_bounds[column][0] - 1e-12) |
                                                       (metrics[column] > normalization_bounds[column][1] + 1e-12)).sum())
                                           for column in METRIC_COLUMNS},
                                      "production_source_sha256": sha256_file(PRODUCTION_SOURCE),
                                      "daylight_samples": int(_daylight(solar).sum()),
                                      "pointwise_DSH_retention": "memory only; no raw sensors exported"})


def compare_results(a: EvaluationResult, b: EvaluationResult,
                    tolerances: Mapping[str, Any]) -> dict[str, Any]:
    """Check pointwise DSH, A/H/V/N, score, exact rank and Pareto flags."""
    result: dict[str, Any] = {}
    if a.metrics.pair.tolist() != b.metrics.pair.tolist() or a.candidate_hours.shape != b.candidate_hours.shape or a.baseline_hours.shape != b.baseline_hours.shape:
        return {"equal": False, "pair_order_equal": False, "reason": "candidate/sensor shape or pair-order mismatch"}
    result["pair_order_equal"] = True
    result["baseline_DSH_max_abs_error"] = float(np.max(np.abs(a.baseline_hours - b.baseline_hours)))
    result["pointwise_DSH_max_abs_error"] = float(np.max(np.abs(a.candidate_hours - b.candidate_hours)))
    result["baseline_DSH_equal"] = result["baseline_DSH_max_abs_error"] <= float(tolerances["dsh_h_abs"])
    result["pointwise_DSH_equal"] = result["pointwise_DSH_max_abs_error"] <= float(tolerances["dsh_h_abs"])
    for column in (*METRIC_COLUMNS, "score"):
        difference = np.abs(a.metrics[column].to_numpy(float) - b.metrics[column].to_numpy(float))
        result[column + "_max_abs_error"] = float(difference.max())
        tol = (tolerances["score_abs"] if column == "score" else
               tolerances["volume_m3_abs"] if column == "V" else tolerances["metric_abs"])
        result[column + "_equal"] = bool(np.isfinite(difference).all() and difference.max() <= float(tol))
    result["ranking_equal"] = bool(np.array_equal(a.metrics["rank"], b.metrics["rank"]))
    result["pareto_equal"] = bool(np.array_equal(a.metrics["is_pareto_front"], b.metrics["is_pareto_front"]))
    result["equal"] = all(value for key, value in result.items() if key.endswith("_equal"))
    return result


def _expected_times(analysis: Mapping[str, Any]) -> pd.DatetimeIndex:
    times = pd.date_range(f"{analysis['date']} {analysis['times_local'][0]}",
                          f"{analysis['date']} {analysis['times_local'][1]}",
                          freq=f"{analysis['step_minutes']}min", tz=analysis["timezone"])
    if len(times) != int(analysis["sample_count"]):
        raise ReadinessError("Registered sample_count conflicts with date/time interval")
    return times


def _new_solar(analysis: Mapping[str, Any]) -> pd.DataFrame:
    import pvlib
    times = _expected_times(analysis)
    solar = pvlib.solarposition.get_solarposition(times, analysis["latitude"], analysis["longitude"])
    altitude, azimuth = solar.apparent_elevation.to_numpy(float), solar.azimuth.to_numpy(float)
    return pd.DataFrame({"time": [stamp.isoformat() for stamp in times],
                         "apparent_elevation_deg": altitude, "azimuth_deg": azimuth,
                         "dx": np.sin(np.radians(azimuth)), "dy": np.cos(np.radians(azimuth)),
                         "tan_altitude": np.tan(np.radians(altitude))})


def _verified_paths(manifest: Mapping[str, Any], base: Path) -> tuple[dict, dict]:
    required = ["building_csv", "geometry_geojson", "sensors_csv"]
    mode = manifest.get("solar_mode")
    if mode == "historical_verified":
        required.append("solar_csv")
        if manifest.get("solar_verified") is not True:
            raise ReadinessError("Historical solar requires solar_verified=true provenance")
    elif mode == "new_pvlib_protocol":
        if not isinstance(manifest.get("solar_version"), str) or not manifest["solar_version"].strip():
            raise ReadinessError("New pvlib solar requires an explicit nonempty solar_version")
        if "solar_csv" in manifest.get("inputs", {}):
            raise ReadinessError("new_pvlib_protocol cannot silently ignore a supplied solar_csv")
    else:
        raise ReadinessError("Explicit historical_verified or new_pvlib_protocol solar_mode required")
    paths, hashes = {}, {}
    for key in required:
        entry = manifest.get("inputs", {}).get(key, {})
        expected = entry.get("sha256", "")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            raise ReadinessError(f"Missing/invalid SHA256 for {key}")
        if not isinstance(entry.get("path"), str) or not entry["path"].strip():
            raise ReadinessError(f"Missing private input path for {key}")
        path = Path(entry["path"]).expanduser()
        path = path if path.is_absolute() else base / path
        if not path.is_file():
            raise ReadinessError(f"Required private input unavailable: {key}")
        actual = sha256_file(path)
        if actual.lower() != expected.lower():
            raise ReadinessError(f"Input SHA256 mismatch: {key}")
        paths[key], hashes[key] = path, actual
    return paths, hashes


def load_real_inputs(manifest_path: str | Path, protocol: Mapping[str, Any]) -> tuple:
    """Return buildings, footprints, ordered sensors, verified/new solar, input_hash.

    Fails closed. Does not repair geometry, infer IDs, reorder sensors, generate
    sensors, or substitute aggregate tables for footprints. New pvlib solar is
    only created after explicit provenance permission; solar.attrs records mode.
    """
    started = time.perf_counter()
    if manifest_path is None or not Path(manifest_path).is_file():
        raise ReadinessError("Missing private provenance manifest; real geometry/sensor inputs are not established")
    manifest_path = Path(manifest_path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest.get("measurement_class") != "REAL_SITE" or manifest.get("synthetic", False) is not False:
            raise ReadinessError("Synthetic/toy data cannot be marked as a real-site benchmark")
        for key in ("source_run", "coordinate_frame"):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                raise ReadinessError(f"Missing provenance field: {key}")
        if manifest.get("source_run") != "baseline_20260909_clean":
            raise ReadinessError("Inputs must identify their canonical baseline_20260909_clean source")
        if manifest.get("site") != protocol["site"] or manifest.get("units") != "m":
            raise ReadinessError("Site and metric-unit provenance must match the protocol")
        if manifest.get("north_deg") != protocol["analysis"]["north_deg"]:
            raise ReadinessError("North orientation does not match the registered analysis")
        if float(protocol["analysis"]["north_deg"]) != 0:
            raise ReadinessError("This wrapper preserves the current north=0 production convention only")
        for key in ("private_runtime_authorized", "sensor_order_preserved"):
            if manifest.get(key) is not True:
                raise ReadinessError(f"Explicit {key}=true is required")
        paths, hashes = _verified_paths(manifest, manifest_path.parent)
        for protocol_key, input_key in (("source_geometry_sha256", "geometry_geojson"),
                                        ("source_sensors_sha256", "sensors_csv")):
            if protocol.get(protocol_key) and protocol[protocol_key] != hashes[input_key]:
                raise ReadinessError(f"Frozen protocol hash mismatch: {input_key}")
        buildings = pd.read_csv(paths["building_csv"], dtype={"building_id": str})
        sensors = pd.read_csv(paths["sensors_csv"], dtype={"sensor_id": str, "grid_id": str})
        if "sensor_id" not in sensors and "grid_id" in sensors:
            sensors = sensors.rename(columns={"grid_id": "sensor_id"})
        elif "sensor_id" in sensors and "grid_id" in sensors and not sensors.sensor_id.equals(sensors.grid_id):
            raise ReadinessError("Conflicting sensor_id and grid_id mapping")
        features = json.loads(paths["geometry_geojson"].read_text(encoding="utf-8-sig"))
        geoms = {}
        if features.get("type") != "FeatureCollection":
            raise ReadinessError("Footprints must be a canonical GeoJSON FeatureCollection")
        for feature in features.get("features", []):
            bid = feature.get("properties", {}).get("building_id")
            if bid is None or str(bid) in geoms:
                raise ReadinessError("Footprints require exactly one unique feature per canonical building ID")
            geoms[str(bid)] = shape(feature["geometry"])
        if len(buildings) != 45 or len(geoms) != 45 or len(sensors) != 2031:
            raise ReadinessError("Real-site input requires 45 buildings/footprints and 2031 ordered sensors; toy input refused")
        if not CANONICAL_BUILDINGS.is_file():
            raise ReadinessError("Frozen canonical attribute reference is unavailable")
        reference = pd.read_csv(CANONICAL_BUILDINGS, dtype={"building_id": str}).set_index("building_id")
        incoming = buildings.set_index("building_id")
        if incoming.index.has_duplicates or set(incoming.index) != set(reference.index):
            raise ReadinessError("Canonical building IDs do not match the frozen reference")
        for column in ("height_m", "canonical_area_m2"):
            if not np.allclose(incoming.loc[reference.index, column].to_numpy(float), reference[column].to_numpy(float), rtol=0,
                               atol=float(protocol["tolerances"]["metric_abs"])):
                raise ReadinessError(f"Canonical building {column} differs from frozen source")
        for column in ("movable", "protected"):
            lhs = [strict_bool(v) for v in incoming.loc[reference.index, column]]
            rhs = [strict_bool(v) for v in reference[column]]
            if lhs != rhs:
                raise ReadinessError(f"Canonical strict eligibility differs: {column}")
        eligible = [str(row.building_id) for row in buildings.itertuples(index=False)
                    if strict_bool(row.movable) and not strict_bool(row.protected)
                    and float(row.height_m) > float(protocol["analysis"]["height_floor_m"])]
        expected_pairs = [tuple(pair) for pair in protocol["benchmark"]["candidate_order"]]
        eligible = sorted(eligible, key=_natural_key)
        if len(eligible) != 36 or list(itertools.combinations(eligible, 2)) != expected_pairs:
            raise ReadinessError("Eligible 36-building universe does not match all 630 registered pairs/order")
        if not np.allclose(sensors.z.to_numpy(float), float(protocol["analysis"]["sensor_height_m"]), rtol=0,
                           atol=float(protocol["tolerances"]["coordinate_m"])):
            raise ReadinessError("Sensor elevation differs from the registered 0.1 m grid")
        for bid, geom in geoms.items():
            actual, expected = float(geom.area), float(incoming.loc[bid, "canonical_area_m2"])
            tol = max(float(protocol["tolerances"]["outside_area_m2_abs"]), expected * float(protocol["tolerances"]["outside_area_relative"]))
            if abs(actual - expected) > tol:
                raise ReadinessError(f"Canonical footprint area mismatch: {bid}")
        load_seconds = time.perf_counter() - started
        solar_started = time.perf_counter()
        if manifest["solar_mode"] == "historical_verified":
            solar = pd.read_csv(paths["solar_csv"])
            if "time" not in solar:
                raise ReadinessError("Historical solar requires exact timezone-aware sample times")
            # Reject naive timestamps instead of letting pandas assume UTC.
            if any(pd.Timestamp(value).tzinfo is None for value in solar.time):
                raise ReadinessError("Historical solar timestamps must include timezone offsets")
            times = pd.DatetimeIndex(pd.to_datetime(solar.time, utc=True))
            if not times.equals(_expected_times(protocol["analysis"]).tz_convert("UTC")):
                raise ReadinessError("Historical solar times/order differ from registered samples")
        else:
            solar = _new_solar(protocol["analysis"])
        if len(solar) != 16:
            raise ReadinessError("Registered real-site solar requires 16 samples")
        _validate_frames(buildings, sensors, geoms, solar)
        if not np.allclose(solar.tan_altitude.to_numpy(float),
                           np.tan(np.radians(solar.apparent_elevation_deg.to_numpy(float))), atol=1e-9, rtol=1e-9):
            raise ReadinessError("Solar elevation and tangent columns are inconsistent")
        solar_seconds = time.perf_counter() - solar_started
        provenance = {key: manifest[key] for key in ("site", "source_run", "units", "north_deg",
                      "coordinate_frame", "private_runtime_authorized", "sensor_order_preserved", "solar_mode")}
        provenance["file_hashes"] = hashes
        if manifest["solar_mode"] == "new_pvlib_protocol":
            provenance["solar_version"] = manifest["solar_version"]
            provenance["solar_generated_values_hash"] = _json_hash(solar.to_dict(orient="list"))
        input_hash = _json_hash(provenance)
        solar.attrs.update({"input_hash": input_hash, "solar_mode": manifest["solar_mode"],
                            "load_seconds": load_seconds, "solar_seconds": solar_seconds,
                            "source_hashes": hashes, "real_inputs_verified": True})
        return buildings, geoms, sensors, solar, input_hash
    except ReadinessError:
        raise
    except (KeyError, TypeError, ValueError, OSError) as exc:
        # Private filesystem paths/raw input values must not enter publishable logs.
        raise ReadinessError(f"Invalid/incomplete real input package ({type(exc).__name__}); inspect privately") from exc


def validate_real_inputs(buildings_path: str | Path, footprints_path: str | Path,
                         sensors_path: str | Path, manifest_path: str | Path,
                         protocol: Mapping[str, Any]) -> tuple:
    """Compatibility entry point; explicit paths must be the verified manifest paths."""
    result = load_real_inputs(manifest_path, protocol)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
    paths, _ = _verified_paths(manifest, Path(manifest_path).parent)
    for name, supplied in (("building_csv", buildings_path), ("geometry_geojson", footprints_path), ("sensors_csv", sensors_path)):
        if Path(supplied).resolve() != paths[name].resolve():
            raise ReadinessError(f"Supplied path does not match verified manifest: {name}")
    return result


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]], metadata: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame([{**row, **metadata} for row in rows])
    for key in PROVENANCE_KEYS:
        if key not in frame:
            frame[key] = metadata.get(key, "")
    frame.to_csv(path, index=False)


def speedup_if_equal(a_seconds: float, b_seconds: float, equivalence: Mapping[str, Any],
                     measurement_class: str) -> float:
    if measurement_class != REAL_MEASUREMENT:
        raise ValueError("Speedup reporting is forbidden for synthetic/unit-test data")
    if equivalence.get("equal") is not True:
        raise ValueError("Matched A/B equality is required before reporting speedup")
    if not all(np.isfinite(v) and v > 0 for v in (a_seconds, b_seconds)):
        raise ValueError("Speedup requires positive measured end-to-end times")
    return float(a_seconds / b_seconds)


def write_blocked(output_dir: str | Path, metadata: Mapping[str, Any], protocol: Mapping[str, Any], reason: str) -> None:
    """Absence is represented by blanks, never zero measured time/error/speedup."""
    output_dir = Path(output_dir)
    metadata = {**metadata, "measurement_class": "BLOCKED_NO_REAL_INPUTS", "input_hash": ""}
    runtime_rows, summary_rows, equality_rows = [], [], []
    for size in protocol["benchmark"]["subset_prefix_sizes"]:
        for method in ("A", "B"):
            runtime_rows.append({"method": method, "subset_size": size, "repeat_id": "", "warmup": "",
                                 "status": "BLOCKED_MISSING_REAL_INPUTS", "reason": reason,
                                 **{phase + "_seconds": "" for phase in PHASES},
                                 "primitive_calls": "", "started_utc": "", "ended_utc": ""})
        summary_rows.append({"subset_size": size, "planned_repetitions": protocol["benchmark"]["repetitions"],
                             "completed_matched_repetitions": "", "A_median_end_to_end_seconds": "",
                             "B_median_end_to_end_seconds": "", "measured_speedup": "",
                             "all_equal": "", "status": "BLOCKED_MISSING_REAL_INPUTS", "reason": reason})
        equality_rows.append({"subset_size": size, "repeat_id": "", "equal": "",
                              **{column + "_max_abs_error": "" for column in ("pointwise_DSH", "A", "H", "V", "N", "score")},
                              "ranking_equal": "", "status": "NOT_MEASURED", "reason": reason})
    _write_csv(output_dir / "ablation_runtime_records.csv", runtime_rows, metadata)
    _write_csv(output_dir / "ablation_summary.csv", summary_rows, metadata)
    _write_csv(output_dir / "ablation_equivalence.csv", equality_rows, metadata)


def _memory_record() -> dict[str, Any]:
    """No Windows peak-memory claim: distinguish current RSS from high-water RSS."""
    if resource is not None:
        usage = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # macOS reports bytes; Linux reports KiB.
        peak_kib = usage / 1024.0 if sys.platform == "darwin" else usage
        return {"peak_rss_kib": peak_kib, "current_rss_kib": "",
                "memory_measurement": "PROCESS_CUMULATIVE_PEAK_RSS"}
    try:
        import psutil
        return {"peak_rss_kib": "", "current_rss_kib": psutil.Process().memory_info().rss / 1024.0,
                "memory_measurement": "CURRENT_RSS_NOT_PEAK"}
    except (ImportError, OSError, AttributeError):
        return {"peak_rss_kib": "", "current_rss_kib": "", "memory_measurement": "UNKNOWN"}


def _hardware() -> dict[str, Any]:
    import shapely
    import pvlib
    return {"os": platform.platform(), "python": platform.python_version(),
            "logical_cpu_count": os.cpu_count(), "processor": platform.processor() or "UNKNOWN",
            "threads": 1, "thread_environment": {key: os.environ.get(key, "UNSET") for key in THREAD_ENV_KEYS},
            "memory_note": "Labelled cumulative peak RSS when available; psutil fallback is current RSS, not peak; unavailable values stay blank",
            "timer": "time.perf_counter", "process_model": "single process; no workers",
            "numpy_version": np.__version__, "pandas_version": pd.__version__,
            "shapely_version": shapely.__version__, "geos_version": shapely.geos_version_string,
            "pvlib_version": pvlib.__version__}


def _real_run(method: str, size: int, repeat_id: str | int, warmup: bool,
              manifest: Path, protocol: Mapping[str, Any], output_dir: Path,
              metadata: Mapping[str, Any],
              normalization_bounds: Mapping[str, Sequence[float]]) -> tuple[EvaluationResult, dict]:
    start_utc, started = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    buildings, geoms, sensors, solar, input_hash = load_real_inputs(manifest, protocol)
    if input_hash != metadata["input_hash"]:
        raise ReadinessError("Input package changed after readiness validation; measurements aborted")
    result = evaluate_method(method, buildings, sensors, geoms, solar,
                             protocol["benchmark"]["candidate_order"][:size],
                             protocol["analysis"], protocol["scoring_weights"],
                             normalization_bounds=normalization_bounds)
    result.phase_seconds["load"] += solar.attrs["load_seconds"]
    result.phase_seconds["solar"] += solar.attrs["solar_seconds"]
    result.measurement_class = REAL_MEASUREMENT
    io_started = time.perf_counter()
    artifact = f"aggregate_{method}_m{size}_r{repeat_id}_{'warmup' if warmup else 'run'}.csv"
    _write_csv(output_dir / artifact, result.metrics.to_dict(orient="records"), metadata)
    result.phase_seconds["io"] = time.perf_counter() - io_started
    result.phase_seconds["end_to_end"] = time.perf_counter() - started
    row = {"method": method, "subset_size": size, "repeat_id": repeat_id, "warmup": warmup,
           "status": "MEASURED", "started_utc": start_utc, "ended_utc": datetime.now(timezone.utc).isoformat(),
           "primitive_calls": result.primitive_calls,
           **{phase + "_seconds": result.phase_seconds[phase] for phase in PHASES},
           **_memory_record(),
           "normalization_outside_reference_json": json.dumps(result.metadata["normalization_outside_reference"], sort_keys=True),
           "threads": 1, "solar_mode": solar.attrs["solar_mode"], "output_artifact": artifact,
           "command": "matched_ablation.py --manifest <private-manifest> --output-dir <run-dir>",
           "source_hash": result.metadata["production_source_sha256"]}
    return result, row


def run_benchmark(manifest: Path, protocol: Mapping[str, Any], output_dir: Path,
                  metadata: Mapping[str, Any]) -> dict:
    """Real-only independent runs; checkpoints survive failures and budget stops."""
    bounds, normalization_provenance = load_normalization_reference(protocol)
    _, _, _, _, input_hash = load_real_inputs(manifest, protocol)
    metadata = {**metadata, **normalization_provenance, "input_hash": input_hash,
                "measurement_class": REAL_MEASUREMENT, "code_commit_role": "SOURCE_BASE_COMMIT",
                "harness_source_sha256": sha256_file(__file__)}
    output_dir.mkdir(parents=True, exist_ok=True)
    hardware = _hardware()
    hardware.update({**metadata, "source_hashes": {"harness": sha256_file(__file__),
                     "production_intersection_source": sha256_file(PRODUCTION_SOURCE),
                     "protocol_file": sha256_file(DEFAULT_PROTOCOL)}})
    (output_dir / "ablation_environment.json").write_text(json.dumps(hardware, indent=2), encoding="utf-8")
    records: list[dict] = []
    equalities: list[dict] = []
    completed: dict[int, list[dict]] = {}
    benchmark = protocol["benchmark"]
    sizes = list(benchmark["subset_prefix_sizes"])
    smallest = min(sizes)

    def persist() -> None:
        _write_csv(output_dir / "ablation_runtime_records.csv", records, metadata)
        _write_csv(output_dir / "ablation_equivalence.csv", equalities, metadata)
        summary = []
        for size, rows in completed.items():
            all_equal = all(row["equal"] for row in rows)
            a_times = [row["A_seconds"] for row in rows]
            b_times = [row["B_seconds"] for row in rows]
            a_med, b_med = float(np.median(a_times)), float(np.median(b_times))
            summary.append({"subset_size": size, "planned_repetitions": benchmark["repetitions"],
                            "completed_matched_repetitions": len(rows), "all_equal": all_equal,
                            "A_median_end_to_end_seconds": a_med, "B_median_end_to_end_seconds": b_med,
                            "measured_speedup": speedup_if_equal(a_med, b_med, {"equal": all_equal}, REAL_MEASUREMENT) if all_equal else "",
                            "status": "MEASURED_MATCHED" if all_equal else "FAILED_EQUIVALENCE"})
        _write_csv(output_dir / "ablation_summary.csv", summary, metadata)

    def run_one(method: str, size: int, repeat: str | int, warm: bool = False) -> EvaluationResult:
        try:
            result, row = _real_run(method, size, repeat, warm, manifest, protocol, output_dir, metadata, bounds)
            records.append(row)
            persist()
            return result
        except Exception as exc:
            records.append({"method": method, "subset_size": size, "repeat_id": repeat,
                            "warmup": warm, "status": "FAILED", "reason": type(exc).__name__,
                            **{phase + "_seconds": "" for phase in PHASES}})
            persist()
            raise

    def compare(a: EvaluationResult, b: EvaluationResult, size: int, repeat: Any, stage: str) -> dict:
        equality = compare_results(a, b, protocol["tolerances"])
        equalities.append({"subset_size": size, "repeat_id": repeat, "stage": stage,
                           **equality, "status": "EQUAL" if equality["equal"] else "FAILED_EQUIVALENCE"})
        persist()
        if not equality["equal"]:
            raise ReadinessError("A/B numerical equivalence failed; no speedup can be reported")
        return equality

    # Matched single warm-up on the smallest registered prefix, explicitly excluded.
    warm_a = run_one("A", smallest, "warmup", True)
    warm_b = run_one("B", smallest, "warmup", True)
    compare(warm_a, warm_b, smallest, "warmup", "warmup")
    pilot_a = run_one("A", smallest, "pilot")
    pilot_b = run_one("B", smallest, "pilot")
    compare(pilot_a, pilot_b, smallest, "pilot", "pilot")
    # Runtime alone controls A scope. These estimates NEVER enter measured speedups.
    repetitions = int(benchmark["repetitions"])
    budget = float(benchmark["max_A_full_three_repeats_h"]) * 3600
    predicted = {size: pilot_a.phase_seconds["end_to_end"] * size / smallest * repetitions for size in sizes}
    matched_sizes = [size for size in sizes if predicted[size] <= budget]
    plan = {**metadata, "pilot_selection": "runtime only", "A_predicted_three_repeat_seconds": predicted,
            "estimate_class": "EXTRAPOLATED_RUNTIME_FOR_SCOPE_ONLY", "matched_sizes": matched_sizes,
            "B_full_size": max(sizes), "repetitions": repetitions,
            "B_total_includes_precompute": True,
            "comparison_note": "No ratios across different candidate counts; independent loading/precompute each run"}
    (output_dir / "ablation_pilot_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    if not matched_sizes:
        raise ReadinessError("Even smallest registered A subset exceeds the registered runtime budget")
    # Fixed candidate order throughout. Alternate A/B execution order to reduce
    # time-order bias, without altering candidate order or reusing B precompute.
    for size in sorted(set(matched_sizes + [max(sizes)])):
        for repeat in range(1, repetitions + 1):
            if size not in matched_sizes:
                run_one("B", size, repeat)
                continue
            methods = ("A", "B") if repeat % 2 else ("B", "A")
            results = {method: run_one(method, size, repeat) for method in methods}
            eq = compare(results["A"], results["B"], size, repeat, "measurement")
            completed.setdefault(size, []).append({"equal": eq["equal"],
                                                   "A_seconds": results["A"].phase_seconds["end_to_end"],
                                                   "B_seconds": results["B"].phase_seconds["end_to_end"]})
            persist()
    return {"status": "MEASURED_MATCHED", "matched_sizes": matched_sizes, "repetitions": repetitions,
            "B_full_repetitions": repetitions, "input_hash": input_hash,
            "full_A_status": "MEASURED" if max(sizes) in matched_sizes else "EXTRAPOLATED_ONLY"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=SPRINT_ROOT / "runs/geometry_20261016")
    parser.add_argument("--run-id", default="geometry_20261016")
    parser.add_argument("--code-commit", default=SOURCE_CODE_COMMIT,
                        help="Source checkout base commit; exact modified sources are separately hashed")
    parser.add_argument("--write-blocked", action="store_true", help="Write blank blocked records when real input validation fails")
    parser.add_argument("--check-only", action="store_true", help="Validate real input readiness without benchmark execution")
    args = parser.parse_args(argv)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if sha256_file(args.protocol) != sha256_file(DEFAULT_PROTOCOL):
        parser.error("A supplied protocol must be byte-identical to the frozen ICORES_PROTOCOL.json")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.code_commit):
        parser.error("--code-commit must identify the 40-character source base commit")
    metadata = {"run_id": args.run_id, "config_hash": sha256_file(args.protocol),
                "code_commit": args.code_commit, "code_commit_role": "SOURCE_BASE_COMMIT",
                "harness_source_sha256": sha256_file(__file__),
                "input_hash": "", "measurement_class": REAL_MEASUREMENT}
    benchmark_started = False
    try:
        if args.manifest is None:
            raise ReadinessError("Missing private provenance manifest, canonical footprints, and original ordered 2031-sensor grid")
        inputs = load_real_inputs(args.manifest, protocol)
        if args.check_only:
            print(json.dumps({"status": "REAL_INPUTS_READY", "input_hash": inputs[-1],
                              "solar_mode": inputs[3].attrs["solar_mode"], "benchmark_executed": False}))
            return 0
        benchmark_started = True
        report = run_benchmark(args.manifest, protocol, args.output_dir, metadata)
        print(json.dumps(report))
        return 0
    except ReadinessError as exc:
        if args.write_blocked and not (args.output_dir / "ablation_runtime_records.csv").exists():
            write_blocked(args.output_dir, metadata, protocol, str(exc))
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "real_benchmark_started": benchmark_started}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
