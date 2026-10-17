# Local Figure Captions and Alt Text

## local_matched_ablation

Caption: End-to-end runtime of fresh ray-intersection evaluation (A) and building-blocker reuse (B) at registered nested prefixes of5,20,60 and630 candidates. Values are medians of three single-thread measured repeats per implementation and scale; B includes independent precomputation. Both axes are logarithmic. All pointwise direct-sun-hours, metric, preference-score, rank and Pareto checks agree. This is a comparison of two particular same-primitive Shapely implementations on a frozen approximate canonical model, not all available solver/indexing implementations.

Alt text: A runtime increases from roughly110seconds at5 candidates to11608seconds at630; B stays around23–24seconds including precompute. No geometry or point coordinates are shown.

Source: `runs/local_ablation_20261016/ablation_summary.csv`; script `scripts/local_finalize.py`; run `local_ablation_20261016`. Exact hashes, producing commit and formats: `figures/local_matched_ablation_manifest.json`.

## local_translation_recheck

Caption: Controlled HB recheck of five historical translated pairs and contained corrections on the same ordered receiving points, sun sources and temporal samples. Left: reduction in low-sun grid area relative to baseline; right: net worsened receiving-point count. C9/C24 and C13/C24 retain historical negative results and eliminate the audited C24 outside-wall obstructions in separate corrections. C9/C13 was already contained: its unchanged result is reused for display, not simulated as an additional corrected scene. Target and actual union removal differ and are reported separately, not volume matched.

Alt text: C9/C24 area reduction changes342to351m² and C13/C24 changes207to216m²; their worsened counts change4to0. C9/C15, C9/C13 and C6/C33 displayed reductions remain342,333 and18m². No site geometry or coordinates appear.

Source: `runs/local_hb_20261016/design_translation_recheck.csv`; script `scripts/local_finalize.py`; run `local_hb_20261016`. Exact hashes, producing commit and formats: `figures/local_translation_recheck_manifest.json`. For geometric volumes and result reuse, use `translation_outcome_comparison.csv`.

