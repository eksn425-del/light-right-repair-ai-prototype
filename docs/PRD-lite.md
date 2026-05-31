# PRD-lite: Light Right Repair AI Prototype

## Product Goal

Build a public-safe AI-assisted spatial decision prototype that helps designers diagnose low-light public-space zones, generate small intervention candidates, and screen them through safety and accessibility constraints.

## Target Users

- Urban designers testing early renewal strategies.
- Architecture students comparing spatial repair options.
- Planning researchers translating spatial equity questions into measurable workflows.

## Problem Statement

Dense blocks often contain under-lit public spaces, narrow gaps, and constrained pedestrian routes. Traditional sunlight analysis is usually used late in the design process. This prototype moves light diagnosis earlier, so the designer can compare possible interventions before investing in detailed modeling.

## Core User Story

As a designer, I want to input a simplified block massing model and receive a heatmap, candidate interventions, validation warnings, and a recommended option, so that I can decide which spatial repair direction deserves manual refinement.

## MVP Scope

Included in v0.1:

- Toy street dataset.
- Standalone OBJ fallback import.
- Algorithm A sunlight diagnosis.
- Algorithm B candidate generation and scoring.
- Optional candidate post-simulation verification.
- Algorithm C accessibility and safety screening.
- Final report with metrics, figures, and caveat notes.

Out of scope for v0.1:

- Professional daylight certification.
- Automatic final design decisions.
- Real-site public data release.
- Full UI dashboard.
- Cloud deployment.

## Product Flow

1. User prepares a dataset or grouped OBJ massing model.
2. System reads geometry, rules, and accessibility inputs.
3. System identifies under-lit zones with a simplified sunlight model.
4. System generates minimal-intervention candidates.
5. System scores candidates by light gain, intervention amount, shadow penalty, and protected-zone risk.
6. System validates candidates against accessibility and safety rules.
7. System outputs a recommendation for design-team review.
8. Human designer adjusts the geometry, rules, or preferred candidate and reruns the workflow.

## Success Criteria

- A non-private toy dataset can run end to end from command line.
- The output includes at least one heatmap, one candidate score table, one safety report, and one final recommendation.
- The README clearly explains that results are framework estimates, not final engineering conclusions.
- A standalone OBJ can be imported for early massing validation with appropriate caveats.

## Product Risks

- The simplified 2.5D model may under-represent complex facade, terrain, and seasonal effects.
- Auto-generated OBJ datasets may infer unrealistic streets and nodes.
- Candidate generation is rule-based and should not be framed as autonomous optimization.
- Safety and accessibility checks require manual site verification before real use.

## Next Product Upgrade

The next version should add a lightweight review interface where designers can accept, reject, or modify candidates, then rerun the workflow as a human-in-the-loop decision cycle.
