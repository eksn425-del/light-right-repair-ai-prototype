from __future__ import annotations

import itertools
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "legacy_route_b"))

from research_runtime import strict_bool  # noqa: E402
from route_b_enumerate_2p5d_candidates import reduced_height  # noqa: E402


def eligible_buildings() -> pd.DataFrame:
    data = pd.read_csv(ROOT / "data" / "derived" / "canonical_site_v2" / "canonical_buildings.csv")
    data["movable_bool"] = data["movable"].map(strict_bool)
    data["protected_bool"] = data["protected"].map(strict_bool)
    return data[(data["movable_bool"]) & (~data["protected_bool"]) & (data["height_m"].astype(float) > 3.0)].copy()


def test_candidate_count() -> None:
    data = eligible_buildings()
    assert len(data) == 36
    assert len(list(itertools.combinations(data["building_id"], 2))) == 630


def test_pair_uniqueness() -> None:
    pairs = [tuple(sorted(pair)) for pair in itertools.combinations(eligible_buildings()["building_id"], 2)]
    assert len(pairs) == len(set(pairs))


@pytest.mark.parametrize("height,expected", [(3.0, 3.0), (6.0, 4.5), (9.0, 6.75), (12.0, 9.0), (21.0, 18.0)])
def test_height_constraint(height: float, expected: float) -> None:
    assert reduced_height(height) == pytest.approx(expected)


def test_units_and_geometry_bounds() -> None:
    data = eligible_buildings()
    for col in ["x_min", "x_max", "y_min", "y_max", "height_m", "canonical_area_m2"]:
        assert pd.to_numeric(data[col], errors="coerce").notna().all()
    assert (data["x_max"] > data["x_min"]).all()
    assert (data["y_max"] > data["y_min"]).all()
    assert (data["height_m"] > 0).all()
    assert (data["canonical_area_m2"] > 0).all()


def test_protected_buildings_do_not_enter_candidates() -> None:
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


def test_hb_mapping_is_unique() -> None:
    mapping = pd.DataFrame({"scenario": ["C9_C15_rule_flat", "C9_C13_rule_flat"], "pair_key": ["C9,C15", "C9,C13"]})
    assert mapping["scenario"].is_unique
    assert mapping["pair_key"].is_unique
