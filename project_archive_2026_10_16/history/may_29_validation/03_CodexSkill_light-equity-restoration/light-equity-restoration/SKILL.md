---
name: light-equity-restoration
description: Run, validate, debug, and package the AI light-right restoration / light equity ABC workflow for architecture datasets. Use when working on light equity restoration, sunlight diagnosis, minimum-intervention spatial optimization, accessibility validation, SketchUp OBJ white models, buildings.csv/street/node/protected-zone schemas, candidate re-simulation, paper-ready metrics, or deliverable folders for the light_equity_project.
---

# Light Equity Restoration

Use this skill for the `light_equity_project` workflow:

1. Algorithm A: sunlight diagnosis on a white-model site.
2. Algorithm B: minimum-intervention candidate generation.
3. Algorithm B verification: optional post-simulation re-ranking of each candidate.
4. Algorithm C: accessibility and safety screening.
5. Final report: paper-ready metrics, charts, heatmaps, and caveat language.

## Default Project Location

Prefer `E:/AI_project/light_equity_project` when the user does not specify another project root.

## Data Contract

A stable dataset folder must contain:

- `site_model.obj`
- `buildings.csv`
- `streets.csv`
- `nodes.csv`
- `protected_zones.csv`

Optional but recommended:

- `site_zones.csv`
- `road_segments.csv`
- `photo_index.csv`

Read `references/data-contract.md` when checking whether a group submission is usable.

## Run Modes

Use the project CLI:

```powershell
python E:/AI_project/light_equity_project/main.py --dataset sample_toy_street --regenerate-toy --output-dir E:/AI_project/light_equity_project/outputs/check_toy
```

For the lakeside leisure district dataset:

```powershell
python E:/AI_project/light_equity_project/main.py --dataset real_guankou/lakeside_leisure_ready --config-dir E:/AI_project/light_equity_project/outputs/lakeside_leisure_final_6m_config --output-dir E:/AI_project/light_equity_project/outputs/check_lakeside_6m
```

For a standalone OBJ:

```powershell
python E:/AI_project/light_equity_project/main.py --obj E:/path/to/site.obj --overwrite-obj-dataset --output-dir E:/AI_project/light_equity_project/outputs/check_obj
```

For paper-facing results, add candidate re-simulation:

```powershell
python E:/AI_project/light_equity_project/main.py --dataset real_guankou/lakeside_leisure_ready --config-dir E:/AI_project/light_equity_project/outputs/lakeside_leisure_final_6m_config --output-dir E:/AI_project/light_equity_project/outputs/check_lakeside_verified --verify-candidates
```

Expect `--verify-candidates` to be slower because each B candidate is re-run through the sunlight model.

## Validation

Use the bundled skill script or project script to run a repeatable validation:

```powershell
python C:/Users/USER/.codex/skills/light-equity-restoration/scripts/run_validation.py --project-root E:/AI_project/light_equity_project --dataset sample_toy_street --output-dir E:/AI_project/light_equity_project/outputs/skill_validation_toy --regenerate-toy
```

The script checks compilation, runs the pipeline, verifies required outputs, and writes `validation_report.json`.

## Interpretation Rules

Never claim:

- 100% safety.
- Complete dark-zone elimination.
- Professional daylight-analysis precision.
- Automatic design finality.

Use:

- "framework estimate"
- "simplified 2.5D sunlight simulation"
- "post-simulation verified candidate ranking"
- "candidate for design-team review"
- "requires manual verification of road width, slope, steps, guardrails, and protected buildings"

## Random OBJ Handling

If only an OBJ is provided:

1. Auto-generate a dataset from OBJ group/object bounding boxes.
2. Treat generated streets/nodes as fallback placeholders.
3. Warn if only one OBJ group is detected.
4. Do not present results as building-level reliable until `buildings.csv`, road centerlines, protected zones, and accessibility nodes are manually verified.

## Deliverable Folder

For final handoff, package:

- `00_notes`: result explanation and caveats.
- `01_inputs`: CSV inputs and readiness summary.
- `02_A_diagnosis`: A summary, sunlight CSV, dark zones, heatmap.
- `03_B_candidates`: candidate scores, interventions, candidate OBJ, verified scores if available.
- `04_C_validation`: safety report, safe routes, final recommendation.
- `05_final_report`: before-after metrics, comparison chart, final heatmap.
