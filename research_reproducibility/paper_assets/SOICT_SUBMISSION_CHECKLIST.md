# SOICT Submission Checklist

This checklist is a hand-off aid for the frozen SOICT paper package. It is not a substitute for the current official SOICT 2026 call for papers, author kit, template, or submission system. Do not hard-code page limits, anonymity rules, or file-size limits from this file; verify them against the venue instructions immediately before submission.

## Evidence and scope

- [ ] Use only the frozen evidence identified as `soict-2026-write-ready-v1`.
- [ ] Do not alter the frozen experimental numbers while editing prose, tables, or figures.
- [ ] State that this is a site-specific computational screening and decision-support study.
- [ ] Distinguish measured HB scenes, measured 2.5D screening repeats, serial-equivalent extrapolation, operational scenes, and research-only validation scenes.
- [ ] Report the frozen independent sample size and its predeclared status.
- [ ] Do not claim universal accuracy, universal safety, or replacement of architectural judgement.

## Methods and reproducibility

- [ ] Define the 2.5D approximation, sensor/grid definition, time window, timestep, timezone, height rule, and low-sun threshold.
- [ ] State that the production score uses four config-driven terms and identify the normalization universe.
- [ ] Explain the 630-candidate universe, curated HB verification, and independent composite-ranking validation separately.
- [ ] Include the source commit, branch, tag, run ID, and software/environment details required by the venue.
- [ ] Confirm that the 630-candidate clean-ranking regression audit passed after parameter migration.
- [ ] Explain human-in-the-loop review and the boundary between computational ranking and architectural judgement.

## Figures and tables

- [ ] Use Figure 1--9 numbering exactly once and ensure every in-text reference points to the intended asset.
- [ ] Use the captions in `FIGURE_CAPTIONS.md` and `TABLE_CAPTIONS.md` as the starting point.
- [ ] Keep Figure 2 and Figure 5 in the private paper-assets repository unless the research team approves a sanitized crop.
- [ ] Check every table against its CSV source after rounding and typesetting.
- [ ] Preserve figure legends, units, sample scope, and the serial-equivalent label.
- [ ] Add alt text or accessibility metadata if required by the venue.

## References and integrity

- [ ] Use `BIBLIOGRAPHY.bib` as the source bibliography and verify the venue's required citation style.
- [ ] Check every DOI resolves and that author/title/journal/year/volume/issue/pages or article number match.
- [ ] Ensure every bibliography entry is cited in the manuscript or remove unused entries.
- [ ] Do not add AI-generated or unverified references.
- [ ] Disclose software, external data, and any human review protocol required by the venue.

## Data and release hygiene

- [ ] Do not upload CAD, DXF, DWG, SKP, OBJ, sensor-coordinate tables, Radiance intermediate files, or unauthorized real raw data to the public repository.
- [ ] Confirm the public mirror contains only the public-safe figures, derived tables, documentation, code, and ledgers.
- [ ] Confirm the private paper-assets repository access list before sharing it with collaborators.
- [ ] Remove local absolute paths, personal names, and machine-specific paths from the manuscript and supplementary files.

## Final editorial pass

- [ ] Replace internal work-package language with formal limitations language.
- [ ] Check that all claims are supported by a source figure, table, ledger entry, or cited reference.
- [ ] Run a final spelling, grammar, figure/table cross-reference, and PDF rendering check.
- [ ] Compare the final PDF against the official SOICT template and submission portal requirements.
- [ ] Archive the submitted PDF and source package with the submission timestamp and checksum.
