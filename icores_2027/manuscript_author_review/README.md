# Complete review contents now available (17 October 2026)

See [WEB_REVIEW_START_HERE.md](WEB_REVIEW_START_HERE.md). All 92 files inside the private author-review archive are now expanded directly here, including every QA render, figure, evidence record and build log. The original single review ZIP container is absent, but none of its member files requires returning to chat. [Inventory](REVIEW_PACKAGE_INVENTORY.json) records every path and hash. Native manuscript PDF and anonymous source ZIP remain available.

This completion update supersedes historical missing-binary statements below and in earlier handoff notes. Scientific/author-approval/submission status is unchanged.

# Submission handoff update (17 October 2026)

Start with [SUBMISSION_HANDOFF.md](SUBMISSION_HANDOFF.md), [full readable English manuscript](FULL_MANUSCRIPT_READABLE.txt), and [15-page PDF](solar_access_decision_support.pdf). These are complete author-review materials; author approvals and final submission remain outstanding. The PDF is now stored natively in this private branch. The [anonymous source ZIP](icores_2027_anonymous_source.zip) is now committed natively. The larger private author-review ZIP remains a Library attachment; its archive upload did not complete. Author-review findings, claim maps, provenance and QA reports are directly readable in this directory. See [independent source verification](INDEPENDENT_SOURCE_CHECK.json).

The following records the earlier text-archive delivery; statements below about intentionally omitting binaries describe that historical snapshot. The update above supersedes those statements for the PDF and anonymous source ZIP.

# ICORES 2027 manuscript: author-review draft

This additive archive contains the final 15-page manuscript source and review evidence prepared on 2026-10-16. Status: COMPLETE_AUTHOR_REVIEW_DRAFT. Author approval: false. Submitted: false. It is a private working archive, not an anonymous supplementary submission.

## Start here
- AUTHOR_REVIEW.md: remaining scientific approval, authorship/rights/single-submission and disclosure-placement decisions.
- manuscript.tex and references.bib: final editable manuscript.
- qa/FINAL_QA.json and qa/INDEPENDENT_REVIEW.md: final quantitative and independent review records.
- REFERENCE_SUPPORT.csv and CLAIM_SOURCE_MAP.csv: citation and frozen evidence mapping.

## Delivered binary artifacts
Binary PDF and ZIP artifacts are delivered as native Library attachments in the owner's conversation. Library IDs are artifact references, not public URLs:
- Final PDF: libfile_6abe2f8ca77c8191b600dfd11f7b74a6
- Anonymous source ZIP: libfile_cf7bc9de367881918db5951bfdc2d8f5
- Private author-review ZIP: libfile_ffef6c3179b08191be037968d993a9a0

Original compiled PDF: 284396 bytes, SHA256 09c362af34cba12b5752b724b8d698a5e20dd6d7847b891a920bdccbde358028.
Library-retained PDF: 304626 bytes, SHA256 eb5a94fbe9e82d24a96babecb34b9af0c05803cfeba7129a8a6e9c6dc0dcbf22.
The retained PDF has identical extracted text and identical rendered pixels on all 15 pages; its author metadata remains blank. Retention changed the bytes, not the reviewed content. See qa/DELIVERY_VERIFICATION.json.
Anonymous source ZIP SHA256: 150ad9a596907f56b2285f157d8c4884c1505f87d35173e05cfda63af54e34f3.
Private author-review ZIP SHA256: a4553a87ed63388c2fb844dd2cf54a8b17699b22e3a8886c647c5b2bd382e2e6.
The source ZIP rebuild was byte-identical to the original compiled PDF in the tested compiler environment. Library retention bytes are not the compiler's reproducibility target.

## Build from this text archive
Use an existing Python environment with Matplotlib and NumPy, then run:
1. python make_figures.py
2. sh build_portable.sh

The first step generates three native-vector PDF figures from the included safe aggregate CSV copies. The second needs a normal TeX Live/MiKTeX installation with the packages listed in SOURCE_README.md. No font files are distributed. The unchanged official class/style preserve their license notices.
The source ZIP includes the PDF figures directly. The repository archive intentionally stores SVG, text and plotting code rather than binary uploads. The archive build sequence is documented; the separately recorded clean source-ZIP build was actually tested. No claim is made that every TeX distribution was tested.

## Evidence and scope
Frozen scientific evidence E: af486946b210b12853b83f9dbdaf708255754d56.
Final evidence handoff M: 91d0d4d7ce9213f1393918122ec42d4e2a4cf568.
Evidence tag: icores-2027-evidence-v1.
No frozen result ledger, original 20-case cohort, handoff, branch other than icores-2027-sprint, or tag is changed by this archive. Earlier readiness flags remain historical snapshots; this directory records manuscript draft completion only.
Three plotting CSV copies have the same values and metadata as the source at M, with line-ending/trailing-newline normalization from the writing workflow. Their exact local hashes are recorded in ARCHIVE_MANIFEST.json and figure provenance. They are not replacement canonical evidence.
No raw geometry, receiver coordinates, WEA, HBJSON, simulation output, fonts or credentials are added.

The writer's DELIVERY_README.md describes the complete delivered packages; its output paths refer to those packages, not binary files in this text-only archive. Original QA records are retained as historical review evidence. Container-specific QA-generation scripts are omitted; their final reports are preserved. This archive makes no new experiment, author approval, submission, publication or acceptance claim.
