# Author-local protocol findings

This adds actual archived input checks to the cloud frozen-table audit; it is not a new daylight simulation. Source script: `scripts/local_protocol_audit.py`. Public-safe output: `runs/local_protocol_20261016/actual_recipe_weather_summary.csv` and `protocol_semantics.json`. Each artifact carries input, protocol, code and exact script hashes. Raw models, WEA, grid coordinates and solver files remain outside Git.

## Actual archived inputs

- All six scenes use 16 subhourly weather records at timestep=2/hour, north=0, UTC+8. Ladybug correctly interprets the WEA west-positive longitude/time-zone header; the negative header values do not mean UTC-8.
- Every actual WEA record has DNI=1000 W/m² and DHI=0. These are constant geometry/direct-sun-hours carriers, not measurements or representative annual weather.
- Actual solar source names encode minute-of-year and map in order to 08:15 through15:45 on December21. The original binary visibility matrices have16 columns, and each cumulative result equals its visibility sum times0.5h exactly. The integrated duration is8h; endpoint span is7.5h. WEA/HOY do not encode a calendar year; do not claim identical year-specific astronomical input between the archived Ladybug and pvlib reconstructions.
- `historical_solar_mapping.csv` retains the measured differences between the two effective solar algorithms. Matching solver scene rays across historical HB cases is established; identity with pvlib rays is not.
- Actual archived execution used baseline cpu-count2 and subsequent cases4, despite a baseline preparation JSON later saying4. New controlled replays use cpu-count1 and workers1 for every scene. Do not combine the old mixed-worker51.11s cost with new same-primitive A/B timings.
- All original grid normals are upward. None of the2031 fixed receivers is strictly inside, or within1e-7m of the boundary of, the canonical building union. No receiver regeneration, sorting or coordinate replacement was performed.
- Every expected roof and wall exists in each of the six actual HB dictionaries. Safe construction validates the expected face geometry. The silent-face and courtyard-hole bugs demonstrated synthetically have not been observed in this real frozen site's faces; the canonical footprints have no holes.

## Scope of the canonical model

The actual frozen geometry source is `dxf_component_bbox_union`. It approximates building groups and shares some components across different IDs. `footprint_overlap_audit.csv` records aggregate overlap areas without polygons or coordinates. The archived original OBJ/canonical audit already reports important disagreements for C6, C13, C24 and C33; it is not a ground-truth geometry certification.

Consequently, matched A/B equality, controlled legacy reproduction and contained-translation checks apply to this frozen computational model. They do not establish surveyed footprint accuracy, true-north registration, structural feasibility, property authorization, annual daylight quality or measured real-street improvement. North=0 remains a registered modeling assumption. Changing the canonical boundaries would be a new scientific input version requiring new registration and explicit impact review; this run does not silently perform it or reselect the original20.

## Regression and temporal provenance

The original protocol and original20 sample remain unchanged. The normalization-source identity amendment and first failed attempt are retained in `LOCAL_FAILURE_HISTORY.md`. The Windows working protocol hash differs from its Git LF blob hash only by checkout line endings; record both forms explicitly rather than silently replacing an old experiment's config hash. New local output files are pinned as binary/text-unconverted evidence in `.gitattributes`.

The2/4 historical cpu split, raw file hashes and exact time mapping come from the actual archived files, not cloud environment inference. Final controlled HB success and full repeated speedup remain subject to their own completed-run reports.
