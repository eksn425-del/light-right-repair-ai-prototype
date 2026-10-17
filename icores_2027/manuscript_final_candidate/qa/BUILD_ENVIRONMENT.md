# Workspace-local LaTeX build

Original source has not been edited. Test build is in `texbuild/test/manuscript.pdf`.

## Build an arbitrary copy of the manuscript

```sh
. /workspace/scratch/8f97152a4ac6/texbuild/env.sh
cd /absolute/path/to/manuscript-copy
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

`env.sh` only changes the current shell process environment. No system or persistent configuration was changed. Installed TeX distribution lacks usable filename databases and format files; explicit lookup paths restore access to installed package/font files. The format was generated locally using the installed pdfTeX and LaTeX distribution. A missing global pdftex.map is harmless here because the manuscript explicitly loads newtx.map, qtm.map, txfonts.map, and cm.map.

Downloaded official CTAN packages (2026-10-17) into `texbuild/packages`:
- https://ctan.math.illinois.edu/fonts/newtx.zip
- https://ctan.math.illinois.edu/fonts/tex-gyre.zip
- https://ctan.math.illinois.edu/macros/generic/kastrup.zip

binhex.tex was generated from kastrup/binhex.ins with local pdflatex. Original source hash and test source hash match: 80a8ec9cc672cbfde811d661e083baa75c2992632b7a547101558623aab0512b.

Final test: 15 pages, 249595 bytes, all fonts embedded. No undefined references/citations, no overfull/underfull boxes. One amsmath warning: Unable to redefine math accent vec. Current default paper output is US Letter; inspect required venue dimensions before final submission.
