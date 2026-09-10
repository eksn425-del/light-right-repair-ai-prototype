# Reproduction protocol

## 1. Environment

Use Python 3.12 on Windows. Install the packages in `requirements-lock.txt`. The Radiance 6.0.2 binaries are installed separately and configured through Honeybee-Radiance; see [ENVIRONMENT.md](ENVIRONMENT.md).

## 2. Inputs

The source dataset is external and private: `../PRIVATE_SOURCE/algorithm_ready_lakeside_v2`. Do not copy or upload CAD/SKP/OBJ/DXF binaries without permission. The route configuration is in `configs/research.yaml`.

## 3. Staged execution

Run in this order from the repository root:

```powershell
$env:LIGHT_EQUITY_CONFIG = "<research-repository>\configs\research.yaml"
$env:LIGHT_EQUITY_RUN_ID = "baseline_20260909_clean"
$env:LIGHT_EQUITY_RUN_DIR = "<research-repository>\experiments\baseline_20260909_clean"
$env:PYTHONPATH = "<research-repository>\src"

python scripts/run_all.py --run-id baseline_20260909_clean --skip-hb
python scripts/run_hb_batch.py --manifest experiments/baseline_20260909_clean/hb_radiance_project_batch/run_manifest.csv --log-dir experiments/baseline_20260909_clean/logs/hb_initial --records experiments/baseline_20260909_clean/logs/runtime_records.csv --scope curated_initial --workers 2
python scripts/run_hb_batch.py --manifest experiments/baseline_20260909_clean/hb_radiance_project_batch_extra/run_manifest.csv --log-dir experiments/baseline_20260909_clean/logs/hb_extra --records experiments/baseline_20260909_clean/logs/runtime_records.csv --scope curated_extra --workers 4
python scripts/run_hb_batch.py --manifest experiments/baseline_20260909_clean/hb_radiance_project_final_design/run_manifest.csv --log-dir experiments/baseline_20260909_clean/logs/hb_design --records experiments/baseline_20260909_clean/logs/runtime_records.csv --scope design_translation --workers 4
python src/legacy_route_b/route_b_collect_hb_merged_results.py
python src/legacy_route_b/route_b_compare_2d_hb.py
python src/legacy_route_b/route_b_compare_verified_2p5d_hb.py
python src/legacy_route_b/route_b_final_candidate_judgement.py
```

The independent validation sample is frozen before HB execution:

```powershell
python scripts/freeze_independent_sample.py
python scripts/prepare_independent_validation.py
python scripts/run_hb_batch.py --manifest experiments/baseline_20260909_clean/independent_validation/hb_batch/run_manifest.csv --log-dir experiments/baseline_20260909_clean/logs/hb_independent --records experiments/baseline_20260909_clean/logs/runtime_records.csv --scope independent_validation --workers 4
python scripts/analyze_independent_validation.py
```

Then run the audit and paper-support steps:

```powershell
python scripts/run_runtime_benchmark.py --run-dir experiments/baseline_20260909_clean --repeats 3
python scripts/run_weight_sensitivity.py
python scripts/validate_inputs.py --run-dir experiments/baseline_20260909_clean
python scripts/generate_figures.py --run-dir experiments/baseline_20260909_clean
python scripts/build_paper_support.py --run-dir experiments/baseline_20260909_clean
pytest -q
```

`run_all.py --skip-hb` is intended for geometry and candidate generation only. A full clean rerun with HB can take substantially longer and writes large private intermediate files.
