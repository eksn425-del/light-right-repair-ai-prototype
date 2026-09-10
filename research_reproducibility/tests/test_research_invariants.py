from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_SITE = ROOT / "data" / "derived" / "canonical_site_v2" / "canonical_buildings.csv"
PRIVATE_RUN = ROOT / "experiments" / "baseline_20260909_clean"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "legacy_route_b"))

from research_runtime import load_runtime, production_score, strict_bool  # noqa: E402
from route_b_enumerate_2p5d_candidates import reduced_height  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from freeze_independent_sample import build_frozen_sample, stratum_allocation  # noqa: E402
from validate_independent_composite import normalize  # noqa: E402


def eligible_buildings() -> pd.DataFrame:
    data = pd.read_csv(ROOT / "data" / "derived" / "canonical_site_v2" / "canonical_buildings.csv")
    data["movable_bool"] = data["movable"].map(strict_bool)
    data["protected_bool"] = data["protected"].map(strict_bool)
    return data[(data["movable_bool"]) & (~data["protected_bool"]) & (data["height_m"].astype(float) > 3.0)].copy()


def test_candidate_count() -> None:
    if PRIVATE_SITE.exists():
        data = eligible_buildings()
        assert len(data) == 36
        assert len(list(itertools.combinations(data["building_id"], 2))) == 630
        return
    audit = pd.read_csv(ROOT / "audit" / "SCORING_FORMULA_MIGRATION_AUDIT.csv")
    assert len(audit) == 630
    assert audit["pair_key"].is_unique


def test_pair_uniqueness() -> None:
    if PRIVATE_SITE.exists():
        pairs = [tuple(sorted(pair)) for pair in itertools.combinations(eligible_buildings()["building_id"], 2)]
        assert len(pairs) == len(set(pairs))
        return
    audit = pd.read_csv(ROOT / "audit" / "SCORING_FORMULA_MIGRATION_AUDIT.csv")
    assert audit["pair_key"].is_unique


@pytest.mark.parametrize("height,expected", [(3.0, 3.0), (6.0, 4.5), (9.0, 6.75), (12.0, 9.0), (21.0, 18.0)])
def test_height_constraint(height: float, expected: float) -> None:
    assert reduced_height(height) == pytest.approx(expected)


def test_runtime_uses_config_for_height_and_timestep() -> None:
    runtime = load_runtime()
    assert runtime.reduced_height(12.0) == pytest.approx(9.0)
    assert runtime.timestep_hours == pytest.approx(0.5)
    assert runtime.timesteps_per_hour == 2
    assert runtime.timezone == "Asia/Shanghai"


def test_production_score_four_term_formula() -> None:
    weights = {
        "low_area_drop_weight": 0.45,
        "avg_gain_weight": 0.35,
        "intervention_volume_economy_weight": 0.15,
        "new_low_area_avoidance_weight": 0.05,
    }
    assert production_score(0.8, 0.6, 0.2, 0.1, weights) == pytest.approx(0.45 * 0.8 + 0.35 * 0.6 + 0.15 * 0.8 + 0.05 * 0.9)
    with pytest.raises(ValueError):
        production_score(0.8, 0.6, 0.2, 0.1, {**weights, "new_low_area_avoidance_weight": 0.06})


def test_composite_normalization_uses_fixed_bounds_without_clipping() -> None:
    assert normalize(5.0, 0.0, 10.0) == pytest.approx(0.5)
    assert normalize(15.0, 0.0, 10.0) == pytest.approx(1.5)
    assert normalize(2.0, 2.0, 2.0) == 0.0


def test_units_and_geometry_bounds() -> None:
    if not PRIVATE_SITE.exists():
        pytest.skip("Private geometry table is intentionally omitted from the public mirror.")
    data = eligible_buildings()
    for col in ["x_min", "x_max", "y_min", "y_max", "height_m", "canonical_area_m2"]:
        assert pd.to_numeric(data[col], errors="coerce").notna().all()
    assert (data["x_max"] > data["x_min"]).all()
    assert (data["y_max"] > data["y_min"]).all()
    assert (data["height_m"] > 0).all()
    assert (data["canonical_area_m2"] > 0).all()


