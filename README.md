# Light Right Repair AI Prototype

AI-assisted spatial decision workflow for light-equity restoration in dense urban blocks.

## 中文项目简介

**Light Right Repair AI Prototype** 是一个面向城市更新和空间公平议题的 AI 辅助决策工作流原型。它把“哪些街区光照不足、哪些微更新策略最值得优先尝试”转化为可运行的三阶段流程：诊断、候选生成、规则验证和最终推荐。

这个项目不是最终版日照工程软件，也不是自动生成城市设计方案。它更适合表达为：**面向设计团队的空间诊断与方案评估 Workflow 产品**。系统用 toy dataset 和公开安全样例展示算法流程，真实项目数据和原始建模文件不在公开仓库中。

**项目关键词：** Workflow 自动化、空间智能、光照公平、数据评测、决策辅助产品。

This repository is a public-safe demo extracted from a larger private research project. It keeps the reusable algorithmic workflow and toy dataset, while excluding all real site data, raw CAD/Rhino/SketchUp files, field materials, team documents, and private project files.

## SOICT 2026 Research Reproducibility Release

The current research patch, audit results and paper-writing handoff are maintained in [`research_reproducibility/`](research_reproducibility/). Start with its [final patch feedback](research_reproducibility/SOICT_2026_FINAL_PATCH_FEEDBACK.md), [handoff](research_reproducibility/HANDOFF_TO_CHATGPT.md), [writing brief](research_reproducibility/SOICT_2026_PAPER_WRITING_BRIEF.md), [paper-number ledger](research_reproducibility/paper_support/PAPER_NUMBERS.csv) and [claims ledger](research_reproducibility/paper_support/CLAIMS_LEDGER.csv). The public branch contains aggregate evidence and toy data only; private geometry and Radiance intermediates remain excluded.

## Product Positioning

This project is best understood as an **AI-assisted spatial decision prototype**, not a final daylight-engineering tool. It turns a spatial justice question - which parts of a dense block remain under-lit, and what small interventions could improve them - into a repeatable product workflow:

```text
site geometry + planning rules -> diagnosis -> candidate generation -> safety validation -> design-team recommendation
```

The intended user is a designer, planner, or urban-renewal researcher who needs an early-stage decision aid before committing to detailed manual modeling.

## What It Does

The prototype runs a three-stage spatial decision workflow:

1. **Algorithm A - Diagnosis**  
   Simulates winter sunlight exposure on a simplified block model, identifies dark zones, and generates diagnostic heatmaps.

2. **Algorithm B - Candidate Generation**  
   Generates small intervention candidates under a minimal-intervention principle.

3. **Algorithm C - Validation**  
   Checks candidate interventions against accessibility and safety rules, then produces a final recommendation.

## AI Product Loop

| Product layer | Current implementation |
| --- | --- |
| User input | Toy block dataset or standalone grouped OBJ massing model |
| Processing | Simplified 2.5D sunlight diagnosis, candidate generation, rule-based validation |
| Output | Dark-zone heatmap, candidate scores, before/after metrics, final recommendation |
| Validation | Post-simulation ranking, accessibility and safety screening, manual caveat notes |
| Human feedback | Designer reviews recommendation, adjusts geometry/rules, and reruns the workflow |

## Why It Matters

Light quality is a spatial justice issue in dense urban renewal. Instead of treating sunlight analysis as a final rendering check, this workflow treats it as an iterative design decision layer:

- where are the dark zones?
- which public-space gaps can be repaired with minimal intervention?
- which candidate improves light while preserving safety and accessibility?
- how can a designer compare algorithmic suggestions with manual design judgment?

## Public Demo Scope

Included:

- Python pipeline code
- public toy street dataset
- sample configuration files
- generated demo outputs
- heatmap and comparison figures

Excluded:

- real site data
- raw CAD/DXF/SKP/OBJ project files
- field photos and survey materials
- private group/team documents
- course or review materials
- real project output folders

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the public toy demo:

```bash
python main.py --dataset sample_toy_street --output-dir outputs/demo_run
```

Regenerate the toy dataset and run:

```bash
python main.py --dataset sample_toy_street --regenerate-toy --output-dir outputs/demo_run
```

Run with candidate post-simulation verification:

```bash
python main.py --dataset sample_toy_street --regenerate-toy --verify-candidates --output-dir outputs/demo_verified
```

Validate a standalone OBJ massing model:

```bash
python main.py --obj examples/single_mass_block.obj --overwrite-obj-dataset --diagnosis-only --output-dir outputs/single_mass_check
```

Standalone OBJ validation is useful for early testing, but it is not a reliable urban-design conclusion until roads, protected zones, accessibility nodes, and building IDs are manually checked. A single massing block should usually use `--diagnosis-only`; full A/B/C optimization is more meaningful when the OBJ contains several grouped buildings plus site context.

## Repository Map

- `main.py` - command-line entry point for the A/B/C workflow
- `src/algorithm_a_diagnosis/` - sunlight diagnosis and dark-zone detection
- `src/algorithm_b_optimization/` - candidate generation and scoring
- `src/algorithm_c_validation/` - safety and accessibility validation
- `src/geometry/` - toy geometry and intervention mesh helpers
- `src/solar/` - simplified sun-path and sunlight simulation
- `src/visualization/` - heatmap and comparison chart generation
- `data/sample_toy_street/` - public toy dataset
- `config/` - public demo settings
- `outputs/demo_run/` - generated demo outputs
- `assets/figures/` - selected figures for README/portfolio review
- `docs/` - project positioning and privacy notes
- `examples/` - small public-safe geometry examples for validation

## Demo Figures

### Diagnosis Heatmap

![Diagnosis heatmap](assets/figures/heatmap.png)

### Candidate Scores

![Candidate scores](assets/figures/candidate_scores.png)

### Before / After Comparison

![Comparison chart](assets/figures/comparison_chart.png)

## Status

Public-safe research prototype release. It is ready to show as a v0.1 AI product prototype, with transparent limitations and an upgrade path toward a richer design-review interface.

The private project archive remains offline and is not published.

## Product Documents

- [PRD-lite](docs/PRD-lite.md)
- [AI product flow diagram](docs/AI_PRODUCT_FLOW_DIAGRAM.md)
- [AI decision pipeline](docs/AI_DECISION_PIPELINE.md)
- [Evaluation metrics](docs/EVALUATION_METRICS.md)
- [Standalone OBJ validation guide](docs/SINGLE_MASS_VALIDATION_GUIDE.md)
- [中文产品定位说明](docs/PRODUCT_POSITIONING_CN.md)
- [Interview talking points](docs/INTERVIEW_TALKING_POINTS.md)
