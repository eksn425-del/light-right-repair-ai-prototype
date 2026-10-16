from __future__ import annotations

import pandas as pd


def select_final_candidate(safety_report: pd.DataFrame, candidate_scores: pd.DataFrame) -> dict:
    """Select the final recommendation from candidate scores and safety results."""
    merged = candidate_scores.merge(safety_report, on="candidate_id", how="inner")
    if merged.empty:
        raise ValueError("No matching candidate scores and safety report rows.")

    passed = merged[merged["passed"].astype(bool)].copy()
    if not passed.empty:
        passed["final_rank_score"] = passed["total_score"] + passed["safety_score"] * 0.2
        selected = passed.sort_values("final_rank_score", ascending=False).iloc[0]
        reason = "highest combined light/intervention score among candidates that passed accessibility checks"
    else:
        merged["final_rank_score"] = merged["safety_score"] * 0.5 + merged["total_score"] * 0.2
        selected = merged.sort_values("final_rank_score", ascending=False).iloc[0]
        reason = "no candidate fully passed; selected least-risk option for design-team revision"

    final_notes = str(
        selected.get("notes_y", selected.get("notes", selected.get("notes_x", "")))
    )
    return {
        "selected_candidate_id": str(selected["candidate_id"]),
        "reason": reason,
        "total_score": float(selected["total_score"]),
        "light_gain": float(selected["estimated_light_gain"]),
        "intervention_volume": float(selected["intervention_volume"]),
        "accessible_route_ratio": float(selected["accessible_route_ratio"]),
        "safety_score": float(selected["safety_score"]),
        "final_notes": final_notes,
    }
