from __future__ import annotations

import pandas as pd


DEFAULT_SCORE_WEIGHTS = {
    "light_gain": 1.0,
    "intervention_volume": 0.08,
    "new_shadow_penalty": 0.6,
    "protected_zone_penalty": 1.0,
}


def score_interventions(interventions: pd.DataFrame, weights: dict | None = None) -> dict:
    """Score a candidate set using the stable Algorithm B formula."""
    weights = {**DEFAULT_SCORE_WEIGHTS, **(weights or {})}
    estimated_light_gain = float(interventions["expected_light_gain"].sum())
    intervention_volume = float(interventions["volume_change"].abs().sum())
    new_shadow_penalty = float(interventions["volume_change"].clip(lower=0).sum() * 0.08)
    protected_zone_penalty = float(interventions["protected_conflict"].astype(bool).sum() * 40.0)

    total_score = (
        estimated_light_gain * float(weights["light_gain"])
        - intervention_volume * float(weights["intervention_volume"])
        - new_shadow_penalty * float(weights["new_shadow_penalty"])
        - protected_zone_penalty * float(weights["protected_zone_penalty"])
    )
    return {
        "total_score": round(total_score, 3),
        "estimated_light_gain": round(estimated_light_gain, 3),
        "intervention_volume": round(intervention_volume, 3),
        "new_shadow_penalty": round(new_shadow_penalty, 3),
        "protected_zone_penalty": round(protected_zone_penalty, 3),
        "number_of_interventions": int(len(interventions)),
    }

