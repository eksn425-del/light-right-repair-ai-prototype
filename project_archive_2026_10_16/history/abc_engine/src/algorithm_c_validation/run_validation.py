from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.algorithm_a_diagnosis.run_diagnosis import STREET_COLUMNS
from src.algorithm_c_validation.final_selector import select_final_candidate
from src.algorithm_c_validation.path_filter import build_candidate_routes
from src.algorithm_c_validation.safety_rules import evaluate_safety_violations, load_accessibility_rules
from src.io.export_results import ensure_dir, write_csv, write_json
from src.io.load_tables import normalise_bool_columns, read_table


NODE_COLUMNS = ["node_id", "x", "y", "z", "node_type", "importance", "notes"]


def _safety_score(
    violations: dict,
    accessible_route_ratio: float,
    blocked_path_count: int,
    protected_conflict_count: int,
    data_confidence: float,
) -> float:
    penalty = (
        violations["slope_violation_count"] * 20
        + violations["width_violation_count"] * 25
        + violations["step_violation_count"] * 20
        + violations["guardrail_violation_count"] * 12
        + blocked_path_count * 15
        + protected_conflict_count * 30
    )
    confidence_penalty = (1.0 - data_confidence) * 18
    score = 58 + accessible_route_ratio * 34 - penalty - confidence_penalty
    return round(max(0.0, min(100.0, score)), 3)


def _data_confidence(streets: pd.DataFrame, nodes: pd.DataFrame) -> tuple[float, list[str]]:
    """Estimate how much of the safety check is supported by surveyed inputs."""
    confidence = 1.0
    flags: list[str] = []

    street_notes = " ".join(streets.get("notes", pd.Series(dtype=str)).astype(str).str.lower().tolist())
    node_notes = " ".join(nodes.get("notes", pd.Series(dtype=str)).astype(str).str.lower().tolist())
    street_dirs = " ".join(streets.get("main_direction", pd.Series(dtype=str)).astype(str).str.lower().tolist())

    if "inferred" in street_notes or "inferred" in street_dirs:
        confidence -= 0.08
        flags.append("road_alignment_inferred")
    if "replace with surveyed" in street_notes or "boundary segment" in street_notes:
        confidence -= 0.05
        flags.append("road_centerline_needs_survey")
    if "placeholder" in node_notes:
        confidence -= 0.05
        flags.append("node_locations_partly_placeholder")
    if len(nodes) < 8:
        confidence -= 0.04
        flags.append("sparse_route_nodes")
    if streets.empty:
        confidence -= 0.25
        flags.append("missing_street_data")
    if nodes.empty:
        confidence -= 0.25
        flags.append("missing_node_data")

    return round(max(0.55, min(1.0, confidence)), 3), sorted(set(flags))


def run_validation(dataset_dir: Path, candidates_dir: Path, output_dir: Path, config_dir: Path) -> dict:
    """Run Algorithm C safety/accessibility validation."""
    dataset_dir = Path(dataset_dir)
    candidates_dir = Path(candidates_dir)
    output_dir = ensure_dir(Path(output_dir))
    config_dir = Path(config_dir)

    candidate_scores = read_table(candidates_dir / "candidate_scores.csv")
    interventions = normalise_bool_columns(
        read_table(candidates_dir / "interventions.csv"),
        ["protected_conflict"],
    )
    streets = normalise_bool_columns(
        read_table(dataset_dir / "streets.csv", STREET_COLUMNS),
        ["pedestrian_priority"],
    )
    nodes = read_table(dataset_dir / "nodes.csv", NODE_COLUMNS)
    rules = load_accessibility_rules(config_dir / "accessibility_rules.yaml")
    data_confidence, data_flags = _data_confidence(streets, nodes)

    safety_rows: list[dict] = []
    route_frames: list[pd.DataFrame] = []
    all_flags: dict[str, list[str]] = {}

    for _, score_row in candidate_scores.iterrows():
        candidate_id = str(score_row["candidate_id"])
        candidate_interventions = interventions[interventions["candidate_id"] == candidate_id].copy()
        violations = evaluate_safety_violations(candidate_interventions, rules)
        route_df = build_candidate_routes(
            candidate_id,
            nodes,
            streets,
            candidate_interventions,
            rules,
            float(score_row["estimated_light_gain"]),
        )
        route_frames.append(route_df)
        raw_route_pass_ratio = (
            float(route_df["is_accessible"].mean()) if not route_df.empty else 0.0
        )
        accessible_route_ratio = raw_route_pass_ratio * data_confidence
        blocked_path_count = int((~route_df["is_accessible"].astype(bool)).sum()) if not route_df.empty else 0
        protected_conflict_count = int(candidate_interventions["protected_conflict"].astype(bool).sum())
        score = _safety_score(
            violations,
            accessible_route_ratio,
            blocked_path_count,
            protected_conflict_count,
            data_confidence,
        )
        passed = (
            accessible_route_ratio >= float(rules["min_accessibility_coverage"])
            and violations["slope_violation_count"] == 0
            and violations["width_violation_count"] == 0
            and violations["step_violation_count"] == 0
            and protected_conflict_count == 0
        )
        risk_flags = sorted(set(violations["risk_flags"] + data_flags))
        all_flags[candidate_id] = risk_flags
        safety_rows.append(
            {
                "candidate_id": candidate_id,
                "safety_score": score,
                "accessible_route_ratio": round(accessible_route_ratio, 3),
                "raw_route_pass_ratio": round(raw_route_pass_ratio, 3),
                "data_confidence": data_confidence,
                "blocked_path_count": blocked_path_count,
                "slope_violation_count": violations["slope_violation_count"],
                "width_violation_count": violations["width_violation_count"],
                "step_violation_count": violations["step_violation_count"],
                "guardrail_violation_count": violations["guardrail_violation_count"],
                "passed": bool(passed),
                "notes": "; ".join(risk_flags) if risk_flags else "passes simplified checks",
            }
        )

    safety_report = pd.DataFrame(
        safety_rows,
        columns=[
            "candidate_id",
            "safety_score",
            "accessible_route_ratio",
            "raw_route_pass_ratio",
            "data_confidence",
            "blocked_path_count",
            "slope_violation_count",
            "width_violation_count",
            "step_violation_count",
            "guardrail_violation_count",
            "passed",
            "notes",
        ],
    ).sort_values(["passed", "safety_score"], ascending=[False, False])
    safe_routes = pd.concat(route_frames, ignore_index=True) if route_frames else pd.DataFrame()
    recommendation = select_final_candidate(safety_report, candidate_scores)

    safety_path = write_csv(safety_report, output_dir / "safety_report.csv")
    routes_path = write_csv(safe_routes, output_dir / "safe_routes.csv")
    recommendation_path = write_json(recommendation, output_dir / "final_recommendation.json")

    summary = {
        "candidate_count": int(len(candidate_scores)),
        "passed_candidate_count": int(safety_report["passed"].astype(bool).sum()),
        "selected_candidate_id": recommendation["selected_candidate_id"],
        "rules_used": rules,
        "data_confidence": data_confidence,
        "data_flags": data_flags,
        "risk_flags": all_flags,
        "notes": "Safety score is confidence-adjusted because some road alignments/nodes are inferred or placeholder.",
    }
    summary_path = write_json(summary, output_dir / "C_summary.json")
    return {
        "safety_report": safety_path,
        "safe_routes": routes_path,
        "final_recommendation": recommendation_path,
        "summary": summary_path,
        "summary_data": summary,
    }
