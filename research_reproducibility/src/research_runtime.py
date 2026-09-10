"""Path, configuration, provenance, and strict parsing helpers.

All experiment scripts use this module so that a run is independent of the
checkout location and writes only to its own run directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TRUE_VALUES = {"true", "1", "yes", "y", "on"}
FALSE_VALUES = {"false", "0", "no", "n", "off"}


def strict_bool(value: Any, *, field: str = "boolean") -> bool:
    """Parse a boolean without treating the string False as true."""

    if isinstance(value, bool):
        return value
    if value is None:
        raise ValueError(f"{field} is missing")
    text = str(value).strip().lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ValueError(f"{field} has invalid boolean value: {value!r}")


def sha256(path: Path) -> str:
    """Return the SHA256 digest of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(project_root: Path) -> str:
    """Return the current commit when the project is a Git checkout."""

    try:
        return subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "NOT_A_GIT_CHECKOUT"


@dataclass(frozen=True)
class Runtime:
    """Resolved paths and settings for one reproducible experiment run."""

    project_root: Path
    config_path: Path
    run_dir: Path
    run_id: str
    source_team_root: Path
    source_dataset: Path
    source_audit: Path
    grid_size_m: float
    sensor_height_m: float
    low_threshold_h: float
    latitude: float
    longitude: float
    north_deg: float
    analysis_date: str
    start_time: str
    end_time: str
    timestep_minutes: int
    cpu_count: int
    seed: int

    @property
    def results_dir(self) -> Path:
        return self.run_dir / "results_csv"

    @property
    def figures_dir(self) -> Path:
        return self.run_dir / "figures"

    @property
    def docs_dir(self) -> Path:
        return self.run_dir / "docs"

    @property
    def logs_dir(self) -> Path:
        return self.run_dir / "logs"

    def ensure_dirs(self) -> None:
        """Create only directories owned by the current run."""

        for path in (self.run_dir, self.results_dir, self.figures_dir, self.docs_dir, self.logs_dir):
            path.mkdir(parents=True, exist_ok=True)


def _resolve(project_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (project_root / path).resolve()


def load_runtime(config_path: str | Path | None = None, run_dir: str | Path | None = None) -> Runtime:
    """Load the run configuration from YAML and resolve project-relative paths."""

    project_root = Path(__file__).resolve().parents[1]
    config = Path(config_path or os.environ.get("LIGHT_EQUITY_CONFIG", project_root / "configs" / "research.yaml"))
    if not config.is_absolute():
        config = (project_root / config).resolve()
    raw = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    paths = raw.get("paths", {})
    analysis = raw.get("analysis", {})
    run_id = os.environ.get("LIGHT_EQUITY_RUN_ID", raw.get("run_id", "unassigned_run"))
    resolved_run_dir = Path(run_dir or os.environ.get("LIGHT_EQUITY_RUN_DIR", project_root / "experiments" / run_id))
    if not resolved_run_dir.is_absolute():
        resolved_run_dir = (project_root / resolved_run_dir).resolve()
    runtime = Runtime(
        project_root=project_root,
        config_path=config.resolve(),
        run_dir=resolved_run_dir.resolve(),
        run_id=str(run_id),
        source_team_root=_resolve(project_root, paths["source_team_root"]),
        source_dataset=_resolve(project_root, paths["source_dataset"]),
        source_audit=_resolve(project_root, paths["source_audit"]),
        grid_size_m=float(analysis.get("grid_size_m", 3.0)),
        sensor_height_m=float(analysis.get("sensor_height_m", 0.1)),
        low_threshold_h=float(analysis.get("low_threshold_h", 3.0)),
        latitude=float(analysis.get("latitude", 24.55)),
        longitude=float(analysis.get("longitude", 118.03)),
        north_deg=float(analysis.get("north_deg", 0.0)),
        analysis_date=str(analysis.get("analysis_date", "2026-12-21")),
        start_time=str(analysis.get("start_time", "08:15")),
        end_time=str(analysis.get("end_time", "15:45")),
        timestep_minutes=int(analysis.get("timestep_minutes", 30)),
        cpu_count=int(analysis.get("cpu_count", 4)),
        seed=int(raw.get("seed", 20260909)),
    )
    runtime.ensure_dirs()
    return runtime


def write_run_metadata(runtime: Runtime, *, stage: str, inputs: list[Path], extra: dict[str, Any] | None = None) -> Path:
    """Write machine-readable provenance for a run stage."""

    metadata: dict[str, Any] = {
        "run_id": runtime.run_id,
        "stage": stage,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(runtime.project_root),
        "config_path": str(runtime.config_path),
        "config_sha256": sha256(runtime.config_path),
        "inputs": [
            {"path": str(path), "exists": path.exists(), "sha256": sha256(path) if path.is_file() else ""}
            for path in inputs
        ],
    }
    if extra:
        metadata.update(extra)
    path = runtime.logs_dir / f"{stage}_metadata.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
