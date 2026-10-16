# Paper Asset Manifest

## Release identity

- Package: `soict-paper-assets-v1`
- Source branch: `research-repro-v1`
- Frozen source commit: `6b64fe43451e2e0330930a5677cbe3432307282b`
- Frozen source tag: `soict-2026-write-ready-v1`
- Frozen run ID: `baseline_20260909_clean`
- Generated: `2026-09-10`

This package is a publication hand-off derived from frozen evidence. The build step does not rerun or modify experiments. Every figure and table has its source CSV/JSON or script and run ID recorded in `FIGURE_CAPTIONS.md` or `TABLE_CAPTIONS.md`.

## Visibility controls

- `PRIVATE ONLY` assets: Figure 2, Figure 5, Table 1, Table 3, and Table 4. Their site-specific geometry or identifiers may allow reconstruction of the study area.
- `PUBLIC` assets: Figures 1, 3, 4, 6, 7, 8, 9 and Tables 2, 5, 6, 7, 8, 9, together with documentation and bibliography.
- The complete package belongs in the private paper-assets repository. The public mirror contains only the explicitly marked public subset.

## Prohibited source material

No original CAD/DXF/DWG/SKP/OBJ, sensor coordinate table, Radiance intermediate (`.ill`, `.res`, `.hbjson`, `.wea`), or unauthorized real raw data is included in this package. Source paths in the manifest are paper provenance labels only; local absolute paths are intentionally omitted.

## Figure/table provenance

See `FIGURE_CAPTIONS.md` and `TABLE_CAPTIONS.md`. Numerical values must be copied from the listed source CSV/JSON files and not from narrative summaries.

## Bibliography verification sources

The bibliography entries include DOI URLs. The primary metadata checks used for this package include the DOI/publisher records for entries [1]--[8], [10]--[13], the official Ladybug Tools publication record and IBPSA proceedings PDF for [9], and the official AAAI proceedings page for [12]. The DOI landing record for [1] is a digitized journal item; the volume/issue citation year is retained as 1986.

## Checksums

