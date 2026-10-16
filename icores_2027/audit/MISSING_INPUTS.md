# Minimal private input request — G0, 2026-10-16

Do not upload these restricted inputs to GitHub. Supply in an author-authorized private runtime or private attachment. No access to the author's E: drive is assumed. Canonical building attributes, 630 aggregate candidate rows, and frozen 20-row sample are already available and are NOT requested again. No full CAD/SKP or whole 630 HB batch is required.

Source index: `project_archive_2026_10_16/indexes/EXCLUDED_SOURCE_FILES.csv`, read at ce4087f; omissions explicitly list the following clean-run inputs. Actual missing-file hashes are unknown until supplied; sizes below are index values, not invented minimum acceptance thresholds.

1. `baseline_20260909_clean/canonical_site_v2/canonical_site_v2.geojson` (indexed 41,062 bytes): all 45 canonical footprints, polygon holes/multipart topology, building_id, units/coordinate-frame provenance. Required for G2 actual containment/volume and G3 matched intersections. Canonical attributes alone cannot reconstruct these footprints.
2. `baseline_20260909_clean/results_csv/100_HB_Radiance传感点.csv` (indexed 47,443 bytes): original ordered 2,031 records, grid_id/x/y/z, UTF-8 CSV. Required for G2 sensor-ID+coordinate mapping and G3. Retain original order/precision. With this table, streets.csv is not necessary to regenerate the grid.
3. Minimal historical replay package: baseline and five original design-stepback cases C9/C24, C9/C15, C9/C13, C13/C24, C6/C33, including generated model/scene and sensor mapping, actual recipe parameters, original 16 timestamps/WEA and ordered sun vectors, per-sensor/per-time visibility `.ill` plus cumulative `.res` and result column mapping. Existing outputs only; mark any unrun/missing case explicitly. Baseline clean-run WEA is indexed 459 bytes; baseline final `.ill` 67,023 bytes and cumulative `.res` 10,155 bytes. Necessary for G2 explaining prior adverse points and G4 actual recipe/time-vector correspondence. For the adverse-ray diagnostic, full baseline and affected C9/C24 visibility is the minimum; other cases' existing model/config and totals can stage the remaining replay. Raw binary formats require their original headers and dimensions.
4. Provenance/permission manifest: SHA256 of supplied files, relation to clean run, units/north/coordinates, sensor order and any transformations. Confirm authorization for private runtime use only. A simple text/JSON manifest is sufficient; no credentials.

Not input requests: Radiance/lbt-recipes are runtime dependencies being inspected/installed by the executor. Author's current 12-page manuscript is not needed for these experiments. The original frozen 20 samples will not be regenerated.

Only real geometry/replay/matched-scene benchmarking and actual historical binary time correspondence are blocked. Code audits, synthetic invariants, frozen aggregate-statistic recomputation, official-template build and honest blocked handoff continue. EVIDENCE_READY_FOR_WEB_REVIEW remains false.

## Updated execution route requested by author

The author chose local Codex continuation for computer-dependent discovery and experiments. Use `LOCAL_CODEX_HANDOFF.md`: locate the above files locally, keep restricted inputs and complete pointwise outputs on that computer, and push only permitted derived evidence to this same private branch. No cloud upload of raw inputs is required. Cloud work will stop branch writes at the final partial checkpoint before local Codex takes over. Missing-to-cloud does not imply these files are absent on the author's computer.
