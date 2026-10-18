# Verified literature and claim boundaries

Checked 2026-10-18. This is a research evidence ledger, not a manuscript or experimental result. Primary publisher pages, author-hosted manuscripts, and institutional publication records were used. Access status below distinguishes reading accessible methods from reading every page of a final published paper. Search-result dates were not treated as publication dates.

## 1. SMAA-2

**Risto Lahdelma and Pekka Salminen (2001). SMAA-2: Stochastic Multicriteria Acceptability Analysis for Group Decision Making. Operations Research 49(3), 444–454. DOI: 10.1287/opre.49.3.444.11220.**

Sources: [publisher](https://pubsonline.informs.org/doi/10.1287/opre.49.3.444.11220); [publisher PDF endpoint with indexed abstract](https://pubsonline.informs.org/doi/pdf/10.1287/opre.49.3.444.11220); [author institution](https://research.aalto.fi/en/publications/smaa-2-stochastic-multicriteria-acceptability-analysis-for-group-/).

Read status: publisher abstract and authoritative metadata verified. PDF endpoint redirects to abstract/navigation; original full text was not obtained. Do not claim full-paper reading. Operational details also checked against the later primary implementation paper below.

Supported claim: SMAA explores preference-weight space; SMAA-2 extends acceptability analysis beyond winning to all rank positions, including partial preference information. The paper also considers uncertain criterion values and confidence factors.

Boundary: no evidence here validates the proposed solar criteria, fixed weights, or real architects' preferences. Sampling weights with fixed criterion values is a restricted SMAA-style application. A Top-10 frequency is conditional on the declared sampling distribution; it is not empirical preference prevalence. Criterion uncertainty and SMAA confidence factors should not be claimed if not implemented.

## 2. Robust ordinal regression foundation

**Salvatore Greco, Vincent Mousseau, and Roman Słowiński (2008). Ordinal regression revisited: Multiple criteria ranking using a set of additive value functions. European Journal of Operational Research 191(2), 415–435. DOI: 10.1016/j.ejor.2007.08.013.**

Sources: [author-hosted published PDF](https://www.lamsade.dauphine.fr/mcda/biblio/PDF/GMS-EJOR2008.pdf); [author bibliography](https://www.lamsade.dauphine.fr/mcda/biblio/Year/2008.complete.html); [publisher](https://www.sciencedirect.com/science/article/pii/S0377221707008752).

Read status: 21-page PDF accessible; abstract, introduction, compatibility constraints, necessary/possible relations, and conclusion inspected. Printed PDF and author bibliography give 415–435; publisher search metadata gives 416–436. Use printed pagination, preserve discrepancy in the audit.

Supported claim: UTA-GMS retains all additive value functions compatible with decision-maker comparisons of reference alternatives. Necessary preference holds for every compatible function; possible preference holds for at least one. Linear-programming constraints support compatibility analysis and preference comparisons.

Boundary: the DOI does not identify a paper literally titled “Robust Ordinal Regression.” Randomly perturbing weights is not ordinal regression. Without elicited comparisons, this study should cite ROR as conceptual context and future elicitation capability, not claim a fitted or validated ROR model. Sampled unanimity does not establish necessity over a continuous model set.

## 3. Minimax regret and utility elicitation

**Craig Boutilier, Relu Patrascu, Pascal Poupart, and Dale Schuurmans (2006). Constraint-based optimization and utility elicitation using the minimax decision criterion. Artificial Intelligence 170(8–9), 686–713. DOI: 10.1016/j.artint.2006.02.003.**

Sources: [publisher](https://www.sciencedirect.com/science/article/pii/S0004370206000245); [author manuscript](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06.pdf); [author publication list](https://www.cs.toronto.edu/~cebly/papers.html).

Read status: 45-page author manuscript dated 26 February 2006 accessible. Sections 2–4 definitions and formulations, introduction's elicitation methods, and relevant guarantees inspected; publisher supplies final bibliographic record.

Supported claim: for imprecise utility, maximum regret compares a feasible decision with the best feasible alternative under adversarial compatible utility; minimax regret chooses a decision minimizing that loss. The work develops mixed-integer formulations exploiting generalized additive utility and elicitation procedures that reduce uncertainty.

Boundary: these are existing ideas, not new algorithms of the solar study. A shortlist differs from an individual decision. A scenario-based greedy shortlist cannot inherit this paper's exact minimax solution claims. No elicitation experiment exists unless people actually provide preference information. Worst observed sampled regret is not an upper bound on continuous worst-case regret.

## 4. EvoMass

**Likai Wang, Patrick Janssen, and Guohua Ji (2024). Optimization-based design exploration of building massing typologies—EvoMass and a typology-oriented computational design optimization method for early-stage performance-based building massing design. Frontiers of Architectural Research 13(6), 1400–1422. DOI: 10.1016/j.foar.2024.06.001.**

Sources: [publisher article](https://www.sciencedirect.com/science/article/pii/S2095263524000797); [DOI publisher version](https://doi.org/10.1016/j.foar.2024.06.001); [journal record](https://journal.hep.com.cn/foar/EN/1159778666085409149); [journal PDF endpoint](https://journal.hep.com.cn/foar/EN/PDF/10.1016/j.foar.2024.06.001).

Read status: publisher-indexed abstract and full-text excerpts covering sections 2–3 and figure 9 were available; journal metadata verified. Direct article/PDF opening failed, including HTTP 502 when attempting PDF retrieval. Do not claim entire full text or survey instrument was read.

Supported claim: EvoMass supports typology-oriented massing exploration through iterative optimization and designer interpretation/reconfiguration. Examples involve daylight, solar exposure, and design intent; the paper reports a user survey. Additive/subtractive generation and weighted integration of daylight/solar objectives appear in the accessible methods/caption.

Boundary: it supports architectural decision-support context, not evidence that the present solar-repair method was user-tested, physically validated, or preference-robust. No “first architect-in-the-loop optimization” claim is defensible.

## 5. SMAA implementation

**Tommi Tervonen and Risto Lahdelma (2007). Implementing stochastic multicriteria acceptability analysis. European Journal of Operational Research 178(2), 500–513. DOI: 10.1016/j.ejor.2005.12.037.**

Sources: [publisher](https://www.sciencedirect.com/science/article/pii/S0377221706000506); [author institutional record](https://research.aalto.fi/fi/publications/implementing-stochastic-multicriteria-acceptability-analysis/).

Read status: primary publisher abstract/introduction accessible in search extraction; not the complete publisher PDF. Secondary mirrors were not relied upon for additional technical claims.

Supported claim: Monte Carlo computation approximates SMAA's multidimensional integrals; outputs include rank acceptability, central weight vectors, and confidence factors. The paper studies computational complexity and numerical accuracy.

Boundary: cite this for Monte Carlo implementation precedent, not as authority for an unchecked assertion that 20,000 samples are sufficient for every candidate or a simultaneous confidence guarantee. Study-specific convergence diagnostics remain necessary. The implementation must specify the actual distribution rather than merely saying “random weights.”

## 6. Crucial shortlist prior art

**Danupon Nanongkai, Atish Das Sarma, Ashwin Lall, Richard J. Lipton, and Jun Xu (2010). Regret-Minimizing Representative Databases. Proceedings of the VLDB Endowment 3, 1114–1124. DOI: 10.14778/1920841.1920980.**

Sources: [official proceedings full text](https://vldb.org/pvldb/vol3/R99.pdf); [author copy](https://personal.denison.edu/~lalla/papers/minregret-vldb10.pdf); [DOI](https://doi.org/10.14778/1920841.1920980); [official conference program](https://www.vldb.org/archives/website/2010/program-16.htm).

Read status: official 11-page PDF accessible; abstract, problem formulation, definitions 1–4 and guarantees inspected. Printed issue is 3(1); DOI-linked catalog metadata sometimes says 3(1–2), so volume and pages are sufficient.

Supported claim: select a bounded-size representative subset, comparing its best attainable utility with the full database's best utility. Worst-case regret ratio is minimized over a class of utility functions; linear monotone functions are a central case. This is directly relevant to offering ten alternatives without requiring a fixed user utility.

Boundary: regret-based shortlist selection is established prior art. Its exact algorithmic guarantees do not transfer to arbitrary greedy code, normalized absolute regret, or a finite sampled preference domain. Distinguish absolute loss from relative regret and specify denominator handling.

## 7. Building optimization context

**Anh-Tuan Nguyen, Sigrid Reiter, and Philippe Rigo (2014). A review on simulation-based optimization methods applied to building performance analysis. Applied Energy 113, 1043–1058. DOI: 10.1016/j.apenergy.2013.08.061.**

Source: [publisher article](https://www.sciencedirect.com/science/article/pii/S0306261913007058).

Read status: publisher abstract/highlights and bibliographic record inspected, not complete text. This is a review by its own authors, used only to establish its stated scope, not as a substitute for checking particular studies.

Supported claim: building performance optimization already has extensive work on multiobjective optimization, computational efficiency, surrogate models, uncertainty, and practical adoption. The article identifies robust solutions and efficiency as challenges.

Boundary: physical/environmental uncertainty and preference uncertainty are distinct. The review does not establish novelty or accuracy of this particular repair workflow.

# Study-specific methodological recommendations

These are deductions/recommendations for the requested study, not claims that the cited authors tested this dataset.

## Definitions to freeze before evaluating results

Let D contain all 630 candidates and x_i=(normalized A_i, normalized H_i, 1-normalized V_i), with larger values always better. Let u_i(w)=w·x_i. Keep normalization fixed across preference spaces and shortlists. Document zero-range behavior. If N is constant, retain it in the historical score and audit but omit it from active discrimination.

Historical effective center is (0.45,0.35,0.15)/0.95 = (9/19,7/19,3/19), provided N contributes the same constant for all candidates. Removing that constant and scaling by positive 0.95 preserves exact score ordering, subject to a consistent tie rule. This is algebra, not an empirical validation of the weights.

Rank acceptability estimates frequency of each rank under the chosen probability measure. Sum ranks 1–10 for Top-10 acceptability. Define how ties are handled: deterministic candidate-ID ordering is reproducible but can privilege equivalent candidates; report tied boundary cases or a sensitivity variant. Average rank should be computed on all samples; worst observed rank must retain “observed.”

A full-simplex distribution can use Dirichlet(1,1,1). Uniform independent components followed by normalization do NOT give this distribution. To generate uniform ordered-simplex weights, sort draws from the exchangeable uniform simplex in descending order. This recommendation relies on symmetry: six equal-volume order regions map to one. A local perturbation needs a specified radius/concentration, support, rejection rule, seed, and sample count.

For independent Monte Carlo draws, a single acceptability proportion has estimated standard error sqrt(p_hat(1-p_hat)/M); at M=20,000 the maximum is about 0.00354, with an approximate pointwise 95% half-width 0.00693. This is not simultaneous coverage for 630 candidates, and it does not apply unchanged to deterministic grids/quasi-Monte Carlo. Include independent-seed or split-batch convergence checks and avoid emphasizing unstable last-decimal differences.

## Explicit shortlist objectives

For a nonempty shortlist S, define best attainable score B(S,w)=max_{s in S} u_s(w) and absolute regret R(S,w)=max_{i in D}u_i(w)-B(S,w). Then choose an objective explicitly:

1. Sampled minimax: minimize max_{w in W_train} R(S,w), subject to |S|=10.
2. Expected sampled regret: minimize mean_{w in W_train} R(S,w), subject to |S|=10.
3. A declared combination or lexicographic objective, with coefficients and ordering frozen.

These objectives differ. Greedily maximizing mean best score addresses mean regret, not automatically minimax regret. Selecting the ten highest individual Top-10 acceptabilities can retain redundant candidates and is not a proof of shortlist coverage. Define winner coverage as the fraction of evaluation weights for which S includes at least one global utility maximizer; account for ties.

Use independent evaluation weights, unchanged for every method. Report average, quantiles, and maximum observed regret separately for all preference spaces. A Pareto set may have a different cardinality: evaluate full Pareto as a descriptive upper-opportunity reference, and use a predeclared ten-candidate reduction rule for fair budget comparisons. Do not silently truncate Pareto using the new method and present it as an independent comparator.

## Optional exact worst-case audit for a fixed shortlist

For fixed S and a compact polyhedral weight region W, continuous worst-case absolute regret can be audited through small linear programs, without proving that S itself is an optimal shortlist. For every candidate i solve:

maximize t over w,t,
subject to w in W and t <= w·(x_i-x_s) for every s in S.

Take the maximum optimal t over i. The identity follows from max_w max_i min_s w·(x_i-x_s) = max_i max_w min_s w·(x_i-x_s). Full and ordered simplexes are polyhedral. Box-constrained local regions are also suitable; a Dirichlet density alone does not define a small local support region. Report solver status/tolerances and witness weights. Checking only the simplex vertices is insufficient for shortlist regret because its upper envelope may attain a maximum at an interior ranking boundary.

This is an independently derived verification option, not an experiment run here. It can distinguish sampled worst cases from an audited continuous worst case while keeping shortlist generation honestly heuristic.

## Permitted contribution framing

- Existing theory: SMAA rank acceptability; necessary/possible preferences; minimax regret; representative regret-minimizing subsets; architectural performance optimization.
- Potential application contribution, conditional on results: a transparent, reproducible implementation combining constrained solar interventions, multiple preference spaces, budget-matched shortlist comparisons, and explicit simulation/geometry evidence labels.
- Evidence still required: actual 630-row metrics and correlations; uncertainty sampling protocol; held-out comparison; candidate-level validation provenance; runtime reproducibility.
- Unsupported without new evidence: novel general-purpose robust optimization algorithm; architect-validated weights; real-user preference probabilities; physical-model robustness; construction feasibility; global shortlist optimality; superiority outside this candidate universe/site.

No experiments, manuscript drafting, or GitHub changes were performed in this research subtask.
