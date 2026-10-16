# ICORES formatting proof

This is a two-page anonymous template proof, not the research manuscript and not a submission-ready paper. It deliberately contains no experimental result values and is below the Regular Paper character minimum.

## Reproduce

From the repository root, use a private writable cache outside the repository:

```sh
python3 icores_2027/formatting/build_anonymous.py --cache-dir /tmp/icores-template-cache --download
python3 icores_2027/formatting/test_anonymity.py
```

Prerequisites: Python 3 with pypdf and Pillow; pdfTeX, BibTeX, a TeX Live base tree, and Poppler tools. The build was executed with TeX Live 2025/dev/Debian. The script repairs the missing distribution lookup database by explicit search paths and generates a format in a private temporary directory. It retrieves only pinned public assets when `--download` is supplied. For an already populated verified cache, omit that option. Changed upstream hashes stop the build for review.

The official class and bibliography style are copied unchanged into temporary build storage. NewTX, TeX Gyre, and binhex dependencies remain there; no font files or vendor archives are included in this directory. LaTeX shell escape stays disabled. No system-wide installation or paid service was used.

`anonymous/` holds the editable `.tex` and `.bib`, generated `.bbl`, PDF, and figure-description sidecar. `rendered/` contains the two inspected page images. `evidence/` records actual commands, timings, sanitized logs, build hash, failed attempts, tests, and visual QA. Generated binaries are review artifacts; the parent chooses the permitted assets for its evidence commit.

Optional private name checks can be supplied with `ICORES_ANON_FORBIDDEN` as a pipe-separated environment value. They are checked but not stored in results. Do not put private identities into the command transcript of a release document.

The bibliography audit preserves the frozen source. Any proposed field corrections must be reviewed before updating a manuscript bibliography. Its `code_commit` identifies the actual protocol base commit; `code_commit_scope=BASE_COMMIT_PLUS_EXACT_SCRIPT_HASH` and the exact provenance-check script hash distinguish the new uncommitted audit work. Its input and protocol hashes are real. The parent records the final code snapshot separately.
