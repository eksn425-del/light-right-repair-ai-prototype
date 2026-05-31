# AI Decision Pipeline

## Positioning

This repository demonstrates an AI-assisted decision workflow. The "AI" value is not a chat feature. It is the structured conversion of a spatial problem into inputs, algorithmic processing, validation metrics, and human review.

## Pipeline Overview

```text
Input data
  -> Algorithm A: sunlight diagnosis
  -> Algorithm B: intervention candidate generation
  -> Optional B verification: post-simulation ranking
  -> Algorithm C: accessibility and safety validation
  -> Final recommendation for design-team review
```

## Input Layer

Required dataset files:

- `site_model.obj`
- `buildings.csv`
- `streets.csv`
- `nodes.csv`
- `protected_zones.csv`

Optional but useful:

- `site_zones.csv`
- manually checked road centerlines
- manually checked accessibility nodes
- protected facade or heritage zones

## Algorithm A: Diagnosis

Goal: estimate which public-space cells receive insufficient winter sunlight.

Outputs:

- `sunlight_hours.csv`
- `dark_zones.csv`
- `zone_diagnosis.csv`
- `heatmap.png`
- `A_summary.json`

Product meaning: the system tells the designer where a repair strategy should focus.

## Algorithm B: Candidate Generation

Goal: generate small spatial interventions under a minimal-intervention principle.

Scoring dimensions:

- estimated light gain
- intervention volume
- new shadow penalty
- protected-zone conflict penalty

Outputs:

- `candidate_scores.csv`
- `interventions.csv`
- candidate OBJ files
- `B_summary.json`

Product meaning: the system creates comparable options instead of a single black-box answer.

## Optional Post-simulation Verification

When `--verify-candidates` is enabled, each candidate is re-run through the sunlight model before final ranking.

Product meaning: the system reduces the gap between estimated candidate scoring and simulated outcome.

## Algorithm C: Validation

Goal: filter and explain candidate risk from accessibility and safety perspectives.

Outputs:

- `safety_report.csv`
- `safe_routes.csv`
- `final_recommendation.json`
- `C_summary.json`

Product meaning: the system avoids treating light improvement as the only design objective.

## Final Recommendation

The final report combines diagnosis, candidate scoring, validation, and caveats.

Outputs:

- `before_after_metrics.csv`
- `comparison_chart.png`
- `final_summary.json`
- `algorithm_heatmap.png`

Product meaning: the recommendation is a decision-support artifact for a human designer, not an automatic final design.

## Human-in-the-loop Role

The designer remains responsible for:

- confirming whether input geometry is accurate
- checking road width, slope, steps, and guardrails
- marking protected buildings or zones
- rejecting unrealistic interventions
- selecting a candidate for detailed architectural development
