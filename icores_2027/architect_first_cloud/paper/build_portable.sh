#!/bin/sh
# Official LNCS class; TeX Live/MiKTeX with newtx/tex-gyre installed.
# In the current cloud workspace only, source the documented texbuild/env.sh first.
set -eu
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp manuscript.pdf anonymous_regular_submission.pdf
