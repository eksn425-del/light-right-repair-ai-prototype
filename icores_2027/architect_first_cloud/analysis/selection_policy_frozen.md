# Frozen selection policy

Source: research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py, lines 224–259.
The production preference score is 0.45 nA + 0.35 nH + 0.15 (1-nV) + 0.05 (1-nN), using frozen full630 normalization bounds, with no clipping/refitting. N=0 gives constant +0.05 and no ranking influence.
Production sorts score descending, then A descending, then H descending. No exact score ties occur in this630. This reanalysis uses stable source-row order for any residual complete-key tie; no observed ranking depends on that extension. This is not a newly tuned preference policy.
Top10 filters A>0, then takes the first10. Pareto maximizes A and minimizes nominal V, with one strict improvement required; it is not four-objective Pareto. All12 front members have A>0. Three overlap Top10.
Historical review selection is Top10(10) union nonzero-front(12) union historical pairs C6,C33 and C13,C24(2) union controls C3,C19 and C26,C35(2), giving10+12+2+2-3=23. These controls are candidate pairs, not the no-intervention baseline scenario. The additional frozen20 are disjoint same-site coverage candidates, not random or independent-site samples.
The candidate table joins rule-level HB and translated-design evidence separately. All10 shortlist entries have archived rule HB results, but only3 have archived design-translation checks. Neither establishes construction readiness.
