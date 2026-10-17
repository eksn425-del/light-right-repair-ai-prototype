# ICORES 2027 final candidate for author review

Read `manuscript.pdf` first. This is the actual revised anonymous 15-page candidate, not a skeleton. `FULL_MANUSCRIPT_READABLE.txt` contains searchable English text; use the PDF/TeX for exact equations and figures.

- `CHANGE_LEDGER.md`: bounded revision and untouched scientific elements.
- `REFERENCE_AND_POLICY_RECHECK.md`: primary-source bibliography checks, Ladybug metadata discrepancy, and venue policy.
- `EVIDENCE_INTEGRITY_AUDIT.md` and its JSON: measurement origins, retained-run checks, per-figure/table evidence and limits.
- `qa/FINAL_CANDIDATE_QA.json`: format, anonymity, counts, table/equation invariance and build checks.
- `qa/FIGURE_REGENERATION_CHECK.json`: all three plots regenerated locally and byte-identical to their frozen versions.
- `manuscript.tex`, `references.bib`, `manuscript.bbl`, `figures/`, class/style and build script: editable source.

Measurements were executed in the original author-side Windows environment. This cloud regenerated plots from recorded CSVs, checked retained logs/results and compiled/rendered the paper. It did NOT execute new physical simulations or rerun the frozen 23/20 cohorts. Raw site/solver inputs remain restricted; archive consistency is not independent as-built validation.

The dedicated identity-free AI disclosure plus section citations is a reasoned handling of contradictory public venue instructions, not confirmed organizer approval. Authors must settle disclosure placement and all authorship, rights, originality/single-submission, conflicts and scientific-approval declarations before submission. No submission, organizer email, legal acceptance or payment has occurred.

Official second-stage Regular deadline: 22 October 2026 AoE, equivalent to 23 October 19:59:59 UTC+8. Recheck official dates and enter PRIMORIS through https://icores.scitevents.org/ImportantDates.aspx . Initial range is 10,000–50,000 non-whitespace characters, not a 12-page cap. See preserved `../manuscript_author_review/SUBMISSION_HANDOFF.md` for author form preparation and verified official entry.

The earlier original manuscript and all 92 review files remain untouched in `../manuscript_author_review/`. The candidate is private review material; supporting audit files contain repository identifiers and must not be submitted as an anonymous supplement.

Latest PDF includes the final bounded prose pass after review of version 710120. See FINAL_PASS_DIFF.patch and qa/FINAL_PASS_QA.json. Earlier QA/delivery records document the preceding candidate and are retained as historical checks; this pass introduces no new measurements.

Current delivery is v3, ICORES2027_Anonymous_Final_20261017_v3.pdf, byte-identical to manuscript.pdf. qa/V3_QA.json is the latest PDF check; earlier checks refer to earlier versions.
