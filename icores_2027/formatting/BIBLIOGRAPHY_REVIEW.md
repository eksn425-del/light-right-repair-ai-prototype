# Bibliography verification

All 13 entries in `research_reproducibility/paper_assets/BIBLIOGRAPHY.bib` were checked on 2026-10-16. The frozen source was not edited. Entry-level facts, primary-source URLs, provenance hashes and qualifications are in `BIBLIOGRAPHY_VERIFICATION.csv`. Minimal publisher-deposited metadata is retained in `evidence/BIBLIOGRAPHY_METADATA.json`.

## Results and proposed changes

- Ten entries have agreeing bibliographic metadata. This checks author/title/year/container/volume/issue/pages or article number/DOI where supplied; it does not establish that every passage of a future manuscript is supported.
- Sampson and Charo: Columbia’s own page places the article in Volume 11(2), 1986, but labels its web publication and generated citation as 2020. Retain the issue year with this qualification. The original PDF and issue-detail routes returned access denied and were not bypassed.
- Ladybug 2013: the original proceedings PDF lists two authors, Mostapha Sadeghipour Roudsari and Michelle Pak. The current IBPSA landing record lists Anthony Viola as a third author. These primary sources conflict. Preserve the PDF-based two-author provenance and ask the author to review the conflict. DOI `10.26868/25222708.2013.2499` and pages `3128--3135` can be added from the official landing record. The original PDF, not its URL identifier, establishes the displayed author list.
- The AEC human-centered AI review has a proposed BibTeX name-parsing correction: `Nabizadeh Rafsanjani, Hamed and Nabizadeh, Amir Hossein`. The existing entry displays the same full name but uses only `Rafsanjani` as the family name, which changes abbreviated citations and sorting. The proposed family-name grouping follows the publisher-deposited Crossref record; retain the frozen entry until approved.
- Jakubik et al.: publisher metadata agrees with the bibliography. A secondary abstract reports a 10.5% improvement while the current AAAI publisher abstract reports 12.9%. No effect size was used in the proof. If the manuscript cites one, check the paper itself and the intended version instead of copying a secondary index.

## Unverified list and limits

Manuscript-specific claim support remains UNVERIFIED for all 13 references because the actual current 12-page manuscript is not present in the working source set. No blanket claim-level verification is asserted. Full text was not obtained for Sampson, Sanaieian or Curreli; those entries carry an additional explicit content-verification limit. Other checks used primary publisher abstracts, records, or original documents to establish the narrow context summarized in the CSV, without certifying each entire paper.

The three AI-design/HITL references should be retained only if they support a real sentence in the revised manuscript. Their presence must not imply a new ML model, an LLM component, or experimentally validated AI performance in this sprint.
