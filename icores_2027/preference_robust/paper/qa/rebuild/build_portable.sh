#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Standard TeX Live/MiKTeX with LNCS dependencies, Computer Modern Type1 fonts.
# In this restricted cloud image, source /workspace/scratch/8f97152a4ac6/texbuild/env.sh first.
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
cp manuscript.pdf anonymous_regular_submission.pdf
