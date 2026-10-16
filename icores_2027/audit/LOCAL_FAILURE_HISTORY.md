# Local execution failure history

1. The first matched benchmark invocation stopped before any geometry evaluation because the frozen protocol declares a normalization-table SHA256 that does not match the actual file committed in the cloud handoff. BOM and LF/CRLF transformations did not reproduce the registered hash. The committed file itself is unchanged locally. No runtime or speedup was produced by this attempt.

The original protocol is preserved byte-for-byte. A separate, pre-benchmark input-identity amendment pins the actual committed bytes and an independent frozen clean-run reference. The loader requires exact hashes plus identical pair identities and numeric agreement within the pre-existing tolerance for every A/H/V/N/score value. This is a provenance correction, not outcome tuning or a normalization refit. The origin of the erroneous cloud-recorded hash is not established by the available files.

2. Initial historical face equality incorrectly compared JSON lists with Honeybee tuples. Counts and identifiers matched. JSON-normalizing the regenerated dictionaries, without rounding or tolerances, gives exact equality for all six historical models. This was a representation error in the new inspection script, not an altered historical model.

3. First local test run: 80 passed, one failed. The frozen SVG manifest hash did not match the Windows checkout because Git's text conversion changed line endings. The working file had no Git diff before repair. Restore the exact committed blob mechanically and pin this SVG plus new local-run evidence as `-text`; do not regenerate a favorable picture or replace its registered hash. The 15 separate anonymity tests were not part of this initial command.

4. Expanded local run including the 15 anonymity tests: 95 passed, one failed. The same Git line-ending issue affected `skeleton.tex` versus its cloud build record. This is not a new local TeX build. Restore the unchanged committed source and pin its bytes; retain the original cloud PDF and build provenance. No manuscript was compiled locally or declared complete.
