# Environment record

Recorded on 2026-09-10 for the clean reproducibility run and updated for the SOICT 2026 evidence patch.

- OS: Windows
- Python: 3.12.2, 64-bit
- NumPy: 2.4.6
- pandas: 2.3.3
- Matplotlib: 3.10.8
- PyYAML: 6.0.3
- trimesh: 4.12.2
- SciPy: 1.17.1
- pytest: 9.0.3
- ladybug-core: 0.44.52
- honeybee-core: 1.64.54
- honeybee-radiance: 1.66.273
- lbt-recipes: 0.28.2
- Radiance: 6.0.2, `RADIANCE 6.0.2 2026-02-02 LBNL`

The Honeybee-Radiance configuration currently resolves the local Radiance installation. If the project is moved to another computer, verify the Radiance executable path before running HB batches. Record any path change in the run metadata rather than editing numerical outputs.

Runtime semantics: the reported 2.5D time is measured for a complete 630-candidate screening repeat; HB time is measured per scene; 23/630 is the selected rule-candidate verification fraction; 33 scenes are operational workflow scenes; 20 scenes are research-only independent validation; and the 630-scene HB number is a serial-equivalent extrapolation, not a completed batch. Operational batch elapsed time is `NOT_MEASURED`.

Runtime records produced by `scripts/run_hb_batch.py` include worker count, host OS, Python version, CPU count, RAM (when available), Radiance version and LBT-Recipes version. Historical records without those columns are labelled as inferred from the invocation documentation in `runtime_summary_v2.json`.
