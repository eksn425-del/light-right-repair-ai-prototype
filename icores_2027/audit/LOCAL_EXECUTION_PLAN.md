# Local takeover, 2026-10-16

Cloud handoff `32721b622d4676be46d210c2c691cbe6a3ee2e92` was fetched and matched to the remote branch. The author explicitly authorized local execution and restricted derived-result publication. Main, historical tags and frozen sample bytes remain unchanged.

Canonical geometry (41,062 bytes), original sensors (47,443 bytes), six historical HB scene folders, WEA, sensor grids, effective sun paths, per-hour visibility and cumulative values were located in the original clean-run directory. Input identity is checked by the hash/strict loader and then independently against historical HB models.

The matched A/B benchmark uses the already frozen protocol and unmodified common intersection harness, including original saved 2.5D solar vectors after a documented schema conversion. Reconstructing that pvlib vector was checked numerically. This is not an assertion that HB uses identical directions: its effective `sunpath.mtx` is inspected separately. The benchmark must retain its pilot, nesting, budget, three repetitions, phase accounting and equality gate.

Geometry and HB replay use new local output directories. Original `.hbjson`, `.ill`, `.res`, WEA, octrees, complete rays and sensor coordinates stay outside the Git checkout. Public evidence records hashes, aggregate outcomes, coded point IDs and face IDs without coordinates.

Runtime versions differ from the cloud: local lbt-recipes 0.28.2 and original Honeybee/Radiance installation are reused. Do not apply the cloud timestamp patch without reproducing it in this version. Historical replay is performed first; any correction is an explicitly separate scene and new measured result.

All unresolved scientific gates keep readiness false. Author approval, manuscript readiness and submission remain false.
