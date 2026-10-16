# Anonymization and release checklist

Scope: the formatting-only skeleton, not the unavailable 12-page manuscript or every future figure. Latest machine results: `evidence/ANONYMITY_RESULTS.json`. Latest visual review: `evidence/VISUAL_QA.json`.

## Completed for the proof

- Blank author and affiliation fields; no email, ORCID, real repository URL, acknowledgment identity, or personal path in source-visible text, extracted PDF text, metadata, links, or parsed textual objects
- Author PDF property empty; neutral title/creator; creation and modification dates omitted; no XMP identity
- No attachments, comments, forms, JavaScript, or external links beyond the two cited public providers
- Embedded Type 1 fonts; no vendor fonts or macro-enabled Word documents included in release files
- Both rendered pages inspected; no clipping, overlap, unresolved citations, or compressed margins/fonts
- Editable equations/table and actual vector diagram, with an exported alternative-text description
- AI assistance identified in the provisional statement and figure caption; no experimental values invented
- 15 current build/anonymity tests pass; earlier failures are retained and explained

## Still required for the real manuscript

- Author approval and all author identities verified outside the anonymous review file
- `POLICY_PLACEMENT_CONFIRMATION_REQUIRED` for AI disclosure versus anonymity instructions
- Confirm actual competing interests; do not reuse a template’s no-conflict assertion without author approval
- Confirm no concurrent SOICT review; absence of a receipt is not evidence of withdrawal
- Audit every final illustration’s metadata, labels, source and release permissions; check manuscript self-citations neutrally
- Count 10,000–50,000 non-whitespace characters for the complete initial submission, including figures and appendices
- Check DOCX properties, comments and tracked revisions if a DOCX is later authored; not applicable to this LaTeX proof
- Review the official font-document discrepancy and accessibility requirements at final preparation
- Re-run this QA after every substantive change; inspect all final pages again

Release remains private and author approval is pending. A successful template test is not evidence readiness, manuscript readiness, author approval, or submission.
