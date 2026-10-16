# Project Forensic Audit

- Audit time (UTC): 2026-09-09T14:54:02+00:00
- Source package: 'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20'
- Research repository: 'E:\AI项目\light-equity-soict-2026'
- Source file count: 2540

## Scope

The June Route B package is treated as historical evidence. This audit records provenance, dependencies, and reproducibility risks before any scientific rerun.

## Key findings

1. The current Route B scripts contain absolute Windows paths and cannot be cleanly rerun from another checkout.
2. route_b_final_candidate_judgement.py assigns statuses and reasons using fixed candidate IDs; this is not an input-driven production rule.
3. Historical outputs exist for geometry, 2.5D screening, HB/Radiance batches, and design translation, but they are not silently promoted to new results.
4. Raw CAD/SKP/OBJ/WEA and private team files are marked private in the provenance ledger.
5. The next gate is engineering repair plus a clean baseline rerun in a new experiment directory.

## Required evidence files

- FILE_PROVENANCE.csv: hashes, roles, and publication policy.
- SCRIPT_DEPENDENCY_GRAPH.md: static imports and path references.
- HISTORICAL_RESULT_MAP.csv: paper-number traceability and verification status.

## Stop conditions

If required source code, data, or the Honeybee/Radiance environment is unavailable, the corresponding experiment must be marked blocked rather than simulated or filled manually.
