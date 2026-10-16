# Author review package — ICORES 2027

Status: substantive anonymous Regular Paper draft prepared for author review. This is not author approval, submission, acceptance, or a public artifact release.

## What is included

- `manuscript.tex`, `references.bib`, `manuscript.bbl`, and the compiled PDF.
- Three publication-size vector figures (PDF and SVG), 300 dpi PNG exports, plotting script, and source hashes. The figures were replotted from unchanged frozen aggregate CSVs to make labels readable at the template's 12.2 cm text width. Original evidence figures are preserved separately.
- `CLAIM_SOURCE_MAP.csv`: manuscript claims, exact frozen-source paths, interpretation limits, and ledger IDs.
- Build logs, font/metadata checks, text and character counts, numerical cross-checks, and page-render QA under `qa/`.

The manuscript is evidence-based. No new physical simulation, reselected sample, learned model, or fabricated measurement was introduced during writing. The frozen evidence commit and tag were not modified.

## Decisions still required from the human authors

1. **Scientific responsibility and final wording.** Read the full manuscript and approve every claim, equation, interpretation and limitation. The DXF component-bounding-box canonical geometry remains approximate, has overlaps/shared components, and disagrees with archived OBJ boundaries. No as-built accuracy or legal modification right is implied.
2. **Authorship, affiliations, rights and single submission.** Confirm author list/order, permissions to use the underlying data and aggregate outcomes, conflicts of interest, and that this paper is not under simultaneous review elsewhere. These facts have not been invented or asserted on your behalf.
3. **AI disclosure location.** The conference Guidelines calls for AI acknowledgements and citations in AI-generated sections but also says to omit acknowledgements for double blindness. The dedicated AI Tools page permits an appropriate disclosure section. This draft uses a neutral, identity-free AI-Assistance Disclosure plus citations in the abstract and each numbered section. It does not silently resolve the conflict: confirm acceptable placement in the official submission instructions/system or with the organizers before submitting. No message to organizers has been sent.
4. **Complete AI record.** The current record honestly covers this manuscript work and prior recorded formatting assistance. Consolidate any additional earlier AI-assisted research, software, translations or drafting. The exact underlying model/version is not in the available execution evidence and is therefore not guessed. AI is not an author.
5. **Template conflict.** The current official LaTeX sample (LLNCS 2.25, 2026-09-03) uses `newtxtext` and `newtxmath[varvw]`; an older author-instruction PDF (2026-08-28) says CMR for LaTeX. Recommendation: retain the current official sample, with no margin/font-size overrides, unless the venue explicitly instructs otherwise. The supplied sample itself uses US Letter pages and a 12.2 × 19.3 cm text area. The build follows that sample. Fonts are not redistributed in the source delivery.
6. **Ladybug reference conflict.** The original BS2013 PDF lists Mostapha Sadeghipour Roudsari and Michelle Pak; the current IBPSA landing metadata adds Anthony Viola. This draft follows the original PDF's two-author list and adds the official DOI/pages. Review this explicit conflict; do not pretend the primary sources agree.
7. **Anonymous artifact boundary.** The manuscript PDF has blank author metadata and no identifying repository URL. The private author-review package includes source mappings and repository identifiers and is NOT an anonymous supplement. Submit only the reviewed anonymous manuscript (and any specifically permitted anonymous supplement). Do not upload restricted geometry, coordinates, WEA/HBJSON or Radiance files.
8. **Submission.** Final submission, declarations, signatures, registration, payment and copyright agreements remain the authors' actions. No submission or fee payment has occurred.

## Official requirements rechecked for this draft

- ICORES 2027 second-stage Regular Paper deadline: 22 October 2026, AoE.
- Target topics: Applications / Decision Support Systems, with Energy and Environment.
- English PDF; double blind.
- Initial Regular Paper: 10,000–50,000 non-whitespace characters, including references, tables, figure/graph content and appendices. The 25-page Full / 20-page Short figures are publication limits, not substitutes for the submission character test.
- Use the current official Springer proceedings template route; do not revert to legacy SCITEPRESS formatting.
- Enter PRIMORIS from the official conference Submit Paper route; do not guess a submission URL.

Sources (checked 2026-10-16):
- https://icores.scitevents.org/ImportantDates.aspx
- https://icores.scitevents.org/Guidelines.aspx
- https://icores.scitevents.org/CallForPapers.aspx
- https://icores.scitevents.org/Templates.aspx
- https://icores.scitevents.org/AiTools.aspx
- https://link.springer.com/series/558/information-for-authors-and-editors

## Scientific framing to preserve

- The 482.927 ratio compares two specific single-thread same-primitive implementations; B includes precompute. It is not superiority over HB, all spatial indexes, or commercial CAD tools.
- The 20 coverage cases are frozen and same site, not random independent-site validation; 0.45 m² is candidate-average error from one 9 m² discrepancy, not sub-grid precision.
- Composite rho=1 does not mean exact scores or independent validation of four criteria: V is shared and N is constant.
- Four new contained corrections plus six historical replays make ten scenes; the unchanged C9/C13 display is reused, not an eleventh scene.
- Net union-volume reduction is |baseline union|−|candidate union|. For noncontained historical solids it is gross removed volume minus added outside volume. It is not a volume-matched intervention comparison or verified construction quantity.
- Canonical-model consistency is not as-built validation. No new experiment is currently necessary to support the deliberately bounded claims in this draft; broader claims would require new evidence.

## Actionable AI-disclosure alternatives

- **Recommended Variant A:** retain the current anonymous `AI-Assistance Disclosure` section and abstract/section-level citations. The dedicated AI policy allows disclosure in acknowledgements or an appropriate section. The statement contains no author or affiliation identities.
- **Variant B, only if the venue explicitly requests it:** rename the same identity-free statement `Acknowledgements: AI Assistance`, retaining all section-level citations. Do not add author, funding or institutional identities to the anonymous version. Do not remove the disclosure to improve anonymity.
- **Exact clarification question for the authors to send if needed:** “For a double-blind Regular Paper, may we place the named AI-tool/use disclosure in an identity-free AI-Assistance Disclosure section, with citations in affected sections, rather than Acknowledgements?”

No alternate no-disclosure PDF is supplied. No organizer contact has been made.

## Page allowance and fee distinction

The current draft is below both the 25-page Full and 20-page Short publication allowances. Its present length would not itself incur an overlength fee under those current allowances. The published €50-per-additional-page charge concerns pages beyond the accepted category's allowance; base author registration is separate. The initial submission remains governed by the 10,000–50,000 non-whitespace-character range, not an invented 12-page cap. Recheck the final accepted category and fees before any registration or payment.
