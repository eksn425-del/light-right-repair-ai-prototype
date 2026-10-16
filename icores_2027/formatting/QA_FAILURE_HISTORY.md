# Retained build and QA history

The first build attempts were real failures. Their sanitized terminal output is retained in `evidence/initial-*` rather than overwritten or described as successful.

1. Installed TeX executables could not locate their distribution files because the system lookup databases/formats were absent. A private format and explicit lookup paths resolved this without changing system configuration.
2. The downloaded current template needs NewTX, binhex and TeX Gyre, which were absent locally. Pinned official CTAN packages were installed only under temporary storage. An initial binhex URL returned 404, and a mirror request failed; the registry-documented kastrup package from a listed CTAN mirror succeeded.
3. Missing line10 and typewriter font mappings stopped PDF output. Existing distribution font maps were added to the private PDF font map. No font substitution or margin adjustment was used.
4. The first completed layout was three pages with a sparse last page. Prose was shortened, the source title line-break warning removed, and the table column gaps improved. No font-size or margin compression occurred. Final proof: two pages.
5. Initial anonymity tests produced false positives: an unbounded Windows-path pattern matched the end of an HTTPS URL, and a phrase assertion ignored extractor whitespace. The second attempt found a random drive-like byte sequence inside encrypted Type 1 font data. The corrected scanner tests real PDF strings and decoded non-font streams, scans font dictionaries, and excludes binary font programs from text matching. Failed test logs are retained separately. The PDF was not edited to hide a leak.
6. Final source rebuilt twice through the reproducible script to the same SHA256. Current run uses real pdfLaTeX/BibTeX and returns zero for all commands. Fifteen current tests pass; both final rendered pages were inspected.

Two harmless final compiler warnings remain: LLNCS/NewTX/amsmath cannot redefine the unused `vec` accent, and epstopdf notes that shell escape is disabled. No EPS conversion is needed. There are no overfull/underfull boxes or unresolved citations.
