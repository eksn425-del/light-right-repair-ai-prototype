# Light Equity / Solar-Access Computational Screening Research

This repository is the reproducible research package for the private Xieyan lakeside case. It is separate from the earlier public toy/demo repository. The current research question is deliberately narrow: can a low-cost 2.5D candidate screen rank minimum-intervention solar-access changes well enough to select a small, auditable set for higher-fidelity HB-Radiance verification?

## Current result boundary

- The canonical table contains 45 buildings. Under the declared rule (`movable=true`, `protected=false`, `height_m>3 m`), 36 are eligible and produce `C(36, 2) = 630` unordered two-building candidates.
- The analysis uses a 3 m ground grid, 0.1 m sensor height, 30-minute winter-solstice samples from 08:15 to 15:45, and 2.5D height-reduction rules.
- The full candidate universe is screened by the low-cost 2.5D method. HB-Radiance is used for curated candidates and a frozen independent validation sample, not all 630 candidates.
- The output is a decision-support experiment, not a proof of buildability, legal compliance, heritage approval, or superiority over human design.

## Reproduce the clean run

The source team folder is private and is supplied separately as `../PRIVATE_SOURCE`. See [REPRODUCE.md](REPRODUCE.md) for the staged sequence. The main run is stored under `experiments/baseline_20260909_clean` in the private package.

```powershell
$env:LIGHT_EQUITY_CONFIG = "<research-repository>\configs\research.yaml"
$env:LIGHT_EQUITY_RUN_ID = "baseline_20260909_clean"
$env:LIGHT_EQUITY_RUN_DIR = "<research-repository>\experiments\baseline_20260909_clean"
$env:PYTHONPATH = "<research-repository>\src"
python scripts/validate_inputs.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/generate_figures.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
python scripts/build_paper_support.py --run-dir $env:LIGHT_EQUITY_RUN_DIR
pytest -q
```

## Evidence package

- `experiments/baseline_20260909_clean/results_csv/`: numerical outputs from the clean rerun.
- `experiments/baseline_20260909_clean/results/`: independent validation, runtime and weight sensitivity.
- `experiments/baseline_20260909_clean/figures/`: generated figures at 320 dpi.
- `experiments/baseline_20260909_clean/paper_support/`: paper-number ledger, claims ledger, table/figure indices and historical diff audit.
- `experiments/baseline_20260909_clean/HANDOFF_TO_CHATGPT.md`: concise handoff for the web conversation.

## Scientific guardrails

Do not turn `rho`, Top-K recall or a positive candidate score into a universal accuracy claim. Do not describe this pipeline as trained AI/ML: the current method is rule-based computational screening. Geometry correspondence, design translation and final acceptance remain human-in-the-loop.

See [ENVIRONMENT.md](ENVIRONMENT.md) for versions and [data/PROVENANCE_PRIVATE_DATA.md](data/PROVENANCE_PRIVATE_DATA.md) for the private-input policy.
