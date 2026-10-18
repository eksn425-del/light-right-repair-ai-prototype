# Anonymous English manuscript source

Run `./build_portable.sh` from a standard TeX Live/MiKTeX installation. The delivered official `llncs.cls` and `splncs04.bst` are included, with Computer Modern text/math defaults. PDF mapping for Computer Modern is explicit for the restricted build image. Keyword centred dots use the equivalent math glyph to avoid an unavailable TS1 bitmap font. No body-font substitution or margin changes are applied.

In the current cloud environment, first run `source /workspace/scratch/8f97152a4ac6/texbuild/env.sh`. This is a cloud-specific format/font search environment, not a dependency on the user's computer. The source bundle is independently recompiled in `qa/rebuild/`; portable production does not require that absolute path on ordinary installations.

`generate_tables.py` reads ../results CSVs, regenerates seven tables and replication prose, and copies the analyst's figures. It is optional for PDF recompilation because generated inputs and figures are delivered. `manuscript_expanded_for_translation.tex` contains nested table/prose inputs expanded for faithful translation; the bibliography is `manuscript.bbl`. Run records and QA are separate from anonymous PDF content.

Only continuous_regret.pdf is included as an experimental chart. Other analyst charts are delivered as supplementary assets. Figure 2 is an editable LaTeX workflow schematic. No generated photographic or site imagery is used.

Author gates: independently review content; confirm AI disclosure scope and placement (conference wording requests acknowledgments, while anonymous guidelines omit acknowledgments); confirm conflicts, rights, originality and submission attestations. No approval or no-conflict statement has been fabricated. This package has not been submitted.

The official downloadable template uses splncs04.bst; the current Springer written instructions additionally mention MathPhySci. The supplied conference-linked template bibliography style is retained; authors should confirm any portal-specific production requirement before final submission.
