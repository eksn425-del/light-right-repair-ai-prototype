# Light Equity / Solar-Access Computational Screening Research

This directory is the reproducible research package for a private lakeside case. It is separate from the earlier public toy/demo repository. The current research question is deliberately narrow: can a low-cost 2.5D candidate screen rank minimum-intervention solar-access changes well enough to select a small, auditable set for higher-fidelity HB-Radiance verification?

## Current result boundary

- The canonical table contains 45 buildings. Under the declared rule (`movable=true`, `protected=false`, `height_m>3 m`), 36 are eligible and produce `C(36, 2) = 630` unordered two-building candidates.
- The analysis uses a 3 m ground grid, 0.1 m sensor height, 30-minute winter-solstice samples from 08:15 to 15:45, and 2.5D height-reduction rules.
- The full candidate universe is screened by the low-cost 2.5D method. HB-Radiance is used for curated candidates and a frozen independent validation sample, not all 630 candidates.
- The output is a decision-support experiment, not a proof of buildability, legal compliance, heritage approval, or superiority over human design.

## Reproduce or inspect the clean run

The source dataset is private and must be supplied separately as `../PRIVATE_SOURCE`; it is intentionally absent from this public mirror. The measured aggregate evidence is included under `results_public/`, while the full run directory and raw geometric/Radiance files remain in the private package. See [REPRODUCE.md](REPRODUCE.md) for the staged sequence and the boundary between inspection and rerun.

```powershell
$env:LIGHT_EQUITY_CONFIG = (Resolve-Path "configs/research.yaml").Path
$env:LIGHT_EQUITY_RUN_ID = "baseline_20260909_clean"
$env:LIGHT_EQUITY_RUN_DIR = "<private-run-directory>\baseline_20260909_clean"
$env:PYTHONPATH = (Resolve-Path "src").Path
python scripts/validate_inputs.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/run_scoring_migration_audit.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/run_weight_sensitivity.py
python scripts/validate_independent_composite.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/generate_figures.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/build_paper_support.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
pytest -q
```

The commands above are a private-run template. In this public mirror, start with `pytest -q` and inspect `results_public/`; the private 630-candidate and HB stages require the omitted source and run directories.

## Evidence package

- `results_public/`: aggregate independent-validation, composite-ranking, runtime and sensitivity evidence with no site geometry.
- `paper_support/`: paper-number ledger, claims ledger, table/figure indices, writing brief and historical diff audit.
- `audit/`: public-safe scoring migration and result-diff audits.
- `HANDOFF_TO_CHATGPT.md`: concise handoff for the web conversation.

## Scientific guardrails

Do not turn `rho`, Top-K recall or a positive candidate score into a universal accuracy claim. Do not describe this pipeline as trained AI/ML: the current method is rule-based computational screening. Geometry correspondence, design translation and final acceptance remain human-in-the-loop.

See [ENVIRONMENT.md](ENVIRONMENT.md) for versions and [PUBLIC_RESEARCH_NOTE.md](PUBLIC_RESEARCH_NOTE.md) for the public/private input boundary.

The production score is the four-term config-driven formula `0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`. The old three-term sensitivity files remain only as superseded audit evidence.
