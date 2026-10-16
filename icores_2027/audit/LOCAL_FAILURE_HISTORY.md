# Local execution failure history

1. The first matched benchmark invocation stopped before any geometry evaluation because the frozen protocol declares a normalization-table SHA256 that does not match the actual file committed in the cloud handoff. BOM and LF/CRLF transformations did not reproduce the registered hash. The committed file itself is unchanged locally. No runtime or speedup was produced by this attempt.

The original protocol is preserved byte-for-byte. A separate, pre-benchmark input-identity amendment pins the actual committed bytes and an independent frozen clean-run reference. The loader requires exact hashes plus identical pair identities and numeric agreement within the pre-existing tolerance for every A/H/V/N/score value. This is a provenance correction, not outcome tuning or a normalization refit. The origin of the erroneous cloud-recorded hash is not established by the available files.
