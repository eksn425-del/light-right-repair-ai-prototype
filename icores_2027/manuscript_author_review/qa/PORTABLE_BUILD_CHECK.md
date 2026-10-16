# Clean source-bundle build check

The anonymous source ZIP was extracted into a fresh temporary directory. The supplied `build_portable.sh` ran PDFLaTeX, BibTeX, PDFLaTeX and PDFLaTeX using the same installed compiler and workspace-local dependency lookup configuration required by this container. No files were obtained from the manuscript working directory except compiler/dependency resources.

The rebuilt PDF is byte-for-byte identical to the delivered PDF:

`09c362af34cba12b5752b724b8d698a5e20dd6d7847b891a920bdccbde358028`

The source bundle is therefore complete for this tested compiler/dependency set. A normal TeX Live/MiKTeX installation must provide the listed font/packages; this is not a claim of testing every TeX distribution. No font files are redistributed.
