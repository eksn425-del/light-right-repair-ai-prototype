# Single integrated final English manuscript

Locked title: Solar-Access Intervention Screening and Preference-Sensitivity Decision Support for Urban Renewal.

`manuscript.tex` is the sole editable main manuscript. `manuscript.pdf` is its compiled review output. `manuscript_expanded_for_translation.tex` is a mechanically expanded copy for faithful translation, not another manuscript version. `gate_table.tex`, `references.bib`, `llncs.cls`, and `splncs04.bst` are the required source dependencies. Run `./build.sh` with TeX Live/MiKTeX and pdftotext. Source files use the inherited Springer LLNCS class and bibliography style; no substitute conference layout was introduced.

## Provenance and scope
The English base is the complete preference-robust formal manuscript at private-repository branch `icores-2027-preference-robust`, pinned HEAD `52aee8ed48e30da0ffdaba5809e63d51a45b8b2d`, path `icores_2027/preference_robust/paper/manuscript.tex`, using its fully expanded source representation and the accompanying source bundle. The third-round analysis comes from the archived solar-priority-final report and recovered output bundle. Recovery independently matches all 159 output SHA-256 hashes/sizes in its pinned manifest. Parent evidence directories retain original files unchanged.

The final revision integrates three completed rounds. It does not run new experiments, draw new weights, optimize new lists or execute physical simulations. LaTeX compilation, PDF rendering, text extraction and numeric/source checks are document-production QA only.

## Anonymous-review handling
The PDF has empty author metadata, no author/institute names, no private repository links and no identifying acknowledgments. The private source provenance above is for the author's handoff and is not printed in the manuscript. Share the PDF alone unless the venue requests additional files. The AI-use statement is intentionally substantive and identity-free; exact model version was not recorded. Placement remains an author confirmation item because the conference's disclosure and anonymous-acknowledgment guidance are not fully reconciled.

The initial-review character check uses nonwhitespace characters extracted from the PDF, including tables, equations, references and schematic labels. It is a local proxy rather than a claimed portal implementation. See `DOCUMENT_QA.json`. No submission, public posting or remote repository write occurred.
