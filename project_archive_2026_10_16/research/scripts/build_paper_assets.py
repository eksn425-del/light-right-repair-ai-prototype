"""Build the final SOICT paper-assets package from frozen evidence.

This script is intentionally a packaging step. It reads the frozen run, copies
paper figures, derives paper-facing table CSVs, and writes provenance files. It
does not rerun an experiment or alter any source result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


SOURCE_COMMIT = "6b64fe43451e2e0330930a5677cbe3432307282b"
SOURCE_BRANCH = "research-repro-v1"
SOURCE_TAG = "soict-2026-write-ready-v1"
RUN_ID = "baseline_20260909_clean"
ASSET_VERSION = "soict-paper-assets-v1"


def sha256(path: Path) -> str:
    """Return the SHA256 digest of one generated asset."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_required(source: Path, destination: Path) -> None:
    """Copy one required file and fail clearly when frozen evidence is missing."""

    if not source.exists():
        raise FileNotFoundError(f"Required frozen evidence is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def save_csv(frame: pd.DataFrame, destination: Path) -> None:
    """Write one paper-facing CSV with stable UTF-8 BOM encoding."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False, encoding="utf-8-sig")


def rerender_runtime_figure(run_dir: Path, destination: Path) -> None:
    """Re-render the frozen runtime plot at 320 dpi from its JSON summary."""

    summary = json.loads((run_dir / "results" / "runtime_summary_v2.json").read_text(encoding="utf-8"))
    rows = [
        ("2.5D screening\nmedian", summary["screening_median_seconds"]),
        ("HB scene\nmedian", summary["hb_median_seconds_per_scene"]),
        ("HB 630\nserial-equivalent", summary["serial_equivalent_hb_630_seconds"]),
    ]
    fig, ax = plt.subplots(figsize=(7, 4), dpi=320)
    ax.bar([row[0] for row in rows], [row[1] or 0 for row in rows], color=["#2a9d8f", "#e9c46a", "#e76f51"])
    ax.set_ylabel("Wall time / seconds")
    ax.set_title("Measured screening/HB scene time and serial-equivalent extrapolation")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=320)
    plt.close(fig)


def rerender_sensitivity_figure(run_dir: Path, destination: Path) -> None:
    """Re-render the frozen four-term robustness plot at 320 dpi."""

    source = pd.read_csv(run_dir / "results" / "candidate_rank_stability_v2.csv")
    top = source.head(20).sort_values("top10_selection_frequency")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=320)
    ax.barh(top["candidate_id"], top["top10_selection_frequency"], color="#2878b5")
    ax.set_xlabel("Top-10 selection frequency under +/-20% weight perturbation")
    ax.set_title("Four-term production-score ranking robustness")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=320)
    plt.close(fig)


def export_vector_companions(png_path: Path, vector_dir: Path) -> None:
    """Export PDF/SVG companions as vector containers with the PNG embedded."""

    # The source plots are raster figures. These companions preserve the exact
    # pixels in a publication-friendly container; they are not claimed to be
    # newly vectorized line art.
    from matplotlib.image import imread

    image = imread(png_path)
    height, width = image.shape[:2]
    fig = plt.figure(figsize=(width / 320, height / 320), dpi=320)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(image)
    ax.axis("off")
    vector_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(vector_dir / f"{png_path.stem}.pdf", format="pdf", dpi=320)
    fig.savefig(vector_dir / f"{png_path.stem}.svg", format="svg", dpi=320)
    plt.close(fig)


def write_bibliography(destination: Path) -> None:
    """Write the DOI-checked bibliography supplied for the paper package."""

    text = r'''% SOICT paper-assets bibliography.
% Metadata checked against DOI landing records, publisher/proceedings pages,
% and the project's locally archived source records on 2026-09-10.
% Entry [1] keeps the journal volume/issue citation year 1986; the Columbia
% digital landing page records the digitized item in 2020.

@article{sampson1986sunlight,
  author  = {Sampson, Tamara C. and Charo, R. Alta},
  title   = {Access to Sunlight: Resolving Legal Issues to Encourage the Use of Solar Energy},
  journal = {Columbia Journal of Environmental Law},
  year    = {1986},
  volume  = {11},
  number  = {2},
  doi     = {10.7916/cjel.v11i2.5670},
  url     = {https://doi.org/10.7916/cjel.v11i2.5670}
}

@article{bryan1986amenity,
  author  = {Bryan, Harvey and Stuebing, Susan},
  title   = {Natural Light as an Urban Amenity: Three Cities Plan for Solar Access},
  journal = {Lighting Design + Application},
  year    = {1986},
  volume  = {16},
  number  = {6},
  pages   = {44--48},
  doi     = {10.1177/036063258601600610},
  url     = {https://doi.org/10.1177/036063258601600610}
}

@article{czachura2022metrics,
  author  = {Czachura, Agnieszka and Kanters, Jouri and Gentile, Niko and Wall, Maria},
  title   = {Solar Performance Metrics in Urban Planning: A Review and Taxonomy},
  journal = {Buildings},
  year    = {2022},
  volume  = {12},
  number  = {4},
  pages   = {393},
  doi     = {10.3390/buildings12040393},
  url     = {https://doi.org/10.3390/buildings12040393}
}

@article{compagnon2004urban,
  author  = {Compagnon, R.},
  title   = {Solar and Daylight Availability in the Urban Fabric},
  journal = {Energy and Buildings},
  year    = {2004},
  volume  = {36},
  number  = {4},
  pages   = {321--328},
  doi     = {10.1016/j.enbuild.2004.01.009},
  url     = {https://doi.org/10.1016/j.enbuild.2004.01.009}
}

@article{sanaieian2014block,
  author  = {Sanaieian, Haniyeh and Tenpierik, Martin and van den Linden, Kees and Mehdizadeh Seraj, Fatemeh and Mofidi Shemrani, Seyed Majid},
  title   = {Review of the Impact of Urban Block Form on Thermal Performance, Solar Access and Ventilation},
  journal = {Renewable and Sustainable Energy Reviews},
  year    = {2014},
  volume  = {38},
  pages   = {551--560},
  doi     = {10.1016/j.rser.2014.06.007},
  url     = {https://doi.org/10.1016/j.rser.2014.06.007}
}

@article{curreli2016form,
  author  = {Curreli, Alessandra and Serra-Coch, Glòria and Isalgue, Antonio and Crespo, Isabel and Coch, Helena},
  title   = {Solar Energy as a Form Giver for Future Cities},
  journal = {Energies},
  year    = {2016},
  volume  = {9},
  number  = {7},
  pages   = {544},
  doi     = {10.3390/en9070544},
  url     = {https://doi.org/10.3390/en9070544}
}

@article{konis2016passive,
  author  = {Konis, Kyle and Gamas, Alejandro and Kensek, Karen},
  title   = {Passive Performance and Building Form: An Optimization Framework for Early-Stage Design Support},
  journal = {Solar Energy},
  year    = {2016},
  volume  = {125},
  pages   = {161--179},
  doi     = {10.1016/j.solener.2015.12.020},
  url     = {https://doi.org/10.1016/j.solener.2015.12.020}
}

@article{wang2024evomass,
  author  = {Wang, Likai and Janssen, Patrick and Ji, Guohua},
  title   = {Optimization-Based Design Exploration of Building Massing Typologies---EvoMass and a Typology-Oriented Computational Design Optimization Method for Early-Stage Performance-Based Building Massing Design},
  journal = {Frontiers of Architectural Research},
  year    = {2024},
  volume  = {13},
  number  = {6},
  pages   = {1400--1422},
  doi     = {10.1016/j.foar.2024.06.001},
  url     = {https://doi.org/10.1016/j.foar.2024.06.001}
}

@inproceedings{roudsari2013ladybug,
  author    = {Sadeghipour Roudsari, Mostapha and Pak, Michelle},
  title     = {Ladybug: A Parametric Environmental Plugin for Grasshopper to Help Designers Create an Environmentally-Conscious Design},
  booktitle = {Proceedings of BS2013: 13th Conference of International Building Performance Simulation Association},
  year      = {2013},
  url       = {https://publications.ibpsa.org/proceedings/bs/2013/papers/bs2013_2499.pdf}
}

@article{deluca2021reverse,
  author  = {De Luca, Francesco and Dogan, Timur and Sepúlveda, Abel},
  title   = {Reverse Solar Envelope Method. A New Building Form-Finding Method That Can Take Regulatory Frameworks into Account},
  journal = {Automation in Construction},
  year    = {2021},
  volume  = {123},
  pages   = {103518},
  doi     = {10.1016/j.autcon.2020.103518},
  url     = {https://doi.org/10.1016/j.autcon.2020.103518}
}

@inproceedings{thoring2023augmented,
  author    = {Thoring, Katja and Huettemann, Sebastian and Mueller, Roland M.},
  title     = {The Augmented Designer: A Research Agenda for Generative AI-Enabled Design},
  booktitle = {Proceedings of the Design Society},
  year      = {2023},
  volume    = {3},
  pages     = {3345--3354},
  doi       = {10.1017/pds.2023.335},
  url       = {https://doi.org/10.1017/pds.2023.335}
}

@inproceedings{jakubik2022human,
  author    = {Jakubik, Johannes and Hemmer, Patrick and V{"o}ssing, Michael and Blumenstiel, Benedikt and Bartos, Andrea and Mohr, Kamilla},
  title     = {Designing a Human-in-the-Loop System for Object Detection in Floor Plans},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  year      = {2022},
  volume    = {36},
  number    = {11},
  pages     = {12524--12530},
  doi       = {10.1609/aaai.v36i11.21522},
  url       = {https://doi.org/10.1609/aaai.v36i11.21522}
}

@article{rafsanjani2023human,
  author  = {Rafsanjani, Hamed Nabizadeh and Nabizadeh, Amir Hossein},
  title   = {Towards Human-Centered Artificial Intelligence (AI) in Architecture, Engineering, and Construction (AEC) Industry},
  journal = {Computers in Human Behavior Reports},
  year    = {2023},
  volume  = {11},
  pages   = {100319},
  doi     = {10.1016/j.chbr.2023.100319},
  url     = {https://doi.org/10.1016/j.chbr.2023.100319}
}
'''
    destination.write_text(text, encoding="utf-8")


def write_captions(destination: Path) -> None:
    """Write figure and table captions with provenance and visibility labels."""

    figures = """# Figure Captions

All figures below are tied to frozen run ID `baseline_20260909_clean`, source commit `6b64fe43451e2e0330930a5677cbe3432307282b`, and tag `soict-2026-write-ready-v1`. The labels `PUBLIC` and `PRIVATE ONLY` are release controls, not claims about scientific validity.

## Figure 1
**Caption:** Reproducible computational workflow for the proposed street-scale solar-access screening and minimum-intervention decision process. The workflow separates input normalization, low-cost 2.5D screening, selective HB-Radiance verification, composite ranking, and human review.

- Asset: `figures/png/F01_workflow.png`
- Visibility: `PUBLIC`
- Source CSV: `N/A (schematic figure)`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 2
**Caption:** Baseline direct-sun-hours field on the 3 m analysis grid. The field is shown as a site-specific diagnostic for the frozen study area and should be interpreted within the stated winter-solstice time window and sensor definition.

- Asset: `figures/png/F02_baseline_field.png`
- Visibility: `PRIVATE ONLY (site geometry may be identifiable)`
- Source CSV: `results_csv/100_HB_Radiance传感点.csv`; baseline HB cumulative result file
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 3
**Caption:** Agreement between canonical 2.5D candidate ranking and curated HB-Radiance verification. The comparison is evidence for the frozen candidate set and selected verification scenes; it is not a claim of universal transferability.

- Asset: `figures/png/F03_curated_rank_agreement.png`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`; `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 4
**Caption:** Translation of a rule-selected massing intervention into architectural design language, including the distinction between the computational rule and the human-readable operations used for review.

- Asset: `figures/png/F04_design_translation_comparison.png`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/138_最终候选规则与设计转译对比.csv`; `results/design_translation_summary.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 5
**Caption:** Point-level change map for the selected candidate relative to the baseline field. This figure is retained for the private manuscript package because the plotted point distribution can reveal the real study geometry.

- Asset: `figures/png/F05_candidate_change_map.png`
- Visibility: `PRIVATE ONLY (site geometry may be identifiable)`
- Source CSV: `results_csv/141_已复核候选Python与HB点位对齐结果.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 6
**Caption:** Frozen independent validation of the low-area screening metric against HB-Radiance outcomes. The points represent the predeclared independent sample and should be reported with its sample size and scope.

- Asset: `figures/png/F06_independent_validation_scatter.png`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_validation_results.csv`; `results/independent_validation_metrics.csv`
- Source script: `scripts/generate_figures.py`
- Run ID: `baseline_20260909_clean`

## Figure 7
**Caption:** Runtime evidence separated by measurement semantics: measured 2.5D screening repeats, measured single HB scenes, and the serial-equivalent extrapolation for 630 HB scenes. The extrapolated value is explicitly not a completed batch measurement.

- Asset: `figures/png/F07_runtime_comparison_v2.png`
- Visibility: `PUBLIC`
- Source CSV/JSON: `results/runtime_benchmark_v2.csv`; `results/runtime_summary_v2.json`
- Source script: `scripts/run_runtime_benchmark.py` (asset re-render at 320 dpi by `scripts/build_paper_assets.py`)
- Run ID: `baseline_20260909_clean`

## Figure 8
**Caption:** Robustness of the four-term production-score ranking under the preregistered scenario set and Monte Carlo weight perturbation. Frequencies describe selection within the frozen 630-candidate universe and do not establish robustness outside that universe.

- Asset: `figures/png/F08_weight_robustness_v2.png`
- Visibility: `PUBLIC`
- Source CSV: `results/weight_sensitivity_v2.csv`; `results/candidate_rank_stability_v2.csv`; `results/weight_sensitivity_summary_v2.csv`
- Source script: `scripts/run_weight_sensitivity.py` (asset re-render at 320 dpi by `scripts/build_paper_assets.py`)
- Run ID: `baseline_20260909_clean`

## Figure 9
**Caption:** Independent composite-ranking agreement between the 2.5D screening score and the HB-Radiance composite score on the frozen independent sample. Report the sample scope, fixed normalization universe, and four-term score definition with this figure.

- Asset: `figures/png/F09_independent_composite_ranking.png`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_composite_metrics.csv`; `results/independent_composite_ranking.csv`
- Source script: `scripts/validate_independent_composite.py`
- Run ID: `baseline_20260909_clean`

## Asset-format note
Each figure has a high-resolution PNG plus PDF and SVG companions. The PDF/SVG companions embed the final raster pixels in publication containers; they should not be described as newly vectorized artwork.
"""
    destination.joinpath("FIGURE_CAPTIONS.md").write_text(figures, encoding="utf-8")

    tables = """# Table Captions

All table CSVs are derived from the frozen run ID `baseline_20260909_clean`, source commit `6b64fe43451e2e0330930a5677cbe3432307282b`, and tag `soict-2026-write-ready-v1`. Derived paper CSVs remove local absolute paths; they do not alter numerical values.

## Table 1
**Caption:** Source-to-canonical geometry audit for the study model, including centroid, height, footprint, and label/group consistency checks.

- Asset: `tables/table_01_geometry_audit.csv`
- Visibility: `PRIVATE ONLY (contains site geometry and identifiers)`
- Source CSV: `results_csv/91_建筑几何一致性总表.csv`
- Source script: `scripts/build_paper_support.py` and audit pipeline
- Run ID: `baseline_20260909_clean`

## Table 2
**Caption:** Declared solar-analysis protocol, grid and sensor parameters, time window, and simulation recipe. Local input paths are intentionally removed from the paper-facing CSV.

- Asset: `tables/table_02_analysis_protocol.csv`
- Visibility: `PUBLIC`
- Source CSV: `results_csv/100_HB_Radiance场景参数表.csv`; configuration `configs/research.yaml`
- Source script: `scripts/build_paper_assets.py`
- Run ID: `baseline_20260909_clean`

## Table 3
**Caption:** Complete 630-candidate 2.5D screening universe with the four-term production-score inputs and deterministic ranking fields.

- Asset: `tables/table_03_candidate_universe.csv`
- Visibility: `PRIVATE ONLY (site-specific candidate identifiers and geometry-derived values)`
- Source CSV: `results_csv/120_canonical_2p5D完整双建筑候选排名.csv`
- Source script: `src/legacy_route_b/route_b_enumerate_2p5d_candidates.py`
- Run ID: `baseline_20260909_clean`

## Table 4
**Caption:** Curated HB-Radiance verification results and Pareto/ranking fields for the selected rule candidates. Local project-folder paths are removed.

- Asset: `tables/table_04_curated_hb_verification.csv`
- Visibility: `PRIVATE ONLY (site-specific candidate identifiers)`
- Source CSV: `results_csv/132_HB_Radiance已复核候选排名与Pareto.csv`
- Source script: HB verification and ranking pipeline
- Run ID: `baseline_20260909_clean`

## Table 5
**Caption:** Frozen independent validation metrics for the low-area screening measure against HB-Radiance outcomes.

- Asset: `tables/table_05_independent_metric_validation.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_validation_metrics.csv`
- Source script: `scripts/analyze_independent_validation.py`
- Run ID: `baseline_20260909_clean`

## Table 6
**Caption:** Rule-selected candidate and human-readable design-translation summary, including reported improvements, new low-sun areas, and human-review flags.

- Asset: `tables/table_06_design_translation.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/design_translation_summary.csv`; detailed source `results_csv/138_最终候选规则与设计转译对比.csv`
- Source script: design-translation validation pipeline
- Run ID: `baseline_20260909_clean`

## Table 7
**Caption:** Runtime measurements and semantic labels distinguishing measured, operational, research-only, and serial-equivalent quantities.

- Asset: `tables/table_07_runtime_semantics.csv`
- Visibility: `PUBLIC`
- Source JSON/CSV: `results/runtime_summary_v2.json`; `results/runtime_benchmark_v2.csv`
- Source script: `scripts/run_runtime_benchmark.py`
- Run ID: `baseline_20260909_clean`

## Table 8
**Caption:** Independent four-term composite-ranking validation metrics and row-level ranking results for the frozen N=20 sample.

- Assets: `tables/table_08_independent_composite_metrics.csv`; `tables/table_08_independent_composite_ranking.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/independent_composite_metrics.csv`; `results/independent_composite_ranking.csv`
- Source script: `scripts/validate_independent_composite.py`
- Run ID: `baseline_20260909_clean`

## Table 9
**Caption:** Four-term weight sensitivity under named scenarios and Monte Carlo candidate-rank stability under the declared perturbation protocol.

- Assets: `tables/table_09_weight_sensitivity_summary.csv`; `tables/table_09_candidate_rank_stability.csv`
- Visibility: `PUBLIC`
- Source CSV: `results/weight_sensitivity_summary_v2.csv`; `results/candidate_rank_stability_v2.csv`
- Source script: `scripts/run_weight_sensitivity.py`
- Run ID: `baseline_20260909_clean`

## CSV note
CSV files are data tables for manuscript production. They should be imported into the target SOICT template and rechecked after typesetting for rounding, column width, and reference numbering.
"""
    destination.joinpath("TABLE_CAPTIONS.md").write_text(tables, encoding="utf-8")


def write_checklist(destination: Path) -> None:
    """Write a submission checklist without inventing venue-specific limits."""

    text = """# SOICT Submission Checklist

This checklist is a hand-off aid for the frozen SOICT paper package. It is not a substitute for the current official SOICT 2026 call for papers, author kit, template, or submission system. Do not hard-code page limits, anonymity rules, or file-size limits from this file; verify them against the venue instructions immediately before submission.

## Evidence and scope

- [ ] Use only the frozen evidence identified as `soict-2026-write-ready-v1`.
- [ ] Do not alter the frozen experimental numbers while editing prose, tables, or figures.
- [ ] State that this is a site-specific computational screening and decision-support study.
- [ ] Distinguish measured HB scenes, measured 2.5D screening repeats, serial-equivalent extrapolation, operational scenes, and research-only validation scenes.
- [ ] Report the frozen independent sample size and its predeclared status.
- [ ] Do not claim universal accuracy, universal safety, or replacement of architectural judgement.

## Methods and reproducibility

- [ ] Define the 2.5D approximation, sensor/grid definition, time window, timestep, timezone, height rule, and low-sun threshold.
- [ ] State that the production score uses four config-driven terms and identify the normalization universe.
- [ ] Explain the 630-candidate universe, curated HB verification, and independent composite-ranking validation separately.
- [ ] Include the source commit, branch, tag, run ID, and software/environment details required by the venue.
- [ ] Confirm that the 630-candidate clean-ranking regression audit passed after parameter migration.
- [ ] Explain human-in-the-loop review and the boundary between computational ranking and architectural judgement.

## Figures and tables

- [ ] Use Figure 1--9 numbering exactly once and ensure every in-text reference points to the intended asset.
- [ ] Use the captions in `FIGURE_CAPTIONS.md` and `TABLE_CAPTIONS.md` as the starting point.
- [ ] Keep Figure 2 and Figure 5 in the private paper-assets repository unless the research team approves a sanitized crop.
- [ ] Check every table against its CSV source after rounding and typesetting.
- [ ] Preserve figure legends, units, sample scope, and the serial-equivalent label.
- [ ] Add alt text or accessibility metadata if required by the venue.

## References and integrity

- [ ] Use `BIBLIOGRAPHY.bib` as the source bibliography and verify the venue's required citation style.
- [ ] Check every DOI resolves and that author/title/journal/year/volume/issue/pages or article number match.
- [ ] Ensure every bibliography entry is cited in the manuscript or remove unused entries.
- [ ] Do not add AI-generated or unverified references.
- [ ] Disclose software, external data, and any human review protocol required by the venue.

## Data and release hygiene

- [ ] Do not upload CAD, DXF, DWG, SKP, OBJ, sensor-coordinate tables, Radiance intermediate files, or unauthorized real raw data to the public repository.
- [ ] Confirm the public mirror contains only the public-safe figures, derived tables, documentation, code, and ledgers.
- [ ] Confirm the private paper-assets repository access list before sharing it with collaborators.
- [ ] Remove local absolute paths, personal names, and machine-specific paths from the manuscript and supplementary files.

## Final editorial pass

- [ ] Replace internal work-package language with formal limitations language.
- [ ] Check that all claims are supported by a source figure, table, ledger entry, or cited reference.
- [ ] Run a final spelling, grammar, figure/table cross-reference, and PDF rendering check.
- [ ] Compare the final PDF against the official SOICT template and submission portal requirements.
- [ ] Archive the submitted PDF and source package with the submission timestamp and checksum.
"""
    destination.write_text(text, encoding="utf-8")


def write_package_readme(destination: Path) -> None:
    """Write a short orientation note for the web ChatGPT hand-off."""

    text = """# SOICT Paper Assets

This folder is the final paper-production hand-off derived from the frozen
evidence identified by `soict-2026-write-ready-v1`.

- Source branch: `research-repro-v1`
- Source commit: `6b64fe43451e2e0330930a5677cbe3432307282b`
- Run ID: `baseline_20260909_clean`

Use `FIGURE_CAPTIONS.md` and `TABLE_CAPTIONS.md` for the manuscript captions
and provenance. Use the CSV files in `tables/` as the only source for numeric
table values. Use `BIBLIOGRAPHY.bib` as the citation source and verify the
target SOICT template before typesetting.

Figures 2 and 5, and Tables 1, 3 and 4, are marked `PRIVATE ONLY` because they
may expose site-specific geometry or identifiers. The complete package is
intended for the private paper-assets repository. The public mirror contains
only the explicitly marked public subset.

No source CAD/DXF/DWG/SKP/OBJ, sensor coordinate table, Radiance intermediate,
or unauthorized real raw data is included here.
"""
    destination.write_text(text, encoding="utf-8")


def write_manifest(asset_root: Path, destination: Path) -> None:
    """Write a hash-backed inventory and release-control manifest."""

    rows: list[str] = []
    for path in sorted(asset_root.rglob("*")):
        if not path.is_file() or path.name == "PAPER_ASSET_MANIFEST.md":
            continue
        relative = path.relative_to(asset_root).as_posix()
        digest = sha256(path)
        rows.append(f"| `{relative}` | `{path.stat().st_size}` | `{digest}` |")
    text = f"""# Paper Asset Manifest

## Release identity

- Package: `{ASSET_VERSION}`
- Source branch: `{SOURCE_BRANCH}`
- Frozen source commit: `{SOURCE_COMMIT}`
- Frozen source tag: `{SOURCE_TAG}`
- Frozen run ID: `{RUN_ID}`
- Generated: `2026-09-10`

This package is a publication hand-off derived from frozen evidence. The build step does not rerun or modify experiments. Every figure and table has its source CSV/JSON or script and run ID recorded in `FIGURE_CAPTIONS.md` or `TABLE_CAPTIONS.md`.

## Visibility controls

- `PRIVATE ONLY` assets: Figure 2, Figure 5, Table 1, Table 3, and Table 4. Their site-specific geometry or identifiers may allow reconstruction of the study area.
- `PUBLIC` assets: Figures 1, 3, 4, 6, 7, 8, 9 and Tables 2, 5, 6, 7, 8, 9, together with documentation and bibliography.
- The complete package belongs in the private paper-assets repository. The public mirror contains only the explicitly marked public subset.

## Prohibited source material

No original CAD/DXF/DWG/SKP/OBJ, sensor coordinate table, Radiance intermediate (`.ill`, `.res`, `.hbjson`, `.wea`), or unauthorized real raw data is included in this package. Source paths in the manifest are paper provenance labels only; local absolute paths are intentionally omitted.

## Figure/table provenance

See `FIGURE_CAPTIONS.md` and `TABLE_CAPTIONS.md`. Numerical values must be copied from the listed source CSV/JSON files and not from narrative summaries.

## Bibliography verification sources

The bibliography entries include DOI URLs. The primary metadata checks used for this package include the DOI/publisher records for entries [1]--[8], [10]--[13], the official Ladybug Tools publication record and IBPSA proceedings PDF for [9], and the official AAAI proceedings page for [12]. The DOI landing record for [1] is a digitized journal item; the volume/issue citation year is retained as 1986.

## Checksums

| Asset | Bytes | SHA256 |
|---|---:|---|
{chr(10).join(rows)}
"""
    destination.write_text(text, encoding="utf-8")


def build_tables(run_dir: Path, table_root: Path) -> None:
    """Create all numbered paper-facing table CSVs without changing values."""

    results_csv = run_dir / "results_csv"
    results = run_dir / "results"
    table_root.mkdir(parents=True, exist_ok=True)

    save_csv(pd.read_csv(results_csv / "91_建筑几何一致性总表.csv"), table_root / "table_01_geometry_audit.csv")

    protocol = pd.read_csv(results_csv / "100_HB_Radiance场景参数表.csv")
    protocol_columns = [
        "scenario",
        "pair",
        "model_type",
        "sensor_count",
        "date",
        "time_range",
        "timestep",
        "grid_size_m",
        "sensor_height_m",
        "north_deg",
        "radiance_recipe",
        "intervention_volume_m3",
        "note",
    ]
    save_csv(protocol[protocol_columns], table_root / "table_02_analysis_protocol.csv")

    save_csv(pd.read_csv(results_csv / "120_canonical_2p5D完整双建筑候选排名.csv"), table_root / "table_03_candidate_universe.csv")

    curated = pd.read_csv(results_csv / "132_HB_Radiance已复核候选排名与Pareto.csv")
    if "project_folder" in curated.columns:
        curated = curated.drop(columns=["project_folder"])
    save_csv(curated, table_root / "table_04_curated_hb_verification.csv")

    save_csv(pd.read_csv(results / "independent_validation_metrics.csv"), table_root / "table_05_independent_metric_validation.csv")
    save_csv(pd.read_csv(results / "design_translation_summary.csv"), table_root / "table_06_design_translation.csv")

    summary = json.loads((results / "runtime_summary_v2.json").read_text(encoding="utf-8"))
    runtime_rows = [
        {"metric": "screening_repeat_count", "value": summary["screening_repeat_count"], "unit": "runs", "measurement_class": "measured", "notes": "complete 630-candidate 2.5D screening repeats"},
        {"metric": "screening_median_seconds", "value": summary["screening_median_seconds"], "unit": "seconds", "measurement_class": "measured", "notes": "median of complete screening repeats"},
        {"metric": "screening_iqr_seconds", "value": summary["screening_iqr_seconds"], "unit": "seconds", "measurement_class": "measured", "notes": "IQR of screening repeats"},
        {"metric": "hb_measured_scene_count", "value": summary["hb_measured_scene_count"], "unit": "scenes", "measurement_class": "measured", "notes": "measured HB scenes in runtime records"},
        {"metric": "hb_median_seconds_per_scene", "value": summary["hb_median_seconds_per_scene"], "unit": "seconds/scene", "measurement_class": "measured", "notes": "per-scene HB median"},
        {"metric": "hb_iqr_seconds_per_scene", "value": summary["hb_iqr_seconds_per_scene"], "unit": "seconds/scene", "measurement_class": "measured", "notes": "IQR of measured HB scenes"},
        {"metric": "rule_candidate_universe_count", "value": summary["rule_candidate_universe_count"], "unit": "candidates", "measurement_class": "screening_universe", "notes": "complete clean candidate universe"},
        {"metric": "rule_candidate_verification_count", "value": summary["rule_candidate_verification_count"], "unit": "candidates", "measurement_class": "operational", "notes": "curated rule candidates verified with HB"},
        {"metric": "rule_candidate_verification_fraction", "value": summary["rule_candidate_verification_fraction"], "unit": "fraction", "measurement_class": "operational", "notes": "verified curated rule candidates / 630"},
        {"metric": "operational_hb_scene_count", "value": summary["operational_hb_scene_count"], "unit": "scenes", "measurement_class": "operational", "notes": "operational workflow scenes"},
        {"metric": "research_only_validation_scene_count", "value": summary["research_only_validation_scene_count"], "unit": "scenes", "measurement_class": "research_only", "notes": "independent validation scenes"},
        {"metric": "serial_equivalent_hb_630_seconds", "value": summary["serial_equivalent_hb_630_seconds"], "unit": "seconds", "measurement_class": "serial_equivalent_extrapolated", "notes": summary["serial_equivalent_hb_630_label"]},
        {"metric": "operational_batch_elapsed_status", "value": summary["operational_batch_elapsed_status"], "unit": "status", "measurement_class": "not_measured", "notes": "no completed 630-scene HB batch elapsed time"},
        {"metric": "python_version", "value": summary["python_version"], "unit": "version", "measurement_class": "environment", "notes": "recorded run environment"},
        {"metric": "lbt_recipes_version", "value": summary["lbt_recipes_version"], "unit": "version", "measurement_class": "environment", "notes": "recorded run environment"},
    ]
    save_csv(pd.DataFrame(runtime_rows), table_root / "table_07_runtime_semantics.csv")

    save_csv(pd.read_csv(results / "independent_composite_metrics.csv"), table_root / "table_08_independent_composite_metrics.csv")
    save_csv(pd.read_csv(results / "independent_composite_ranking.csv"), table_root / "table_08_independent_composite_ranking.csv")
    save_csv(pd.read_csv(results / "weight_sensitivity_summary_v2.csv"), table_root / "table_09_weight_sensitivity_summary.csv")
    save_csv(pd.read_csv(results / "candidate_rank_stability_v2.csv"), table_root / "table_09_candidate_rank_stability.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="Frozen evidence run directory")
    parser.add_argument("--output-dir", type=Path, required=True, help="Complete paper_assets output directory")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    asset_root = args.output_dir.resolve()
    if run_dir.name != RUN_ID:
        raise ValueError(f"This release builder is pinned to run ID {RUN_ID}, received {run_dir.name}")
    asset_root.mkdir(parents=True, exist_ok=True)
    figures_png = asset_root / "figures" / "png"
    figures_vector = asset_root / "figures" / "vector"

    figure_sources = {
        "F01_workflow.png": "F01_workflow.png",
        "F02_baseline_field.png": "F02_baseline_field.png",
        "F03_curated_rank_agreement.png": "F03_curated_rank_agreement.png",
        "F04_design_translation_comparison.png": "F04_design_translation_comparison.png",
        "F05_candidate_change_map.png": "F05_candidate_change_map.png",
        "F06_independent_validation_scatter.png": "F06_independent_validation_scatter.png",
        "F09_independent_composite_ranking.png": "F09_independent_composite_ranking.png",
    }
    for destination_name, source_name in figure_sources.items():
        copy_required(run_dir / "figures" / source_name, figures_png / destination_name)
    rerender_runtime_figure(run_dir, figures_png / "F07_runtime_comparison_v2.png")
    rerender_sensitivity_figure(run_dir, figures_png / "F08_weight_robustness_v2.png")
    for png_path in sorted(figures_png.glob("F*.png")):
        export_vector_companions(png_path, figures_vector)

    build_tables(run_dir, asset_root / "tables")
    write_captions(asset_root)
    write_bibliography(asset_root / "BIBLIOGRAPHY.bib")
    write_checklist(asset_root / "SOICT_SUBMISSION_CHECKLIST.md")
    metadata = {
        "package": ASSET_VERSION,
        "source_branch": SOURCE_BRANCH,
        "source_commit": SOURCE_COMMIT,
        "source_tag": SOURCE_TAG,
        "run_id": RUN_ID,
        "figures_png": sorted(path.name for path in figures_png.glob("F*.png")),
        "tables_csv": sorted(path.name for path in (asset_root / "tables").glob("*.csv")),
        "private_only_figures": ["F02_baseline_field.png", "F05_candidate_change_map.png"],
        "private_only_tables": ["table_01_geometry_audit.csv", "table_03_candidate_universe.csv", "table_04_curated_hb_verification.csv"],
    }
    write_package_readme(asset_root / "README.md")
    (asset_root / "ASSET_BUILD_METADATA.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_manifest(asset_root, asset_root / "PAPER_ASSET_MANIFEST.md")

    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
