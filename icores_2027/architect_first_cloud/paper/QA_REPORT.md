# Final anonymous manuscript QA

Date:2026-10-18 UTC. Status: PASS_FOR_AUTHOR_REVIEW; author approval and submission readiness are separate.

## Actual build
- Official LNCS class and bibliography style from the pinned controlled source; newtx/tex-gyre fonts, no margin/textblock overrides.
- Cloud pdflatex→bibtex→pdflatex→pdflatex, followed by stabilization after figure update. Logs in qa/; current manuscript.log has no undefined reference/citation, label-rerun, overfull or underfull boxes.
- One nonblocking installed-package warning: amsmath could not redefine math accent vec; no vec expression is used.
- FinalPDF: anonymous_regular_submission.pdf;18pages, Letter612×792pt; all14listedfonts embedded; text extractable; blankAuthor metadata; no encryption, JavaScript or form.
- SHA256:27f20bc85c92403d24c5567bc55fd3a126603f044c0a2b259af19e0584f5df0f.
- Nonwhitespace characters from final pdftotext -layout output:40926, within10000–50000. This includes extracted figure/table text and references. Slight extractor whitespace differences are irrelevant to range compliance. LaTeX source count is not used as the conference limit.
- Final source SHA256:fc4cd28bfac0d5f67e41a39d4c4623148168af3ec8d9440f002afd047286d680.

## Numeric and anonymous checks
- verify_outputs.py ran55assertions:630decisionrows,10rankedTop10,12front,23selection,all10ruleHBversus3translationchecks,alltable2numericcells,officialcharacterrange,blankmetadata/noidentifyingrepoURLs,AI disclosure, resolvedreferences,overflow,embeddedfonts and18renders. AllPASS; qa/AUTOMATED_QA.json.
- All95initialinputs were verified against pinnedGitblob identities; full630andoriginal20 hash checks passed independently. This verifies archive consistency, not rawphysics.
- Reviewer independently checked Top10, sixcohortstatisticrows, runtime ratios, volumes, correction narrative, equations and primaryreferences. See qa/INDEPENDENT_FINAL_REVIEW.md.

## Visual review of all18pages
Pages1–4:title/abstract/sectionhierarchy/equations clear. Pages5–8:bounds/workflow/methods readable, no clippedformulas. Pages9–12:cohortprotocol,Top10table,tradeoffplot and statistical/runtime tables sharp. Page13:volume table and correction text clear. Page14:two-panel correctionfigure and caption agree; intentionalfigure-onlypage. Pages15–18:discussion,limitations,conclusion,AI disclosure,references legible and uncropped. All page images in qa/rendered/page-01.png throughpage-18.png and refreshedcontacts. Independentvisualreview alsoPASS.

One initialQAdefect was found and fixed: Figure3caption describedtwo panels while firstgeneratedasset hadone. Supporting script nowgeneratesbothareaandworsened-pointpanels; finalcompiledPDFrerendered/reviewed. Initial17pagecountis supersededby18; no newscientificresultwascreatedbythisfix.

## Remaining author decisions
AI acknowledgment placement versus double-blind instructions requires author/conference confirmation; currentdisclosurecontainsnoauthoridentityandhonestlydescribessubstantialassistance. Authorsstillneedconfirmdata/textrights,priorpublicationandnon-simultaneoussubmission,authorship,competinginterestsandfinalcontent. TechnicalQAisnotanacademicmisconductguaranteeoracceptancepromise. NoPRIMORISsubmission/payment/declarationwasperformed.

## Current official template verification
Current Springer ZIP linked from ICORES was downloaded independently. llncs.cls v2.25 (2026-09-03) and splncs04.bst match byte-for-byte. Its sample PDF is also Letter 612×792pt. The redundant standalone amsmath import was removed as its documentation instructs; newtxmath still loads the needed functionality. Rebuild PDF SHA and extracted text are byte-identical, preserving all reviewed pages and translation content. Source hash above reflects this preamble-only cleanup. See handoff/TEMPLATE_VERIFICATION.json.
