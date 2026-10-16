from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the light equity project validation script.")
    parser.add_argument("--project-root", type=Path, default=Path("E:/AI项目/light_equity_project"))
    parser.add_argument("--dataset", default="sample_toy_street")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config-dir", type=Path)
    parser.add_argument("--obj", type=Path)
    parser.add_argument("--verify-candidates", action="store_true")
    parser.add_argument("--regenerate-toy", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    script = project_root / "scripts" / "validate_light_equity_pipeline.py"
    if not script.exists():
        raise FileNotFoundError(f"Project validation script not found: {script}")

    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(project_root),
        "--dataset",
        args.dataset,
        "--output-dir",
        str(args.output_dir),
    ]
    if args.config_dir:
        command += ["--config-dir", str(args.config_dir)]
    if args.obj:
        command += ["--obj", str(args.obj)]
    if args.verify_candidates:
        command.append("--verify-candidates")
    if args.regenerate_toy:
        command.append("--regenerate-toy")

    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
