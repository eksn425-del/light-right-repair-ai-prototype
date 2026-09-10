"""Run an LBT direct-sun-hours manifest and record measured wall time."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def run_manifest(manifest: Path, log_dir: Path, workers: int, scope: str) -> list[dict[str, object]]:
    """Execute each manifest row and return one measured record per scenario."""

    log_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        entries = list(csv.DictReader(handle))
    for entry in entries:
        scenario = entry["scenario"]
        project_folder = Path(entry["project_folder"])
        input_json = Path(entry["input_json"])
        debug_folder = Path(entry["debug_folder"])
        stdout_path = log_dir / f"{scope}_{scenario}.log"
        started = datetime.now(timezone.utc)
        timer = time.perf_counter()
        command = [
            "lbt-recipes",
            "run",
            "direct-sun-hours",
            str(input_json),
            "-p",
            str(project_folder),
            "-w",
            str(workers),
            "-d",
            str(debug_folder),
        ]
        with stdout_path.open("w", encoding="utf-8", errors="replace") as output:
            completed = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, text=True)
        elapsed = time.perf_counter() - timer
        finished = datetime.now(timezone.utc)
        rows.append(
            {
                "scope": scope,
                "scenario": scenario,
                "input_json": str(input_json),
                "project_folder": str(project_folder),
                "start_utc": started.isoformat(timespec="seconds"),
                "end_utc": finished.isoformat(timespec="seconds"),
                "wall_seconds": f"{elapsed:.6f}",
                "exit_code": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "log": str(stdout_path),
            }
        )
        if completed.returncode != 0:
            print(f"[FAIL] {scope}/{scenario}; see {stdout_path}", file=sys.stderr)
        else:
            print(f"[PASS] {scope}/{scenario}: {elapsed:.2f}s")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    rows = run_manifest(args.manifest, args.log_dir, args.workers, args.scope)
    args.records.parent.mkdir(parents=True, exist_ok=True)
    with args.records.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["scope", "status"])
        if handle.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)
    if any(row["status"] != "PASS" for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
