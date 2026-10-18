# ICORES 2027 Official Requirements and Template Audit
Verified 2026-10-18 UTC. Read-only audit; no repository changes or submission actions.

## Resolved template verification
The current template was reached through ICORES Templates → Springer author resources → LaTeX2e Proceedings Template ZIP. It is LLNCS v2.25, dated 2026-09-03. Both llncs.cls and splncs04.bst in the paper directory are byte-for-byte identical to that download. The class Git blob is 056b4d4bb2a5c6aa85a258b1b045651607820634. The official bundled samplepaper.pdf itself uses Letter (612 × 792 points), exactly as the inspected manuscript. The sample uses newtxtext and newtxmath with varvw, as does the manuscript. The manuscript has no geometry/margin overrides. Therefore current official class, bibliography style, fonts and page-stock choice are verified; no A4 conversion is needed. Running-head omission is consistent with anonymous initial review and publication instructions leaving running heads to production.

One small source correction: official llncsdoc.pdf page 5 instructs against separately loading amsmath when newtxmath is used. Remove the redundant explicit amsmath package line, rebuild and rerun checks. This does not imply the existing page geometry is wrong.

## Submission-stage checks
Second-stage Regular Paper deadline: 2026-10-22 AoE; author notification December 4; camera-ready/registration December 18. End-of-day deadline converts to October 23 11:59:59 UTC / 19:59:59 UTC+8.
English anonymous PDF with 10,000–50,000 non-whitespace characters including references, tables, graphs and appendices. Current extracted PDF text is within range; extraction is an operational count and cannot count text embedded as paths/images. Full-paper publication allowance is 25 pages, short-paper allowance 20, with paid extensions available. Neither 15 nor 18 pages alone violates the initial submission requirement. At most nine authors. No author details or identifying acknowledgments/links in review copy. Do not publish submitted-paper preprints during review.

## AI transparency
The manuscript has an identity-free AI-Assistance Disclosure and affected-section AI-system citations, including the abstract. The bibliography identifies OpenAI and honestly states that the exact underlying model was not recorded. Do not invent a model/version. The prose describes substantial drafting/code assistance rather than claiming only copyediting.
A genuine placement ambiguity remains: Guidelines prescribe acknowledgments while also excluding acknowledgments for anonymity; AI Tools begins with mandatory acknowledgments disclosure but later permits an appropriate section. The current acknowledgments placement has not been approved by organizers. Keep this as an author clarification item; do not delete disclosure or claim official approval.

## Author-only matters
Confirm final author list/order and contributions, rights to data and reused material, prior publication and nonconcurrent submission, final content, AI-use inventory and competing interests. Do not fabricate a no-competing-interests assertion. Springer production instructions require such a declaration and final source files plus matching PDF; corresponding-author signing authority must cover all authors. These production requirements do not require names in an anonymous review PDF.
INSTICC permits limited cited/marked self-text reuse and previous nonarchival/non-English exceptions, but these do not waive originality, attribution, rights or the venue's substantial-overlap rule. Establish whether the archived Chinese manuscripts were actually published. Repository drafts alone do not establish publication.
Springer encourages public code/data; applicable code-availability statements should explain access restrictions. No ICORES-specific compulsory public repository requirement was located. Keep research private unless separately authorized. Manuscript-source delivery is different from public release of research data/code.

## Primary sources
- https://icores.scitevents.org/ImportantDates.aspx
- https://icores.scitevents.org/Guidelines.aspx
- https://icores.scitevents.org/Templates.aspx
- https://icores.scitevents.org/AiTools.aspx
- https://icores.scitevents.org/FAQ.aspx
- https://portal.insticc.org/plagiarism-policy
- https://www.scitepress.org/EthicsOfPublication.aspx (background; ICORES 2027 identifies Springer as publisher)
- https://link.springer.com/series/558/information-for-authors-and-editors
- https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27851904/data/LaTeX2e%20Proceedings%20Template%20ZIP
- https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27852130/data/Instructions%20for%20Authors%20PDF
- https://www.springernature.com/gp/policies/book-publishing-policies

See TEMPLATE_VERIFICATION.json for exact inspected PDF/class/template hashes. This audit verifies official requirements and template provenance, not author approval or acceptance prospects. The separate scientific reference reviewer checked substantive bibliography entries; this audit inspected their presence and AI citation structure without duplicating that reference-content review.
