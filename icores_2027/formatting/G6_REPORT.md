# G6 result

Completed: current official template downloads and provenance; an actual two-page pdfLaTeX/BibTeX build; all-page rendered inspection; 15 passing build/anonymity tests; editable equations, table, citations, and vector figure with alternative-text sidecar; 13-entry bibliography metadata audit with explicit claim-verification limits.

Main deliverables:
- `TEMPLATE_MANIFEST.json`
- `anonymous/skeleton.tex`, `references.bib`, `skeleton.bbl`, `skeleton.pdf`, `DescriptionTexts.txt`
- `rendered/page-1.png`, `page-2.png`
- `evidence/BUILD_RECORD.json`, `ANONYMITY_RESULTS.json`, `VISUAL_QA.json`, actual sanitized compile and test logs
- `BIBLIOGRAPHY_VERIFICATION.csv`, `BIBLIOGRAPHY_REVIEW.md`
- `OFFICIAL_RECHECK.md`, `ANONYMIZATION_CHECKLIST.md`, `AI_USE_RECORD.md`, `QA_FAILURE_HISTORY.md`

Build: official LLNCS 2.25, 2026-09-03. The original class and `splncs04` style were used unchanged. No font/margin compression. Official ZIPs, Word macros, template binaries and external font files remain outside the repository. Missing free TeX dependencies and format files were handled in private temporary storage, with shell escape disabled.

Proof PDF SHA256: `43fc467adbc207340fc464c54644e71b0994352c693227e3f3d6ac04c5b221da`.

Important author-stage issues: AI disclosure location conflicts with anonymity instructions; original Ladybug author list conflicts with current publisher landing metadata; newer template fonts differ from the August instruction wording; the final interests disclosure and SOICT concurrent-review status need author confirmation. A proposed family-name parsing correction is documented for the AEC review.

The skeleton has 3,309 non-whitespace characters by pypdf extraction and deliberately fails the official manuscript minimum. This is a template verification result, not a finished manuscript, scientific evidence readiness, author approval, or submission. PDF accessibility tagging and any future DOCX metadata/revision audit remain outside this proof’s completed checks.

No commits were made by the G6 worker; only formatting-owned files were written. The parent must record the actual evidence commit after staging. The bibliography CSV records the actual protocol base commit plus `BASE_COMMIT_PLUS_EXACT_SCRIPT_HASH` scope, its exact verification-script hash, and the real protocol/input-bibliography hashes. The new scripts are not claimed to exist at that earlier base commit.