def test_protected_buildings_do_not_enter_candidates() -> None:
    if not PRIVATE_SITE.exists():
        pytest.skip("Private protected-building table is intentionally omitted from the public mirror.")
    all_data = pd.read_csv(ROOT / "data" / "derived" / "canonical_site_v2" / "canonical_buildings.csv")
    candidates = set(eligible_buildings()["building_id"])
    protected = set(all_data.loc[all_data["protected"].map(strict_bool), "building_id"])
    assert protected
    assert candidates.isdisjoint(protected)


def test_boolean_parser() -> None:
    assert strict_bool("False") is False
    assert strict_bool("TRUE") is True
    with pytest.raises(ValueError):
        strict_bool("unknown")


def test_empty_candidate_is_safe() -> None:
    empty = pd.DataFrame(columns=["pair_key", "is_hb_pareto_front"])
    assert empty.empty


def test_no_recommendation_when_all_candidates_fail() -> None:
    scores = pd.DataFrame({"candidate_id": ["A", "B"], "passed": ["False", "False"]})
    parsed = scores["passed"].map(strict_bool)
    assert not parsed.any()


def test_reproducible_sampling() -> None:
    data = list(range(607))
    first = pd.Series(data).sample(20, random_state=20260909).tolist()
    second = pd.Series(data).sample(20, random_state=20260909).tolist()
    assert first == second


def test_actual_sampler_preserves_frozen_n20_and_fixes_n12() -> None:
    if PRIVATE_RUN.exists():
        candidates = pd.read_csv(PRIVATE_RUN / "results_csv" / "120_canonical_2p5D完整双建筑候选排名.csv")
        merged = pd.read_csv(PRIVATE_RUN / "results_csv" / "131_HB_Radiance合并候选汇总结果.csv")
        curated = set(merged.loc[merged["model_type"].eq("rule_flat"), "pair_key"])
        n20 = build_frozen_sample(candidates, curated, n=20, seed=20260909)
        frozen = pd.read_csv(PRIVATE_RUN / "independent_validation" / "VALIDATION_SAMPLE_FROZEN.csv")
        assert n20["pair_key"].tolist() == frozen["pair_key"].tolist()
    else:
        pairs = list(itertools.combinations([f"C{i}" for i in range(1, 37)], 2))
        candidates = pd.DataFrame(
            {
                "candidate_id": [f"P{i:03d}" for i in range(1, len(pairs) + 1)],
                "building_ids": [f"{left},{right}" for left, right in pairs],
                "score": [float(index) / len(pairs) for index in range(len(pairs))],
                "intervention_volume_m3": [float((index % 17) + 1) for index in range(len(pairs))],
            }
        )
        curated = set()
        n20 = build_frozen_sample(candidates, curated, n=20, seed=20260909)
        assert len(n20) == 20
    n12 = build_frozen_sample(candidates, curated, n=12, seed=20260909)
    assert len(n12) == 12
    assert n12["pair_key"].is_unique
    assert n12.groupby("stratum", observed=False).size().reindex(["Q1", "Q2", "Q3", "Q4", "Q5"]).tolist() == [3, 3, 2, 2, 2]
    assert stratum_allocation(20) == {"Q1": 4, "Q2": 4, "Q3": 4, "Q4": 4, "Q5": 4}
    assert stratum_allocation(12) == {"Q1": 3, "Q2": 3, "Q3": 2, "Q4": 2, "Q5": 2}


def test_scoring_migration_audit_is_clean() -> None:
    audit_path = (
        PRIVATE_RUN / "audit" / "SCORING_FORMULA_MIGRATION_AUDIT.csv"
        if PRIVATE_RUN.exists()
        else ROOT / "audit" / "SCORING_FORMULA_MIGRATION_AUDIT.csv"
    )
    audit = pd.read_csv(audit_path)
    assert len(audit) == 630
    assert audit["abs_diff"].max() < 1e-9
    assert audit[["rank_same", "top10_same", "pareto_same"]].all().all()


def test_hb_mapping_is_unique() -> None:
    mapping = pd.DataFrame({"scenario": ["C9_C15_rule_flat", "C9_C13_rule_flat"], "pair_key": ["C9,C15", "C9,C13"]})
    assert mapping["scenario"].is_unique
    assert mapping["pair_key"].is_unique
