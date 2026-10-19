#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Use a standard TeX Live/MiKTeX installation. This optional fallback is local only.
if [ -f /workspace/scratch/8f97152a4ac6/texbuild/env.sh ]; then
  . /workspace/scratch/8f97152a4ac6/texbuild/env.sh
fi
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdftotext -layout manuscript.pdf manuscript.txt
