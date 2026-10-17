#!/bin/sh
# Requires a normal TeX Live/MiKTeX installation with newtx and tex-gyre.
set -eu
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
