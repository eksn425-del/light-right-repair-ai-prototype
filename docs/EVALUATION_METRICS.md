# Evaluation Metrics

## Purpose

These metrics make the prototype explainable in portfolio reviews, interviews, and future product iteration. They are framework estimates, not professional daylight certification.

## Core Metrics

| Metric | Source | Meaning |
| --- | --- | --- |
| Average sunlight hours | `sunlight_hours.csv` and final report | Mean estimated sunlight exposure across sampled cells |
| Dark-zone ratio | `A_summary.json` and `final_summary.json` | Share of sampled cells below the low-light threshold |
| Estimated light gain | `candidate_scores.csv` | Expected improvement from a candidate intervention |
| Intervention volume | `candidate_scores.csv` | Amount of spatial change required |
| New shadow penalty | `candidate_scores.csv` | Penalty for changes that may create new obstruction |
| Protected-zone penalty | `candidate_scores.csv` | Penalty for conflict with protected areas |
| Safety score | `safety_report.csv` | Accessibility and safety screening result |
| Accessible route ratio | `safety_report.csv` | Share of checked routes that remain acceptable |

## How to Read the Result

A strong candidate should:

- reduce dark-zone ratio or improve average sunlight hours
- use low intervention volume
- avoid protected-zone conflict
- preserve accessibility and safe movement
- remain explainable enough for a designer to review

## Current Demo Caveat

The public toy demo may produce limited or zero improvement when the generated candidate does not materially change simulated light exposure. This is acceptable for v0.1 because the purpose is to prove the decision workflow, output structure, and validation logic.

## Interview Explanation

The important product claim is not "the algorithm always improves sunlight." The stronger claim is:

```text
I designed a repeatable decision workflow that diagnoses light-equity issues, generates candidate interventions, checks them against non-light constraints, and exposes metrics for human review.
```

## Next Metrics Upgrade

Future versions should add:

- intervention acceptance rate from human reviewers
- before/after route comfort score
- per-zone improvement ranking
- candidate rejection reason taxonomy
- visual side-by-side massing comparison
