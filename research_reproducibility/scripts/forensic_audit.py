"""Create a read-only forensic inventory for the Route B research package.

The audit deliberately does not execute the scientific pipeline or rewrite any
historical outputs. It records where files and historical numbers came from so
that later experiments can be run in a fresh run directory.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_info(path: Path, logical_path: str, role: str, publish_policy: str) -> dict[str, object]:
    return {
        "logical_path": logical_path,
        "source_path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else "",
        "sha256": sha256(path) if path.exists() and path.is_file() else "",
        "role": role,
        "publish_policy": publish_policy,
    }


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def inventory(source_root: Path, external_files: list[tuple[str, Path]]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = safe_rel(path, source_root)
        if path.suffix.lower() in {".obj", ".skp", ".skb", ".dxf", ".dwg", ".pdf", ".docx", ".xlsx", ".zip"}:
            role = "source_or_binary_input"
            policy = "PRIVATE_NOT_FOR_PUBLIC_REPO"
        elif "results_csv" in path.parts or path.suffix.lower() in {".csv", ".json", ".png", ".md"}:
            role = "derived_or_documentation"
            policy = "PUBLISH_ONLY_AFTER_LICENSE_AND_PRIVACY_REVIEW"
        else:
            role = "code_or_config"
            policy = "PUBLISHABLE_AFTER_REVIEW"
        entries.append(file_info(path, rel, role, policy))
    for logical, path in external_files:
        entries.append(file_info(path, logical, "private_external_input", "PRIVATE_NOT_FOR_PUBLIC_REPO"))
    return entries


def dependency_graph(source_root: Path) -> list[dict[str, str]]:
    code_root = source_root / "code"
    rows: list[dict[str, str]] = []
    for path in sorted(code_root.glob("*.py")):
        imports: set[str] = set()
        paths: set[str] = set()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"script": path.name, "imports": "", "file_references": "", "parse_error": repr(exc)})
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                if any(token in value.lower() for token in (".csv", ".obj", ".geojson", ".json", ".hbjson", ".wea")):
                    paths.add(value.replace("\\", "/"))
        rows.append(
            {
                "script": path.name,
                "imports": "; ".join(sorted(imports)),
                "file_references": "; ".join(sorted(paths)),
                "parse_error": "",
            }
        )
    return rows


def historical_map(source_root: Path) -> list[dict[str, str]]:
    results = source_root / "results_csv"
    canonical = source_root / "canonical_site_v2"
    rows: list[dict[str, str]] = []

    building_rows = csv_rows(canonical / "canonical_buildings.csv")
    building_count = len(building_rows)
    eligible_rows = [
        row
        for row in building_rows
        if str(row.get("movable", "")).strip().lower() in {"true", "1", "yes", "y"}
        and str(row.get("protected", "")).strip().lower() not in {"true", "1", "yes", "y"}
        and float(row.get("height_m", "nan")) > 3.0
    ]
    eligible_count = len(eligible_rows)
    candidate_count = len(csv_rows(results / "120_canonical_2p5D完整双建筑候选排名.csv"))
    sensor_count = len(csv_rows(results / "100_HB_Radiance传感点.csv"))
    final_rows = csv_rows(results / "138_最终候选规则与设计转译对比.csv")
    hb_rows = csv_rows(results / "131_HB_Radiance合并候选汇总结果.csv")
    hb_pairs = sorted({row.get("pair_key", "") for row in hb_rows if row.get("pair_key")})

    def add(
        claim: str,
        value: str,
        source_csv: str,
        source_column: str,
        script: str,
        upstream: str,
        reproducible: str,
        notes: str,
    ) -> None:
        rows.append(
            {
                "paper_claim": claim,
                "paper_value": value,
                "source_csv": source_csv,
                "source_column": source_column,
                "generating_script": script,
                "upstream_input": upstream,
                "reproducible_now": reproducible,
                "notes": notes,
            }
        )

    add(
        "Eligible buildings",
        str(eligible_count),
        "canonical_site_v2/canonical_buildings.csv",
        "building_id after movable/protected/height_m filter",
        "code/route_b_geometry_audit.py + route_b_enumerate_2p5d_candidates.py",
        "private source/algorithm_ready_lakeside_v2/buildings.csv and DXF/OBJ audit",
        "PARTIAL",
        f"The canonical table has {building_count} rows; {eligible_count} satisfy the current candidate eligibility rule.",
    )
    add(
        "Paired candidates",
        str(candidate_count),
        "results_csv/120_canonical_2p5D完整双建筑候选排名.csv",
        "building_ids",
        "code/route_b_enumerate_2p5d_candidates.py",
        "canonical_site_v2/canonical_buildings.csv",
        "PARTIAL",
        "Expected 36 choose 2 = 630; the clean relative-path rerun is still pending.",
    )
    add(
        "HB sensor points",
        str(sensor_count),
        "results_csv/100_HB_Radiance传感点.csv",
        "grid_id",
        "code/route_b_prepare_hb_batch.py",
        "canonical geometry and 3 m grid configuration",
        "PARTIAL",
        "Existing derived file; no new simulation was run during this audit.",
    )
    add(
        "Curated HB candidate set",
        f"{len(hb_pairs)} unique pairs in merged historical output",
        "results_csv/131_HB_Radiance合并候选汇总结果.csv",
        "pair_key",
        "code/route_b_collect_hb_merged_results.py",
        "120/123 candidate selection plus HB batch outputs",
        "PARTIAL",
        "The requested historical value 23 must be reconciled with scenario-level rows before it is used in a paper.",
    )
    add(
        "Curated Spearman rho",
        "0.883 (historical claim; unverified in this audit)",
        "results_csv/110_候选排名一致性.csv",
        "Spearman or rank column",
        "code/route_b_compare_2d_hb.py / route_b_compare_verified_2p5d_hb.py",
        "historical 2.5D and HB candidate summaries",
        "UNVERIFIED",
        "The exact row/column must be confirmed by a clean rerun; do not hard-code this value.",
    )
    add(
        "Top-3 recall",
        "0.667 (historical claim; unverified in this audit)",
        "results_csv/111_TopK召回与Pareto重叠.csv or 144_已复核TopK召回与Pareto重叠.csv",
        "topK_recall",
        "code/route_b_compare_2d_hb.py / route_b_compare_verified_2p5d_hb.py",
        "ranked 2.5D and HB candidate sets",
        "UNVERIFIED",
        "The table must be separated into curated and verified scopes.",
    )
    add(
        "Top-5 recall",
        "0.400 (historical claim; unverified in this audit)",
        "results_csv/111_TopK召回与Pareto重叠.csv",
        "topK_recall",
        "code/route_b_compare_2d_hb.py",
        "ranked 2.5D and HB candidate sets",
        "UNVERIFIED",
        "Do not describe this as global recall for all 630 candidates.",
    )
    add(
        "Top-10 recall",
        "0.800 (historical claim; unverified in this audit)",
        "results_csv/111_TopK召回与Pareto重叠.csv",
        "topK_recall",
        "code/route_b_compare_2d_hb.py",
        "ranked 2.5D and HB candidate sets",
        "UNVERIFIED",
        "Keep scope and denominator explicit.",
    )
    add(
        "Pareto overlap",
        "12/12 (historical claim; unverified in this audit)",
        "results_csv/111_TopK召回与Pareto重叠.csv or 144_已复核TopK召回与Pareto重叠.csv",
        "pareto overlap columns",
        "code/route_b_compare_2d_hb.py / route_b_compare_verified_2p5d_hb.py",
        "2.5D and HB Pareto sets",
        "UNVERIFIED",
        "Must be recomputed from explicit Pareto definitions.",
    )
    for row in final_rows:
        pair = row.get("pair_key", "")
        add(
            f"Design translation result {pair}",
            json.dumps(row, ensure_ascii=False),
            "results_csv/138_最终候选规则与设计转译对比.csv",
            "rule_low_area_drop_h3_m2; design_low_area_drop_h3_m2; design_worsened_point_count; design_new_low_area_h3_m2",
            "code/route_b_final_candidate_judgement.py",
            "132_HB_Radiance已复核候选排名与Pareto.csv and 131_HB_Radiance合并候选汇总结果.csv",
            "PARTIAL",
            "This is a historical output. The current script hard-codes pair classifications and must be refactored before reproduction.",
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--external", nargs="*", default=[])
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    repo_root = args.repo_root.resolve()
    audit_root = repo_root / "audit"
    audit_root.mkdir(parents=True, exist_ok=True)

    external_files: list[tuple[str, Path]] = []
    for spec in args.external:
        logical, raw_path = spec.split("=", 1)
        external_files.append((logical, Path(raw_path)))

    entries = inventory(source_root, external_files)
    with (audit_root / "FILE_PROVENANCE.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(entries[0].keys()))
        writer.writeheader()
        writer.writerows(entries)

    graph = dependency_graph(source_root)
    graph_lines = [
        "# Script Dependency Graph",
        "",
        "This graph is a static inventory. It does not claim that every referenced file was regenerated.",
        "",
        "| Script | Imports | File references | Parse error |",
        "|---|---|---|---|",
    ]
    for row in graph:
        graph_lines.append("| {script} | {imports} | {file_references} | {parse_error} |".format(**row))
    (audit_root / "SCRIPT_DEPENDENCY_GRAPH.md").write_text("\n".join(graph_lines) + "\n", encoding="utf-8")

    historical = historical_map(source_root)
    with (audit_root / "HISTORICAL_RESULT_MAP.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(historical[0].keys()))
        writer.writeheader()
        writer.writerows(historical)

    inventory_lines = [
        "# Project Forensic Audit",
        "",
        f"- Audit time (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Source package: '{source_root}'",
        f"- Research repository: '{repo_root}'",
        f"- Source file count: {len([row for row in entries if row['source_path']])}",
        "",
        "## Scope",
        "",
        "The June Route B package is treated as historical evidence. This audit records provenance, dependencies, and reproducibility risks before any scientific rerun.",
        "",
        "## Key findings",
        "",
        "1. The current Route B scripts contain absolute Windows paths and cannot be cleanly rerun from another checkout.",
        "2. route_b_final_candidate_judgement.py assigns statuses and reasons using fixed candidate IDs; this is not an input-driven production rule.",
        "3. Historical outputs exist for geometry, 2.5D screening, HB/Radiance batches, and design translation, but they are not silently promoted to new results.",
        "4. Raw CAD/SKP/OBJ/WEA and private team files are marked private in the provenance ledger.",
        "5. The next gate is engineering repair plus a clean baseline rerun in a new experiment directory.",
        "",
        "## Required evidence files",
        "",
        "- FILE_PROVENANCE.csv: hashes, roles, and publication policy.",
        "- SCRIPT_DEPENDENCY_GRAPH.md: static imports and path references.",
        "- HISTORICAL_RESULT_MAP.csv: paper-number traceability and verification status.",
        "",
        "## Stop conditions",
        "",
        "If required source code, data, or the Honeybee/Radiance environment is unavailable, the corresponding experiment must be marked blocked rather than simulated or filled manually.",
    ]
    (audit_root / "PROJECT_INVENTORY.md").write_text("\n".join(inventory_lines) + "\n", encoding="utf-8")
    print(json.dumps({"inventory_files": len(entries), "historical_rows": len(historical), "audit_root": str(audit_root)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