| Asset | Bytes | SHA256 |
|---|---:|---|
| `ASSET_BUILD_METADATA.json` | `1370` | `0a4e5e4e88bb5206e89496f251403f6e13fa325c877dc043609be1e2a01dfbe0` |
| `BIBLIOGRAPHY.bib` | `6126` | `e4e033e7aec75b96b2dcb6286861325a3e6ea3830c5729f5e06c5158e4ab6bd6` |
| `FIGURE_CAPTIONS.md` | `5512` | `e1458d5552714839d7c877d5c4946ee1340f77ab44d66b65bff26108eb66c381` |
| `figures/png/F01_workflow.png` | `125081` | `39923803772773c6b62a967a77e73c204dcb68697a7e3a0349a06f872f44cc0b` |
| `figures/png/F02_baseline_field.png` | `266516` | `262428962db7c11cec13b4f25f038619d13c831a86121c092d029ecfda37d7c2` |
| `figures/png/F03_curated_rank_agreement.png` | `132030` | `0fd15a94a0ca7071e5c4b5c585c133ecaca26b2c4a372c26f55ec9ab30f45bb9` |
| `figures/png/F04_design_translation_comparison.png` | `146331` | `bf69cd412bc210e58676ea735b259faf1a38d1fc2a1b90e6146703c73feea7d4` |
| `figures/png/F05_candidate_change_map.png` | `161797` | `e37d95489337a0cf5be94812d72b448d5af89b17be206b1b8c00497558c2d467` |
| `figures/png/F06_independent_validation_scatter.png` | `116049` | `200c0727f4cc65d651afaf8c31f124c43ed217e8ea9aef9b8c83a4f04c5d7737` |
| `figures/png/F07_runtime_comparison_v2.png` | `96817` | `4428af722cd04a454c9f7856ca6d3880b04ae820db0c657585a9a59c673350e9` |
| `figures/png/F08_weight_robustness_v2.png` | `127855` | `85d4f8d467c905dacdcccdff3f5b68bb2b90c73ca747c813cd8f5fc462abec0e` |
| `figures/png/F09_independent_composite_ranking.png` | `137547` | `82b9d4a0c2ae00a781ffb015d8d5e1e6ba3d9df3d6bec6deaa9abf4648dbeff2` |
| `figures/vector/F01_workflow.pdf` | `121801` | `aec7dabc4d4998428b4ac6ac14ec3692d70ed4884b21021dbeb4710abc90fed0` |
| `figures/vector/F01_workflow.svg` | `171688` | `4bdd6ec3f3c33e0a88ec8a92d5eae891d2ab9cb8713573d916c53dd7e20ec730` |
| `figures/vector/F02_baseline_field.pdf` | `262334` | `6c1bff89a2406e5f35253a4ac35335d2968716e9cca6862169ec6597be931d77` |
| `figures/vector/F02_baseline_field.svg` | `378075` | `b90bb194f364a3944e0427520c6678318b9d544be674ad85809061f75a2a31d7` |
| `figures/vector/F03_curated_rank_agreement.pdf` | `146883` | `700649ee48403651991bf35f89958d4b13a71eab6cf3ffc91c6ed57c8c0f54f8` |
| `figures/vector/F03_curated_rank_agreement.svg` | `208821` | `07f66a88b3516b067130ae11c296d049244e1499886eff767f49eb5c8b266203` |
| `figures/vector/F04_design_translation_comparison.pdf` | `141011` | `9eaa8b9f170b4de70ad493efe689efb77c24fddb3d43d706a7d68795f7966536` |
| `figures/vector/F04_design_translation_comparison.svg` | `195680` | `15d194b8e2adc49da8f602621e481c9259445a6a74ea3d1a17502fdb833032b3` |
| `figures/vector/F05_candidate_change_map.pdf` | `165986` | `61dad4be3a9cc7ebf674ef44a28bafadbfbc78471bc0432b7188a96ba1dfc34e` |
| `figures/vector/F05_candidate_change_map.svg` | `225089` | `04ee7c07cb3ab4e8deb6f954c4dd382aef988176d82ae2de57c3b812955be4f0` |
| `figures/vector/F06_independent_validation_scatter.pdf` | `128899` | `686308a4fbee14829c80248948eebb2e0a16208a33b4f206b792c3cc25a4e71c` |
| `figures/vector/F06_independent_validation_scatter.svg` | `182233` | `34235561d8205470b82f85a2cbc980f52a1d2ce15f5942741c732df3ba096304` |
| `figures/vector/F07_runtime_comparison_v2.pdf` | `96794` | `ba927b32982bf43899072b43b56af3b01a1f8ba51753d6ce728f080f7d5b8343` |
| `figures/vector/F07_runtime_comparison_v2.svg` | `130424` | `938ccb9d7fe68d2c6facbf2d30b3e344ba98d14eff0c635d08ba30d1e14628de` |
| `figures/vector/F08_weight_robustness_v2.pdf` | `124340` | `526939c3841cda12d3f23e41a6f582cb57fd50d699c7d6629a5ebe52b683bd49` |
| `figures/vector/F08_weight_robustness_v2.svg` | `173376` | `7c72316ca2f62681bf64f082fdf333316e5128895a0b070eeabbd7d0e8651596` |
| `figures/vector/F09_independent_composite_ranking.pdf` | `130927` | `837b660684a6a941d8d993e7b14a422d1ea3b755b3a1d57569a691ceb7a8fffe` |
| `figures/vector/F09_independent_composite_ranking.svg` | `188692` | `1c0e36851ebf11009d288e8cdea46a762ea450689c5e833cce65c6faa376d531` |
| `README.md` | `978` | `bbab0530c7627e2ece2829473449b2121a7b2e86866fb1e018454613ac64d007` |
| `SOICT_SUBMISSION_CHECKLIST.md` | `3872` | `07cc942c6da73f5bb7a992bb9a64e3d60d855a15cec2e06296a87c70f56d9c64` |
| `TABLE_CAPTIONS.md` | `4608` | `a4c8117d5163c06c43672ed8a628701a9b7192fa9195616463752938b7aa91be` |
| `tables/table_01_geometry_audit.csv` | `15079` | `1324504f7ffaab6408339cc52815360a066e6c3b03989474927fa6fed3e5f74c` |
| `tables/table_02_analysis_protocol.csv` | `1247` | `6b58a23e555ca321c82bc7c0a2f5d3be314be11fd97ed8b7bf031711c7a9ef4c` |
| `tables/table_03_candidate_universe.csv` | `171864` | `3779555e4b63cb6b47a81b24bb7aa60eb09f622f85b81f71dfc0914beb2bb3a6` |
| `tables/table_04_curated_hb_verification.csv` | `7256` | `1a82e82647746f46ab8b8587daaf091c18a999217b9a7b7425633cf9975ef72e` |
| `tables/table_05_independent_metric_validation.csv` | `600` | `22bb6c107e7bbd48156ee03a70c4922283199f4e37f696e5ee951dbc6875227c` |
| `tables/table_06_design_translation.csv` | `4388` | `b677c2f9e59df642e962819a164b0a8b872c56a35630191e5cfc73be00265214` |
| `tables/table_07_runtime_semantics.csv` | `1513` | `fb7b75ee7ed95ed7f3123941d17290ccb01857617c4dbae770ab112bc24d241c` |
| `tables/table_08_independent_composite_metrics.csv` | `979` | `61ac94f6e5cbfa9e0154041f16c1330da337085b3a61b8cc0e67e217ace8aaed` |
| `tables/table_08_independent_composite_ranking.csv` | `5489` | `2bad0f8bb11f0471cb47543a52e2d7ca909f439292a1d860a49d39f8ba310823` |
| `tables/table_09_candidate_rank_stability.csv` | `33726` | `832fdf8ac540b96d43e7b806bae962173b207245a86c4d1f61d8bc7c3cf89c3e` |
| `tables/table_09_weight_sensitivity_summary.csv` | `874` | `ac4b985b33f07ac64a7c52444cd123a47c43aba30d596f76aa1368f755ffd1cb` |
