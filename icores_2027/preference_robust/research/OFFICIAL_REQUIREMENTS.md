# ICORES 2027 official submission requirements audit

Verified: 2026-10-18 UTC. Scope: official public conference pages and the Springer author resources linked directly by the conference. No submission, identity entry, agreement acceptance, or payment performed. Both plain URLs and their `?y=2027` versions resolve to ICORES 2027 with consistent requirements.

## 1. Deadline

Source: https://icores.scitevents.org/ImportantDates.aspx

Second-stage category includes Regular Papers and Position Papers. Submission: **22 October 2026, AoE**. Notification: 4 December 2026. Camera-ready and registration: 18 December 2026. First-stage submission has expired.

Short exact evidence (17 quoted words total from this page): “Paper Submission: October 22, 2026”; “All dates refer to AOE time”; “Anywhere on Earth”.

Operational interpretation: AoE is UTC−12; end of 22 October corresponds to 23 October at 11:59:59 UTC. The page gives the date/time zone, not an explicit cutoff second. Do not treat the converted second as a portal guarantee; submit early and recheck immediately before author submission.

## 2. Submission, length and anonymity

Source: https://icores.scitevents.org/Guidelines.aspx

Regular Paper means completed, validated research. Submit an English PDF via PRIMORIS, prepared for double-blind review. Length is **10,000–50,000 non-whitespace characters**, counting references, tables, graphs and appendices. Outside-range submissions risk no review. This is a character limit, not an initial 18-page limit. Accepted Full Papers have 25 proceedings pages; Short Papers have 20, with up to four paid extra pages.

Remove author identities, personal details, identifying references and acknowledgments. Avoid excessive self-citation. No public posting of the submitted paper during review, through final selection announcement. Originality and no substantial overlap with published/simultaneously submitted proceedings work are required. AI-generated sections need a citation to the AI system; AI text disclosure is requested in acknowledgments.

Exact evidence (20 quoted words total): “10,000 to 50,000 characters (excluding white spaces)”; “including references, tables, graphs and appendices”; “WITHOUT any reference to any of the authors”.

Implementation checks (our QA recommendations): inspect PDF metadata, URLs, figure labels and filenames for identity leakage. Count extracted PDF text plus text embedded in figure images; source-code length is not the paper’s character count. The page specifies no counting utility or separate Regular Paper abstract character cap.

## 3. Template chain

Source: https://icores.scitevents.org/Templates.aspx

Templates are strongly advised at review submission and compulsory for the camera-ready paper. The conference links to Springer Computer Science proceedings resources, rather than a separate two-column SCITEPRESS template.

Exact evidence: “strongly advised”; “mandatory for those uploading the camera-ready version”.

Conference link: https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines

Verified redirect: https://link.springer.com/series/558/information-for-authors-and-editors

Official LaTeX2e template ZIP:
https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27851904/data/LaTeX2e%20Proceedings%20Template%20ZIP

The download link was verified; web extraction cannot parse application/zip. This audit does not claim a downloaded archive checksum or inspect its exact class/version. The implementation worker must use the official bundle and record provenance, not imitate its appearance.

## 4. Springer preparation details

Sources: https://link.springer.com/series/558/information-for-authors-and-editors and the official instructions PDF:
https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27852130/data/Instructions%20for%20Authors%20PDF

PDF dated 28 August 2026, ten pages; read during this audit. It applies to LNCS and CCIS, among other Springer proceedings series. For final production supply matching PDF and source, associated assets/style files and bib/bbl. The PDF now specifies MathPhySci bibliography style. LaTeX template fonts are CMR. Tables and equations remain editable. Figure captions go below figures, table captions above tables. Equations use consecutive numbers without section counters. Citations are numeric; include DOIs. Appendices precede references and continue numbering. No need to insert running heads or page numbers. Provide accessible alternative text when requested. Interests declarations need truthful author input; do not invent a no-conflict declaration. Publication-stage author identity requirements do not override conference review anonymity.

Exact evidence: “use the bibliographic style MathPhySci”; “The final source files, incl. bib/bbl files for LaTeX”.

QA additions required by the user: all fonts embedded, page-by-page visual inspection, CSV-to-table/figure consistency, and recompilation from delivered source. Explicit font-embedding wording was not found in these four conference pages; keep it as user-required QA.

## 5. AI disclosure and unresolved placement conflict

Source: https://icores.scitevents.org/AiTools.aspx

Disclose AI-generated text, images, figures and code. Name the tool, identify affected parts, and explain its use. Humans retain responsibility; AI cannot be an author. Fabricating/manipulating scientific data or results is prohibited. Literature claims must be verified against original sources. Language correction, shortening and translation are allowed. Generated illustrations require tool/prompt caption disclosure and clear labeling as illustrations rather than experimental evidence. The page prohibits processing manuscripts under review through public AI platforms for peer-review-like tasks.

Exact evidence (16 quoted words): “must be disclosed in the acknowledgments section”; “preferably in the acknowledgments or appropriate section of the paper”.

**Unresolved official wording conflict:** mandatory acknowledgment disclosure conflicts with the Guidelines’ instruction to omit acknowledgments for double-blind review. The later AI wording permits an appropriate section, but no explicit anonymous-review exception resolves this.

Recommended provisional handling: include an identity-free “AI Use Disclosure” section and cite the tool in affected sections; omit identifying acknowledgments. Record actual analysis/code/writing/translation assistance rather than describing all work as grammar polishing. Flag placement for author/chair confirmation before submission. Do not claim this workaround has official approval. No chair outreach performed.

## 6. Author handoff and remaining gates

- Keep repository and drafts private; remove identifying repository links from the anonymous PDF.
- Author must verify declarations, actual AI scope, conflicts and any submission attestations.
- Recheck dates and any portal-specific fields before manual submission.
- Template archive/version verification and PDF-specific QA remain implementation tasks, not completed by this policy audit.
- No automatic submission, payment, identity filling, or agreement acceptance is authorized by this task.
