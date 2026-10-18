# Final independent scientific and rendered-PDF review

Reviewed 2026-10-18. Read-only against manuscript/project; review outputs only in this directory.

## Verdict

No actionable scientific or visual blocker found in the reviewed manuscript. This is an author-review draft, not approval to submit. Official formatting and AI-disclosure placement remain the lead policy reviewer's and authors' pending decisions. No unsupported page limit is imposed.

Reviewed PDF SHA-256: 27f20bc85c92403d24c5567bc55fd3a126603f044c0a2b259af19e0584f5df0f. Snapshot: review_snapshot.pdf. The revised two-panel Figure 3 makes this version **18 pages**, superseding the earlier 17-page description. Source manuscript hash supplied by lead: 130da0b621e371a7e63b2bbdab9e7e2364c76db6876071e92b3d055a90c08a9d.

## Scientific checks

- All Top10 identities, ordering, rounded A/H/V/S values and three Pareto memberships agree with independent_top10.csv. All ten have historical rule HB review; only three have translation evidence. Two contained corrections and one reused result remain distinguished.
- 36 observed eligible identifiers, 630 unordered pairs, 12 Pareto candidates, three Top10/front overlaps, and 23 curated candidates reconcile with the independent audit and source selection implementation.
- Equations 1–11 preserve the declared height rule, discrete duration mask, net threshold-area benefit, mean gain, additive volume proxy, new-low area, fixed normalization and score, and signed blocker-count updates. Production score→A→H order and separate cohort natural-pair tie rule are correctly distinguished. N contributes constant +0.05.
- Score preferences are declared rather than learned or elicited. No stakeholder-validation, architectural-quality gain or general optimization superiority is claimed.
- Table 1 bounds and Table 3 cohort correlations, MAEs and exact-match counts match independent_results.json. The 0.45 m² MAE is explicitly one 9 m² cell discrepancy averaged over 20, not sub-grid accuracy. Cohorts remain nonprobability same-site evidence.
- Table 4's four runtime medians and ratios match independent recomputation. The 482.927 comparison is limited to two matched single-thread unindexed implementations, including B preparation; it is not a speedup over Honeybee or optimized solvers generally.
- Table 5 and Figure 3 match translation_outcome_comparison.csv. Legacy failures remain visible. Four actual corrections and one unchanged reuse are not relabeled five new simulations, volume matching, or construction validation.
- Geometry and inference conditions are explicit: approximate canonical bounding-box unions/overlaps, receivers outside/off boundaries, no actual polygon holes, fixed rays, active-sun issue, fixed grid/day, assumed north, differing HB/pvlib vectors, constant WEA carrier, and no new physical cloud run.
- Historical 112-test claim is supported by LOCAL_FINAL_REPORT.md and HANDOFF_TO_WEB.md as a historical integrated record, not claimed as a newly executed test suite here.
- Related-work distinctions are bounded and do not claim unsupported superiority. References were checked against publisher/author-institution sources, including Compagnon, Czachura, De Luca, Konis, pvlib, Ladybug and Radiance. No fabricated reference found. Ladybug's publisher landing page names an extra author but its actual published PDF has exactly the two authors cited in this manuscript; no correction is demanded on that basis.

## PDF/visual checks

All 18 pages were rendered and inspected, with detailed checks of formulas, dense tables and both scientific figures. No clipping, overlap, missing formula glyph, broken table, unexplained placeholder or out-of-page text block found. Figure 3 now visibly contains both panels matching its caption. The figure-only page has generous whitespace but is clean; this is not a blocking defect. Some bibliography entries flow to page 18 normally.

- Title/author metadata: author blank; no identifying institution, private repository URL or user identity in PDF links/metadata.
- External hyperlinks are seven scholarly DOIs and https://openai.com/ only.
- Approximately 40,927 nonwhitespace PDF-extracted characters, comfortably within the requested 10,000–50,000 range; extraction method may differ by a character or two.
- Abstract approximately 213 whitespace-delimited extracted words; readable and self-contained.
- All displayed citations, equation/table/figure references resolve in visible output; no ??, TODO, FIXME or TBD found.
- Fonts inspected with pdffonts are embedded. Letter page size recorded, with template compliance deferred to official-format review.
- AI disclosure is identity-free, describes substantial assistance and explicitly leaves author review/responsibility pending. Section citations and abstract reference are present. Acknowledgment-placement ambiguity is not resolved by this review and must remain author pending.

## Minor delivery hygiene, not scientific blockers

1. RESOLVED: the initial log retained a labels-changed warning. The writer performed a stabilization compile and reports the warning cleared with the PDF hash unchanged. No broken reference was visible. Final delivery may use the same reviewed PDF hash.
2. Ensure final manifests/readme say 18 pages for this corrected figure version rather than reusing 17-page metadata. The writer has already acknowledged this correction.

## Primary bibliography sources checked

- https://www.sciencedirect.com/science/article/pii/S0378778804000398
- https://www.mdpi.com/2075-5309/12/4/393
- https://ws.lib.ttu.ee/publikatsioonid/en/Publ/Item/246639a2-2223-4807-9e0a-c40faaf50145?langVersion=et
- https://www.sciencedirect.com/science/article/pii/S0038092X15006933
- https://joss.theoj.org/papers/10.21105/joss.00884
- https://publications.ibpsa.org/proceedings/bs/2013/papers/bs2013_2499.pdf
- https://doi.org/10.1145/192161.192286

No manuscript, translation, source, repository or frozen sample was edited. No new physics execution, local Windows access, submission or payment occurred.
