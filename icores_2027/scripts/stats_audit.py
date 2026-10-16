"""Audit immutable frozen aggregate tables; never select samples or run a solver.

Run after ICORES_PROTOCOL.json is committed. Source tables retain their original
bytes. All new CSVs carry run/config/code/input provenance and measurement class.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import platform
import sys
from importlib.metadata import version
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import scipy
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path("project_archive_2026_10_16/research/experiments/baseline_20260909_clean")
RUN_ID = "statistics_20261016"
EXPECTED_SAMPLE_SHA256 = "ad4abb9b89a263edaecc2cb3553f7832ce0ccb460521ba218e0083e05bcb46b2"
FROZEN_COMMIT = "6b64fe43451e2e0330930a5677cbe3432307282b"
RETRIEVAL_COMMIT = "ce4087f564a1169b500c0106f869158349c58c6e"
FIELDS = {"A": "low_area_drop_h3_m2", "H": "avg_gain_vs_baseline_h",
          "V": "intervention_volume_m3", "N": "new_low_area_h3_m2"}
WEIGHTS = {"A": .45, "H": .35, "V": .15, "N": .05}
INPUTS = {
    "universe": ARCHIVE / "results_csv/120_canonical_2p5D完整双建筑候选排名.csv",
    "curated": ARCHIVE / "results_csv/132_HB_Radiance已复核候选排名与Pareto.csv",
    "heldout": ARCHIVE / "results/independent_composite_ranking.csv",
    "sample": ARCHIVE / "independent_validation/VALIDATION_SAMPLE_FROZEN.csv",
    "sample_digest": ARCHIVE / "independent_validation/VALIDATION_SAMPLE_FROZEN.sha256",
    "sampling_plan": ARCHIVE / "independent_validation/VALIDATION_SAMPLING_PLAN.md",
    "freeze_metadata": ARCHIVE / "logs/freeze_independent_sample_metadata.json",
    "runtime_records": ARCHIVE / "logs/runtime_records.csv",
    "solar": ARCHIVE / "results_csv/100_统一太阳时刻表.csv",
    "historical_config": Path("research_reproducibility/configs/research.yaml"),
    "score_source": Path("research_reproducibility/src/research_runtime.py"),
    "enumeration_source": Path("research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py"),
    "wea_source": Path("research_reproducibility/src/legacy_route_b/route_b_prepare_hb_batch.py"),
    "sample_source": Path("research_reproducibility/scripts/freeze_independent_sample.py"),
    "area_analysis_source": Path("research_reproducibility/scripts/analyze_independent_validation.py"),
    "composite_analysis_source": Path("research_reproducibility/scripts/validate_independent_composite.py"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_key(value: str) -> str:
    parts = [p.strip() for p in str(value).split(",")]
    if len(parts) != 2 or len(set(parts)) != 2:
        raise ValueError(f"Not a distinct two-building pair: {value!r}")
    return ",".join(sorted(parts, key=lambda p: int(p.removeprefix("C"))))


def normalize(values, lower: float, upper: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if upper < lower or not np.isfinite(values).all():
        raise ValueError("Invalid normalization inputs")
    return np.zeros_like(values) if abs(upper - lower) < 1e-12 else (values-lower)/(upper-lower)


def score(frame: pd.DataFrame, bounds: dict, weights: dict | None = None) -> np.ndarray:
    w = WEIGHTS if weights is None else weights
    norms = {k: normalize(frame[k], **bounds[k]) for k in FIELDS}
    return w["A"]*norms["A"] + w["H"]*norms["H"] + w["V"]*(1-norms["V"]) + w["N"]*(1-norms["N"])


def top_set(frame: pd.DataFrame, metric: str, k: int, policy: str) -> set[str]:
    if not 1 <= k <= len(frame):
        raise ValueError("Top-k is outside comparison set")
    if policy == "pair_key_natural_numeric":
        ordered = frame.assign(_numeric_pair=frame.pair_key.map(lambda p: tuple(int(x[1:]) for x in pair_key(p).split(","))))
        return set(ordered.sort_values([metric, "_numeric_pair"], ascending=[False, True], kind="stable").head(k).pair_key)
    if policy == "pair_key_lexicographic":
        return set(frame.sort_values([metric, "pair_key"], ascending=[False, True], kind="stable").head(k).pair_key)
    if policy == "source_row_order":
        return set(frame.sort_values(metric, ascending=False, kind="stable").head(k).pair_key)
    if policy == "include_boundary_ties":
        threshold = frame[metric].nlargest(k).min()
        return set(frame.loc[frame[metric] >= threshold, "pair_key"])
    raise ValueError(f"Unknown tie policy: {policy}")


def p_display(value: float) -> str:
    return "NUMERICAL_ZERO_NOT_EXACT_ZERO" if value == 0.0 else format(value, ".10g")


def describe_agreement(frame: pd.DataFrame, group: str, metric: str, unit: str) -> dict:
    x, y = frame[f"two_d_{metric}"].to_numpy(float), frame[f"hb_{metric}"].to_numpy(float)
    rho, r = spearmanr(x, y), pearsonr(x, y)
    exact = 2 / math.factorial(len(x)) if (abs(float(rho.statistic)) >= 1-1e-14 and
            len(set(x)) == len(x) and len(set(y)) == len(y)) else None
    return {
        "comparison_set": group, "comparison": f"{metric}_vs_{metric}", "n": len(frame), "unit": unit,
        "spearman_rho": float(rho.statistic), "spearman_pvalue_asymptotic_raw": float(rho.pvalue),
        "spearman_pvalue_display": p_display(float(rho.pvalue)),
        "perfect_rank_permutation_p_if_exchangeable": exact,
        "pvalue_scope": "descriptive; no population inference from nonprobability coverage sample",
        "pearson_r": float(r.statistic), "pearson_pvalue_asymptotic_raw": float(r.pvalue),
        "mae": float(np.abs(x-y).mean()), "median_absolute_error": float(np.median(np.abs(x-y))),
        "max_absolute_error": float(np.max(np.abs(x-y))), "bias_2p5d_minus_hb": float((x-y).mean()),
        "exact_equal_count": int(np.count_nonzero(x == y)),
        "within_1e_minus_12_count": int(np.count_nonzero(np.abs(x-y) <= 1e-12)),
        "unique_values_2p5d": len(set(x)), "unique_values_hb": len(set(y)),
        "spearman_ties": "average ranks; scipy.stats.spearmanr",
    }


def masked_direct_sun_hours(blocked, solar_active, minutes: float) -> np.ndarray:
    blocked, active = np.asarray(blocked, dtype=bool), np.asarray(solar_active, dtype=bool)
    if blocked.ndim != 2 or active.shape != (blocked.shape[1],) or minutes <= 0:
        raise ValueError("Invalid sensor/time shape or timestep")
    return ((~blocked) & active[None, :]).sum(axis=1) * minutes / 60


def legacy_night_result(source: Path) -> float:
    """Execute only the inspected, side-effect-free legacy integration function."""
    module = ast.parse(source.read_text(encoding="utf-8-sig"))
    function = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "hours_from_blocked")
    namespace = {"np": np, "RUNTIME": SimpleNamespace(timestep_minutes=30)}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
    return float(namespace["hours_from_blocked"](np.zeros(1, dtype=bool), 1, 1, 30)[0])


def read_sources(root: Path) -> dict:
    return {name: pd.read_csv(root / INPUTS[name]) for name in ["universe", "curated", "heldout", "sample", "solar", "runtime_records"]}


def validate_sample(root: Path, data: dict) -> dict:
    actual = sha256(root / INPUTS["sample"])
    declared = (root / INPUTS["sample_digest"]).read_text(encoding="ascii").strip()
    if actual != declared or actual != EXPECTED_SAMPLE_SHA256:
        raise AssertionError("Frozen sample bytes changed; never reselect or silently repair")
    sample, heldout, curated = data["sample"], data["heldout"], data["curated"]
    if len(sample) != 20 or sample.pair_key.duplicated().any():
        raise AssertionError("Frozen N=20 is not unique")
    expected = sample.sort_values("sample_order")[["sample_order", "pair_key"]].reset_index(drop=True)
    pd.testing.assert_frame_equal(expected, heldout.sort_values("sample_order")[["sample_order", "pair_key"]].reset_index(drop=True))
    overlap = set(sample.pair_key) & set(curated.pair_key)
    if overlap:
        raise AssertionError("Heldout sample overlaps curated review")
    freeze = json.loads((root / INPUTS["freeze_metadata"]).read_text(encoding="utf-8-sig"))
    records = data["runtime_records"]
    earliest_hb = records.loc[records.scope.eq("independent_validation"), "start_utc"].min()
    earlier = datetime.fromisoformat(freeze["timestamp_utc"]) < datetime.fromisoformat(earliest_hb)
    return {"sha256": actual, "declared_sha256": declared, "bytes": (root / INPUTS["sample"]).stat().st_size,
            "sample_size": 20, "pair_order_unchanged": True, "curated_overlap_count": len(overlap),
            "selection": "pre-frozen coverage sample held out from curated review; not probability sampling",
            "strata_counts": sample.stratum.value_counts().sort_index().to_dict(),
            "reported_freeze_timestamp_utc": freeze["timestamp_utc"], "reported_first_heldout_hb_start_utc": earliest_hb,
            "reported_freeze_precedes_hb": earlier,
            "chronology_caveat": "archived execution logs report ordering; SHA verifies bytes, not chronology; no external timestamp attestation"}


def build_comparisons(data: dict) -> tuple[pd.DataFrame, dict, dict]:
    universe = data["universe"].copy()
    universe["pair_key"] = universe.building_ids.map(pair_key)
    identifiers = set(",".join(universe.pair_key).split(","))
    complete = {pair_key(",".join(p)) for p in itertools.combinations(identifiers, 2)}
    if len(universe) != 630 or len(identifiers) != 36 or universe.pair_key.duplicated().any() or complete != set(universe.pair_key):
        raise AssertionError("Universe is not exactly C(36,2)")
    bounds = {key: {"lower": float(universe[field].min()), "upper": float(universe[field].max())} for key, field in FIELDS.items()}
    u = universe.rename(columns={v: k for k, v in FIELDS.items()})
    scores = score(u, bounds)
    residual = float(np.max(np.abs(scores - universe.score)))
    if residual > 1e-12:
        raise AssertionError("Stored scores do not match frozen 45/35/15/5 formula")
    if not (u.N.min() == u.N.max() == 0):
        raise AssertionError("N=0 expectation differs from frozen table")
    n_checks = []
    for weight in [0.0, .05, .25, 1.0]:
        changed = score(u, bounds, {**WEIGHTS, "N": weight})
        # A constant additive change preserves score differences mathematically.
        residual_constant = float(np.max(np.abs((changed-scores)-(weight-WEIGHTS["N"]))))
        left = pd.DataFrame({"pair_key": universe.pair_key, "score": scores}).sort_values(["score", "pair_key"], ascending=[False, True]).pair_key.tolist()
        right = pd.DataFrame({"pair_key": universe.pair_key, "score": changed}).sort_values(["score", "pair_key"], ascending=[False, True]).pair_key.tolist()
        n_checks.append({"N_weight": weight, "other_weights_fixed": True, "max_constant_shift_residual": residual_constant,
                         "rank_order_unchanged": left == right})
    rows = []
    ui = u.set_index("pair_key")
    for group, frame in [("curated23", data["curated"]), ("heldout20", data["heldout"])]:
        if len(frame) != (23 if group == "curated23" else 20) or frame.pair_key.duplicated().any():
            raise AssertionError(f"Invalid {group} comparison set")
        for index, row in frame.iterrows():
            pair = pair_key(row.pair_key)
            base = ui.loc[pair]
            entry = {"comparison_set": group, "source_row_order": index+1, "pair_key": pair,
                     "candidate_id": base.candidate_id}
            for key in FIELDS:
                entry[f"two_d_{key}"] = float(base[key])
            if group == "curated23":
                for key, field in FIELDS.items():
                    entry[f"hb_{key}"] = float(row[field])
                for field in ["low_area_drop_h3_m2", "avg_gain_vs_baseline_h"]:
                    if not np.isclose(row[f"{field}_2p5d"], base[{v:k for k,v in FIELDS.items()}[field]], atol=1e-12, rtol=0):
                        raise AssertionError("Curated 2.5D fields diverge from universe")
            else:
                entry.update(hb_A=float(row.hb_low_area_drop_h3_m2), hb_H=float(row.hb_avg_gain_h),
                             hb_V=float(row.intervention_volume_m3), hb_N=float(row.hb_new_low_area_h3_m2))
                for key, field in {"A":"two_d_low_area_drop_h3_m2", "H":"two_d_avg_gain_h", "N":"two_d_new_low_area_h3_m2"}.items():
                    if not np.isclose(row[field], base[key], atol=1e-12, rtol=0):
                        raise AssertionError("Heldout 2.5D fields diverge from universe")
            if not np.isclose(entry["two_d_V"], entry["hb_V"], rtol=0, atol=1e-9):
                raise AssertionError("Intervention volume differs between solvers")
            rows.append(entry)
    comparisons = pd.DataFrame(rows)
    for side in ["two_d", "hb"]:
        f = comparisons.rename(columns={f"{side}_{key}": key for key in FIELDS})
        comparisons[f"{side}_score"] = score(f, bounds)
    for metric in ["A", "H", "score"]:
        comparisons[f"error_{metric}_2p5d_minus_hb"] = comparisons[f"two_d_{metric}"] - comparisons[f"hb_{metric}"]
    info = {"size": len(u), "unique_building_ids": len(identifiers), "all_pairs_present": True,
            "N_min": float(u.N.min()), "N_max": float(u.N.max()), "N_normalized_value": 0,
            "N_base_score_constant": .05, "stored_score_max_abs_residual": residual,
            "N_weight_only_checks": n_checks, "normalization_bounds": bounds,
            "normalization_fit": "fixed full 630 2.5D universe; never re-fit to curated or heldout HB outcomes; no clipping",
            "shared_components": "V reused across solvers; N is constant zero in frozen rule candidates"}
    return comparisons, bounds, info


def audit_time(data: dict, root: Path) -> dict:
    solar = data["solar"]
    times = pd.to_datetime(solar.time)
    deltas = times.diff().dropna().dt.total_seconds() / 60
    norm = np.linalg.norm(solar[["vx", "vy", "vz"]], axis=1)
    old_night = legacy_night_result(root / INPUTS["enumeration_source"])
    return {"source": str(INPUTS["solar"]), "samples": len(solar), "first_local": str(times.iloc[0]),
            "last_local": str(times.iloc[-1]), "step_minutes_unique": sorted(set(deltas.tolist())),
            "endpoint_span_h": (times.iloc[-1]-times.iloc[0]).total_seconds()/3600,
            "sum_sample_weights_h": float(solar.weight_h.sum()), "minimum_altitude_deg": float(solar.altitude_deg.min()),
            "maximum_altitude_deg": float(solar.altitude_deg.max()), "nonpositive_altitude_count": int((solar.altitude_deg<=0).sum()),
            "active_count": int(solar.active.sum()), "max_vector_unit_norm_error": float(np.abs(norm-1).max()),
            "night_bug_reproduction_h": old_night, "correct_masked_night_h": float(masked_direct_sun_hours([[False]], [False], 30)[0]),
            "night_finding": "CONFIRMED_LATENT_INTEGRATION_BUG; saved 16-slot vector table has no night slots, so this does not establish frozen-result contamination",
            "time_interpretation": "16 weighted samples at 0.5 h imply 8 h; endpoint span is 7.5 h. 08:00-16:00 midpoint-bin interpretation is plausible but not verified against actual HB inputs",
            "wea_code_semantics": "constant DNI=1000 W/m2 and DHI=0; geometry/DSH carrier, not measured weather or annual weather validation",
            "solar_algorithm_caveat": "current source uses pvlib apparent_elevation, configured 2026 date and UTC+8; WEA DateTime passes month/day/hour/minute without year; actual Ladybug and pvlib vectors unverified",
            "archived_schema_caveat": "saved table has altitude_deg,vx,vy,vz,weight_h,active; current solar_samples source emits apparent_elevation_deg,dx,dy,tan_altitude. Provenance does not establish a byte-identical effective vector sequence",
            "missing_for_equivalence": ["actual frozen recipe inputs", "actual WEA and hours files", "HB effective solar vectors", "per-point/per-time binary solver outputs", "sensor ID and coordinate correspondence"]}


def reconstruct_solar_algorithms(data: dict) -> tuple[pd.DataFrame, dict]:
    """Diagnostic reconstruction only: not a replay of the missing HB recipe."""
    import pvlib
    from ladybug.sunpath import Sunpath
    saved = data["solar"]
    times = pd.DatetimeIndex(pd.to_datetime(saved.time))
    pv = pvlib.solarposition.get_solarposition(times, 24.55, 118.03)
    sunpath = Sunpath(latitude=24.55, longitude=118.03, time_zone=8, north_angle=0)
    lb = [sunpath.calculate_sun(12, 21, t.hour+t.minute/60) for t in times]
    # Ladybug Sun.sun_vector points down from the sun; compare geographic
    # altitude/azimuth here to avoid silently mixing vector sign conventions.
    result = pd.DataFrame({"sample_index": range(1, len(times)+1), "local_time": times.astype(str),
        "saved_altitude_deg": saved.altitude_deg, "pvlib_apparent_altitude_deg": pv.apparent_elevation.to_numpy(),
        "pvlib_azimuth_deg": pv.azimuth.to_numpy(), "ladybug_altitude_deg": [s.altitude for s in lb],
        "ladybug_azimuth_deg": [s.azimuth for s in lb], "ladybug_internal_year": [s.datetime.year for s in lb]})
    result["saved_minus_pvlib_altitude_deg"] = result.saved_altitude_deg-result.pvlib_apparent_altitude_deg
    result["ladybug_minus_pvlib_altitude_deg"] = result.ladybug_altitude_deg-result.pvlib_apparent_altitude_deg
    result["ladybug_minus_pvlib_azimuth_deg"] = result.ladybug_azimuth_deg-result.pvlib_azimuth_deg
    return result, {"measurement_class": "RECOMPUTED_SOLAR_ALGORITHM_DIAGNOSTIC", "pvlib_version": pvlib.__version__,
        "ladybug_core_version": version("ladybug-core"), "latitude": 24.55, "longitude_east": 118.03,
        "utc_offset_hours": 8, "north_deg": 0, "pvlib_year": 2026, "ladybug_internal_year": lb[0].datetime.year,
        "saved_vs_pvlib_altitude_max_abs_deg": float(result.saved_minus_pvlib_altitude_deg.abs().max()),
        "ladybug_vs_pvlib_altitude_max_abs_deg": float(result.ladybug_minus_pvlib_altitude_deg.abs().max()),
        "ladybug_vs_pvlib_azimuth_max_abs_deg": float(result.ladybug_minus_pvlib_azimuth_deg.abs().max()),
        "actual_archived_hb_ray_equivalence": "UNVERIFIED; reconstructed current installed algorithms only",
        "causal_attribution": "not established; differing algorithm/date handling may matter at visibility boundaries but is not proven to cause any observed mismatch"}


def run(root: Path, output: Path, code_commit: str, protocol_commit: str) -> dict:
    started = datetime.now(timezone.utc).isoformat()
    protocol = root / "icores_2027/configs/ICORES_PROTOCOL.json"
    if not protocol.exists() or len(code_commit) != 40 or len(protocol_commit) != 40:
        raise ValueError("Require committed protocol and explicit 40-character source/protocol commits")
    data = read_sources(root)
    sample = validate_sample(root, data)
    comparisons, bounds, universe = build_comparisons(data)
    manifest = [{"name": name, "source_path": str(path), "sha256": sha256(root/path),
                 "size_bytes": (root/path).stat().st_size} for name, path in INPUTS.items()]
    input_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    provenance = {"run_id": RUN_ID, "config_hash": sha256(protocol), "code_commit": code_commit,
                  "input_hash": input_hash, "measurement_class": "RECOMPUTED_FROZEN_AGGREGATES"}
    output.mkdir(parents=True, exist_ok=True)
    def write_csv(name, records, measurement_class=None):
        f = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
        for key, value in provenance.items():
            f[key] = value
        if measurement_class:
            f["measurement_class"] = measurement_class
        f.to_csv(output/name, index=False, float_format="%.17g")
    stats, topk = [], []
    for group, frame in comparisons.groupby("comparison_set", sort=False):
        for metric, unit in [("A", "m2"), ("H", "h"), ("score", "dimensionless")]:
            stats.append(describe_agreement(frame, group, metric, unit))
            for policy in ["pair_key_natural_numeric", "pair_key_lexicographic", "source_row_order", "include_boundary_ties"]:
                for k in [3, 5, 10]:
                    x, y = top_set(frame, f"two_d_{metric}", k, policy), top_set(frame, f"hb_{metric}", k, policy)
                    topk.append({"comparison_set": group, "metric": metric, "k": k, "tie_policy": policy,
                                 "size_2p5d": len(x), "size_hb": len(y), "overlap": len(x&y),
                                 "recall_hb_set": len(x&y)/len(y), "jaccard": len(x&y)/len(x|y),
                                 "members_2p5d": ";".join(sorted(x)), "members_hb": ";".join(sorted(y)),
                                 "scope": f"within {group} only; not global 630 recall"})
    curated = data["curated"]
    old_rho = spearmanr(curated.rank_2p5d_within_verified, curated.rank_hb_low_area_drop)
    time = audit_time(data, root)
    solar_rows, solar_diagnostic = reconstruct_solar_algorithms(data)
    time["algorithm_reconstruction"] = solar_diagnostic
    summary = {**provenance, "status": "COMPLETED_FROZEN_TABLE_RECOMPUTATION_PHYSICAL_REPLAY_BLOCKED",
               "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
               "source_frozen_commit": FROZEN_COMMIT, "retrieval_commit": RETRIEVAL_COMMIT,
               "protocol_commit": protocol_commit, "audit_script_sha256": sha256(Path(__file__)),
               "runtime": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                           "scipy": scipy.__version__, "platform": platform.platform()},
               "frozen_sample": sample, "universe": universe, "statistics": stats, "time_weather": time,
               "legacy_curated_unequal_metric_rank_rho": float(old_rho.statistic),
               "legacy_curated_warning": "legacy score-ranking versus HB-area-ranking is not comparable to heldout area-area or score-score correlation",
               "simulation_executed": False, "sample_reselected": False,
               "limitations": ["aggregate table audit cannot validate geometry, sensor mapping or effective HB time vectors",
                               "shared V and constant N mean perfect composite rank correlation is not independent validation of four metrics",
                               "MAE 0.45 m2 is an average candidate-level error, not 0.45 m2 spatial resolution"]}
    write_csv("same_metric_agreement.csv", stats)
    write_csv("comparison_values.csv", comparisons)
    write_csv("topk_tie_audit.csv", topk)
    write_csv("normalization_bounds.csv", [{"metric": k, **v} for k,v in bounds.items()])
    write_csv("N_weight_only_invariance.csv", universe["N_weight_only_checks"])
    write_csv("input_manifest.csv", manifest)
    write_csv("solar_algorithm_diagnostic.csv", solar_rows, "RECOMPUTED_SOLAR_ALGORITHM_DIAGNOSTIC")
    (output/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False)+"\n")
    if sha256(root/INPUTS["sample"]) != EXPECTED_SAMPLE_SHA256:
        raise AssertionError("Frozen sample changed during audit")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--protocol-commit", required=True)
    args = parser.parse_args()
    output = args.output or args.root / "icores_2027/runs" / RUN_ID
    result = run(args.root, output, args.code_commit, args.protocol_commit)
    print(json.dumps({"status": result["status"], "run_id": RUN_ID, "frozen_sample_sha256": result["frozen_sample"]["sha256"],
                      "statistics": result["statistics"], "time_weather": result["time_weather"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
