# English manuscript QA and freeze

Final English source frozen 2026-10-18 UTC. No old manuscript or evidence file edited.

## Outputs
- Anonymous English PDF: `anonymous_regular_submission.pdf`, 21 pages.
- LaTeX: `manuscript.tex`, generated table/prose includes, `references.bib`, `manuscript.bbl`, official class/style and vector chart.
- Expanded translation source: `manuscript_expanded_for_translation.tex` (all nested inputs expanded; references in `.bbl`).
- Portable source archive: `latex_source_bundle.zip`.

## Scientific checks
All new numeric tables derive from saved final CSVs through `generate_tables.py`. Seven tables, two figures, 21 consecutive equations and 13 cited references. Full-space improvement, ordered/local equality, worse top-ten recovery in every space, lack of global heuristic optimality, three unreviewed robust candidates and two corrected robust translations are explicit. No new Honeybee execution, architect survey, learned preferences or constructed intervention is claimed. Historical efficiency and geometry findings remain labelled historical. Original weights are unelicited scenario preferences, not invalid arithmetic.

## Build and presentation
- Official extracted llncs.cls and splncs04.bst used unchanged; default Computer Modern text/math retained.
- Clean source-only rebuild in `qa/rebuild/` is byte-identical to delivered PDF. `qa/clean_rebuild.log` retains the four-pass build.
- Initial plain pdflatex failed because the cloud image lacked a configured format; existing cloud TeX format environment fixed it. Missing default font maps were handled by explicit CM Type1 map. The class keyword centred-dot glyph used an unavailable TS1 bitmap; equivalent CM math dot fixes this without a body-font change. No external installation or user's computer was used.
- 44,968 nonwhitespace characters by Poppler extraction, 45,095 by pypdf. Both include references, tables and extractable vector chart labels and fall within 10,000--50,000. Difference is extraction/ligature handling; no image-only text is omitted.
- 18 fonts, all embedded and subsetted, including vector chart font. See `qa/fonts.txt`.
- Zero overfull boxes, undefined references/citations or missing-character warnings in final log.
- All 21 pages rendered to `qa/page-01.png` through `qa/page-21.png`, reviewed in labelled montages 1--4. Title, text, equations, all tables, both figures, disclosure and references have no observed clipping, overlaps or missing glyphs. Standard template margins and text sizes preserved.
- PDF author metadata empty. No identifying repository, account or workspace path in PDF text. Bibliography author identities are literature citations, not submitting-author identities.

## Remaining human gates
AI use is disclosed substantially and anonymously, with per-section citations. Its placement in a dedicated section is provisional because conference AI wording and anonymous-acknowledgment wording conflict; author/chair confirmation remains needed. The official bundle style is splncs04 while written Springer instructions mention MathPhySci; author should check any portal-specific production instruction. No conflict declaration, author approval, rights declaration or submission attestation is invented. No conference submission, payment, identity entry or public release performed.

## Hashes
See `qa/PAPER_QA.json`. Final PDF SHA256: `d5d1730c6463ec9301dbf524dcf995ce047bfdce00e9c43827ca827b6fe3813a`.
