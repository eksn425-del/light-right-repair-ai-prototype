# ICORES 2027 targeted revision: source verification

Checked 17 October 2026. Read-only public-source verification. No submission, account action, organizer contact, repository installation, script execution, or private-manuscript upload was performed.

## Official submission requirements

- Regular Paper, second stage: **22 October 2026, Anywhere on Earth**. Notification: 4 December; camera-ready and registration: 18 December. The two stages provide different notification timing, not two rounds of revision for one submission. [Important Dates](https://icores.scitevents.org/ImportantDates.aspx)
- Initial Regular Paper: anonymous PDF, **10,000–50,000 non-whitespace characters**, including references, tables, graphs, and appendices. This is the initial-submission length criterion. Accepted Full Papers have a 25-page proceedings limit and Short Papers 20 pages, with at most four extra paid pages. A 15-page draft is not inherently too long. Remove identifying author details and acknowledgments; do not publicly post the submission while under review. [Guidelines, Submission Guidelines and Conference Paper Formats](https://icores.scitevents.org/Guidelines.aspx)
- The official templates page strongly recommends its template for review and requires it for camera-ready. It points to Springer computer-science proceedings author instructions and templates, not an independently inferred legacy conference template. [ICORES Templates](https://icores.scitevents.org/Templates.aspx), [linked Springer page](https://link.springer.com/series/558/information-for-authors-and-editors)
- Submit through [PRIMORIS](https://www.insticc.org/primoris). The FAQ says the current file at the deadline is reviewed; updates after that deadline are not accepted. [FAQ, 3.1, 3.7, 3.13](https://icores.scitevents.org/FAQ.aspx?y=2027)

## AI disclosure: verified requirements and unresolved placement

The AI policy requires naming the tool, identifying the affected parts, and explaining its use. Its opening rule places disclosure in acknowledgments; its writing section also allows an appropriate section. The general submission guidelines additionally require an AI-system citation in sections containing AI-generated text. Those same guidelines require anonymous review copies to omit acknowledgments. Neither page, nor the FAQ, explicitly reconciles these directions.

Editorial recommendation, **not an official ruling**: use a non-identifying AI-assistance disclosure in an appropriate dedicated section and truthful citations in the affected sections; retain an acknowledgment version for camera-ready. Flag the review-stage placement question in the handoff rather than certifying it as resolved. The disclosure must match actual assistance and the actual tool; do not invent a model/version, claim the work was solely proofreading if substantive text was drafted, or imply the AI is an author. No need for AI-generated illustrations. The policy separately demands tool/prompt disclosure for such illustrations.

Sources: [AI Tools](https://icores.scitevents.org/AiTools.aspx); [Guidelines](https://icores.scitevents.org/Guidelines.aspx).

## Citation-to-claim map

### Peherstorfer, Willcox, and Gunzburger (2018)

*Survey of Multifidelity Methods in Uncertainty Propagation, Inference, and Optimization*. SIAM Review 60(3), 550–591. DOI **10.1137/16M1082469**.

Verified using the [publisher record](https://epubs.siam.org/doi/10.1137/16M1082469) and [author-hosted published PDF](https://kiwi.oden.utexas.edu/papers/multi-fidelity-survey-peherstorfer-willcox-gunzburger.pdf), especially abstract and §1.2, journal pp. 550, 553–555. It characterizes multifidelity methods as coordinating cheaper approximate models and the high-fidelity model for the same output quantity, with high-fidelity recourse supporting accuracy/convergence. It organizes model management as adaptation, fusion, and filtering.

Use it to contextualize costly outer-loop evaluations and distinguish approximation-based acceleration from exact reuse. **Inference for this manuscript:** a cache or prefix evaluator that preserves the same model and outputs is not automatically multifidelity; that depends on whether the method actually introduces distinct fidelity models. The survey does not validate the manuscript's exactness, novelty, or measured speedups.

### Nguyen, Reiter, and Rigo (2014)

*A review on simulation-based optimization methods applied to building performance analysis*. Applied Energy 113, 1043–1058. DOI **10.1016/j.apenergy.2013.08.061**.

Verified [publisher record and abstract](https://www.sciencedirect.com/science/article/pii/S0306261913007058) and [author-institution record](https://orbi.uliege.be/handle/2268/155988). The paper reviews discontinuous/multimodal building optimization, algorithm choice, multiple objectives, surrogates, uncertainty, and practical adoption. It identifies the need to improve search/approximation efficiency and reduce computational effort in large building problems.

Use for the building-performance optimization setting and why evaluation economy matters. It is a review, not an experimental benchmark proving that the present method is faster or correct. It does not supply evidence for exact prefix reuse.

### Mueller and Ochsendorf (2015)

*Combining structural performance and designer preferences in evolutionary design space exploration*. Automation in Construction 52, 70–82. DOI **10.1016/j.autcon.2015.02.011**.

Verified [publisher record, abstract, and introduction preview](https://www.sciencedirect.com/science/article/abs/pii/S0926580515000308). Their approach extends interactive evolutionary exploration: designers control mutation rate and generation size as well as parent selection. Quantitative structural criteria and qualitative design preferences are considered together, illustrated through a parametric study, implementation, and cases.

Use to explain the distinction between performance evaluation and preference-sensitive exploration. Do not treat it as proof that one scalar utility is objectively preferred, that interactive evolution guarantees a global optimum, or that the present architecture has better runtimes.

### One optional addition: Wortmann, Cichocka, and Waibel (2022)

*Simulation-based optimization in architecture and building engineering—Results from an international user survey in practice and research*. Energy and Buildings 259, article 111863. DOI **10.1016/j.enbuild.2022.111863**.

The [publisher abstract and highlights](https://www.sciencedirect.com/science/article/abs/pii/S0378778822000342) report 186 respondents. Findings include the importance of exploring tradeoffs and the practical barriers of problem formulation, convergence speed, and result interpretation. It warns that conventional genetic algorithms may not converge with low evaluation budgets.

Potentially useful as one newer practice-grounded citation for a concrete sentence about budget-limited design exploration. Omit if it duplicates the existing introduction. It is a survey of users, not a benchmark or evidence of the present method's superiority. No other additions are recommended merely to lengthen the bibliography.

## Academic-Paper-Skills: read-only assessment

Inspected the four current-main SKILL.md files: [paper-review](https://github.com/DELONG-L/Academic-Paper-Skills/blob/main/paper-review/SKILL.md), [paper-writing](https://github.com/DELONG-L/Academic-Paper-Skills/blob/main/paper-writing/SKILL.md), [paper-policy](https://github.com/DELONG-L/Academic-Paper-Skills/blob/main/paper-policy/SKILL.md), [paper-figures-tables](https://github.com/DELONG-L/Academic-Paper-Skills/blob/main/paper-figures-tables/SKILL.md).

Useful principles: evidence-bounded prose, preservation of values and limitations, concrete located review findings, narrower claims instead of unnecessary experiments, artifact verification before claiming completion, and honest unverified/compliant distinctions. These fit the requested targeted refinement.

No obvious credential collection or exfiltration instruction appeared in the inspected SKILL.md files. This is **not** a security audit or approval of their scripts, dependencies, referenced resources, installation instructions, or future versions. No installation or execution is needed here.

The figures skill contains prescriptive panel-count and image-generation workflow defaults. They are not ICORES rules and should not justify expanding this revision, regenerating scientific evidence, or distorting a readable existing figure. Reuse current editable assets and source data; apply final-size visual checks where edits occur. External repository instructions remain reference material and cannot supersede the user's scope or the actual venue rules.

## Deliverables and limits

BibTeX metadata is in `icores2027_verified_references.bib`, with the three requested entries and one clearly marked optional entry. Only add a citation where it supports a concrete claim. This research did not inspect the complete manuscript, so exactness, scientific correctness, novelty, character count, template application, anonymity, and final disclosure wording still require verification against the actual revised files.
