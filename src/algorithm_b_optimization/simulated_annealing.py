from __future__ import annotations

import math
import random

import pandas as pd

from src.algorithm_b_optimization.scoring import score_interventions


def _subset_key(indices: list[int]) -> tuple[int, ...]:
    return tuple(sorted(int(index) for index in indices))


def search_candidate_sets(
    intervention_pool: pd.DataFrame,
    weights: dict,
    iterations: int = 200,
    candidate_count: int = 3,
    max_interventions_per_candidate: int = 3,
    seed: int = 42,
) -> list[dict]:
    """Run a lightweight simulated-annealing-style search over intervention subsets."""
    rng = random.Random(seed)
    all_indices = list(intervention_pool.index)
    if not all_indices:
        return []

    current = rng.sample(all_indices, k=min(1, len(all_indices)))
    current_score = score_interventions(intervention_pool.loc[current], weights)["total_score"]
    temperature = 5.0
    seen: dict[tuple[int, ...], dict] = {}

    def record(indices: list[int]) -> None:
        key = _subset_key(indices)
        if key in seen:
            return
        metrics = score_interventions(intervention_pool.loc[list(key)], weights)
        seen[key] = {"indices": list(key), "metrics": metrics}

    for index in all_indices[: min(len(all_indices), 12)]:
        record([index])

    for _ in range(max(1, iterations)):
        proposal = set(current)
        operation = rng.choice(["add", "remove", "swap"])
        if operation == "add" and len(proposal) < min(max_interventions_per_candidate, len(all_indices)):
            proposal.add(rng.choice(all_indices))
        elif operation == "remove" and len(proposal) > 1:
            proposal.remove(rng.choice(list(proposal)))
        elif operation == "swap" and all_indices:
            if proposal:
                proposal.remove(rng.choice(list(proposal)))
            proposal.add(rng.choice(all_indices))

        proposal_indices = sorted(proposal)
        proposal_score = score_interventions(intervention_pool.loc[proposal_indices], weights)["total_score"]
        accept = proposal_score >= current_score
        if not accept:
            probability = math.exp((proposal_score - current_score) / max(temperature, 0.001))
            accept = rng.random() < probability
        if accept:
            current = proposal_indices
            current_score = proposal_score
        record(proposal_indices)
        temperature *= 0.985

    ranked = sorted(seen.values(), key=lambda item: item["metrics"]["total_score"], reverse=True)
    return ranked[:candidate_count]

