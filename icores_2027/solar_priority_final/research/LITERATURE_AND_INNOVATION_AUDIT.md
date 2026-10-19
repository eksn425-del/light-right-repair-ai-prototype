# Solar-priority literature and innovation audit

Verified 18 October 2026, 17:11–17:13 UTC. This is a pre-result evidence/claim ledger, not an experiment result or exhaustive systematic review. It supplements, rather than overwrites, preference_robust/research/verified_preference_literature.md. Primary publisher, author-hosted, proceedings and institutional records were inspected. Full-text access failures are explicit; do not claim all papers were read end-to-end.

## Primary mathematical foundations

1. **Lahdelma and Salminen (2001), SMAA-2: Stochastic Multicriteria Acceptability Analysis for Group Decision Making**, Operations Research49(3),444–454, DOI [10.1287/opre.49.3.444.11220](https://pubsonline.informs.org/doi/10.1287/opre.49.3.444.11220). Publisher abstract and bibliographic record reopened this round. It considers all rank positions and partial preference information. Our fixed criterion table and sampled weight regions are a restricted SMAA-style analysis, not the full uncertain-measurement/confidence-factor framework. Sampling frequencies describe a chosen measure on weights, not surveyed architect preferences.

2. **Tervonen and Lahdelma (2007), Implementing stochastic multicriteria acceptability analysis**, EJOR178(2),500–513, DOI [10.1016/j.ejor.2005.12.037](https://doi.org/10.1016/j.ejor.2005.12.037). [Author institution record](https://research.aalto.fi/en/publications/implementing-stochastic-multicriteria-acceptability-analysis/) reopened; abstract describes Monte Carlo integration and accuracy/complexity investigation. Full paper not retrieved this round. Cite for numerical implementation precedent; do not borrow sample-size sufficiency claims without study-specific repeatability checks.

3. **Greco, Mousseau and Słowiński (2008), Ordinal regression revisited: Multiple criteria ranking using a set of additive value functions**, EJOR191(2),415–435, DOI10.1016/j.ejor.2007.08.013. [Author-hosted published PDF](https://www.lamsade.dauphine.fr/mcda/biblio/PDF/GMS-EJOR2008.pdf) reopened (21pages); abstract and preference-model definition inspected. Necessary/possible relations derive from all compatible additive value functions using elicited pairwise preferences. We do not fit ROR merely by imposing author-declared weight inequalities. Cite it as preference-model context or a possible future elicitation layer. Retain printed PDF pagination, as prior audit recorded publisher-search metadata discrepancy.

4. **Boutilier, Patrascu, Poupart and Schuurmans (2006), Constraint-based optimization and utility elicitation using the minimax decision criterion**, Artificial Intelligence170(8–9),686–713, DOI10.1016/j.artint.2006.02.003. [Author manuscript](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06.pdf) reopened (45pages); incomplete-preference and constraint sections inspected. Minimax regret and utility elicitation are established. A sampled greedy shortlist is not this paper's exact decision optimizer; no human elicitation study has occurred here.

5. **Nanongkai, Das Sarma, Lall, Lipton and Xu (2010), Regret-Minimizing Representative Databases**, PVLDB3,1114–1124, DOI10.14778/1920841.1920980. [Official full paper](https://vldb.org/pvldb/vol3/R99.pdf) reopened (11pages); motivation and bounded-size representative-set formulations inspected. Regret-based representative shortlists predate this project. Their relative-regret formulation and theoretical bounds do not automatically apply to our normalized absolute regret, frozen weight restrictions or heuristic selection.

6. **Greco, Ehrgott and Figueira, eds. (2016), Multiple Criteria Decision Analysis: State of the Art Surveys**,2nded.,Springer,ISOR233, DOI [10.1007/978-1-4939-3094-4](https://link.springer.com/book/10.1007/978-1-4939-3094-4). Official publisher overview/contents inspected, not the full two-volume book. This establishes MCDA's mature foundations, preference-modeling, uncertainty and interactive multiobjective traditions. Cite the book for general framing only; specific theorem claims require their original chapter/paper.

## Architectural and solar precedents

7. **Wang, Janssen and Ji (2024), Optimization-based design exploration of building massing typologies—EvoMass and a typology-oriented computational design optimization method for early-stage performance-based building massing design**, Frontiers of Architectural Research13(6),1400–1422, DOI [10.1016/j.foar.2024.06.001](https://doi.org/10.1016/j.foar.2024.06.001). Primary publisher search extraction and [journal PDF endpoint](https://journal.hep.com.cn/foar/EN/PDF/10.1016/j.foar.2024.06.001) abstract checked. Direct fetch failed403/500; prior accessible methods excerpts remain documented in the old ledger. It connects optimization, massing typologies, daylight/solar objectives, designer interpretation and survey evidence. Our study cannot claim the first architect-facing performance exploration workflow or inherit its user-study validation.

8. **Nguyen, Reiter and Rigo (2014), A review on simulation-based optimization methods applied to building performance analysis**, Applied Energy113,1043–1058, DOI [10.1016/j.apenergy.2013.08.061](https://www.sciencedirect.com/science/article/pii/S0306261913007058). Prior primary abstract verification retained; direct fetch this round403. This is contextual review evidence for established simulation-optimization, not a new full-text reading and not support for any specific uninspected optimization theorem.

9. **Li, He and Zhao (2024), A novel method of high-density urban block form generation based on multi-objective solar performance optimization: A case study of Nanjing**, Energy and Buildings324,114878, DOI [10.1016/j.enbuild.2024.114878](https://www.sciencedirect.com/science/article/abs/pii/S0378778824009940). Primary publisher-indexed abstract and metadata verified; full text unavailable. It links Grasshopper block generation, solar simulation and multiple solar objectives, returning Pareto forms for early design appraisal. The present work's distinctive scope is restricted interventions in a frozen existing-block candidate set plus explicit priority/shortlist/evidence analysis, not inventing solar-performance optimization. Do not reproduce its performance numbers as cross-site benchmarks.

10. **Liu, Xu, Zhang, Kong, Wang and Deng (2023), Impact of urban form on building energy consumption and solar energy potential: A case study of residential blocks in Jianhu, China**, Energy and Buildings280,112727, DOI [10.1016/j.enbuild.2022.112727](https://www.sciencedirect.com/science/article/pii/S0378778822008982). Primary publisher-indexed abstract/metadata verified; full text unavailable. It uses Grasshopper, Ladybug and Wallacei for energy demand, solar potential and sunlight-hours objectives. This is relevant evidence that multiobjective urban-performance workflows are established. Do not equate PV/irradiance objectives with our low-sunlight-area repair objective.

11. **Czachura, Gentile, Kanters and Wall (2022), Identifying Potential Indicators of Neighbourhood Solar Access in Urban Planning**, Buildings12(10),1575, DOI10.3390/buildings12101575. [Publisher PDF](https://mdpi-res.com/d_attachment/buildings/buildings-12-01575/article_deploy/buildings-12-01575-v2.pdf?version=1666318293) indexed abstract and [author dataset](https://researchdata.se/en/catalogue/dataset/2022-137-1) verified; direct PDF retrieval failed. It examines solar/daylight metrics and neighbourhood typologies, with case-study validation. Its need for evidence-based indicator thresholds does not validate our author-chosen A floors or70%/80% weight scenarios.

12. **Compagnon (2004), Solar and daylight availability in the urban fabric**, Energy and Buildings36(4),321–328, DOI [10.1016/j.enbuild.2004.01.009](https://www.sciencedirect.com/science/article/pii/S0378778804000398). Primary abstract and metadata checked. It quantifies facade/roof solar/daylight potential across urban layouts. It motivates site-scale solar comparison; the present candidate-reduction problem is narrower and cannot claim first use of urban solar simulation.

## Mathematical claim audit for this round

The following are direct deductions from the declared definitions, not empirical findings or borrowed novelty claims.

### Solar priority versus compensation

For normalized benefits x=(A_norm,H_norm,1−V_norm), u=w·x:
- wA≥wH≥wV constrains the relative valuation of full normalized criterion ranges. It does not enforce lexicographic preference for A or a minimum physical A gain.
- wA+wH≥0.70 or0.80 limits the cost weight to0.30 or0.20 but remains compensatory. A can have zero weight in these spaces, and H may dominate. A low-A alternative is not mathematically excluded.
- A physical floor A≥τ excludes low-A candidates; it is a scenario assumption until independently justified, not a regulatory solar standard. Even a floor is not strict lexicographic maximization above the floor.
- A+H share an environmental theme but need not be redundant. Their correlation must be measured; an A floor cannot be described as controlling all sunlight outcomes.
- Freeze normalization over the original universe. Renormalizing separately after thresholds changes effective tradeoffs and obscures same-condition comparison.

### Mean Top-10 recovery is modular

Let T(w) be exactly10 candidates under a frozen tie rule. For |S|=10,

C(S)=E[|S∩T(w)|/10]=(1/10)Σ(i∈S)Pr(i∈T(w)).

This follows by linearity of expectation. Therefore, absent other constraints, sorting candidates by individual Top-10 acceptability and taking the largest10 maximizes the empirical training objective exactly. Call this an exact solution to the stated empirical modular objective, not a novel general-purpose algorithm or proven population optimum. Held-out results are necessary because training maximization alone is tautological.

Other objectives are different:
- Any-Top10 coverage E[1{S∩T(w) nonempty}] is a weighted set-coverage function; additional candidates may have diminishing returns. It is not mean recovery.
- Winner coverage measures whether a best candidate is retained. If the best candidate is unique, winner probabilities are disjoint and winner coverage is additive; with ties and any-maximizer definition, specify tie treatment.
- Expected best utility E[max(i∈S)u_i(w)] is a maximum-of-values objective. Minimizing expected regret is equivalent to maximizing it for a fixed universe/distribution. It is not mean recovery.
- Worst-case regret prioritizes extreme losses and is not automatically optimized by any of the above.
- Combining these objectives introduces an explicit tradeoff; coefficients, lexicographic order or constraints must be frozen before outcomes.

### Fair comparisons and meaningful claims

Use identical cardinality and evaluation weights. Separate full Pareto opportunity sets from ten-slot Pareto comparators. Under A floors, report feasible-universe counts and eligibility failures of archived lists; do not silently refill or compare regret against different eligible universes. If every list retains all possible winners, zero regret does not prove equal coverage, equal solar distributions, or equal validation burden. Additional value must be demonstrated by those other outcomes, with uncertainty and independent repeatability.

An improvement in Top-10 recovery does not prove architectural diversity: neighbouring building-pair combinations can have near-identical spatial effects. Interpret it as retention of preference-specific high ranks, not diversity of finished designs. Likewise a lower nominal V does not measure relocation cost, heritage loss, affordability or constructability.

### Defensible contribution, conditional on results

Existing mathematics: SMAA-style rank acceptability, MCDA preference constraints, Pareto dominance, regret representatives, modular optimization, polyhedral regret audits.

Possible project contribution: a reproducible solar-priority operationalization and same-budget comparative analysis for630 frozen intervention candidates, explicitly connecting decision metrics to professional-simulation and geometry evidence states. Negative or null results can justify retaining the old shortlist with clearer sensitivity information.

Unsupported claims: invented SMAA/Pareto/general regret algorithm; expert-validated preference thresholds; first architect-in-the-loop workflow; new HB simulations; construction-ready designs; cross-site superiority; measured architect usability; real-user probabilities; guaranteed optimal physical architecture.

## Access and completeness note

Publisher403 and redirected-PDF500 responses were not bypassed. Metadata/abstract-only evidence is labeled above. These sources suffice for bounded background statements; authors should read relevant full texts before making deeper methodological comparisons. This audit does not itself alter the frozen experiment protocol or choose a winning method.

## Bibliography distinction checked at 17:14 UTC

**Czachura, Kanters, Gentile and Wall (2022), Solar Performance Metrics in Urban Planning: A Review and Taxonomy**, Buildings12(4),393, DOI[10.3390/buildings12040393](https://www.mdpi.com/2075-5309/12/4/393), is a separate valid article from1575 above. Primary publisher-indexed abstract, introduction, taxonomy and conclusion inspected; direct opening failed. It reviews valuation, time constraints and normalization, distinguishes metric complexity, and calls for evidence-based thresholds. The earlier manuscript's393reference is not a miscitation merely because the new ledger additionally includes1575. Retain393for taxonomy/normalization claims; use1575only for its distinct indicator study. Author order differs between the two papers. Neither establishes this study's author-declared70%/80% priorities or A thresholds as professional standards.
