from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.io.dxf_reference import analyze_dxf_reference


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract reference tables from a DXF CAD file.")
    parser.add_argument("dxf_path", type=Path, help="Path to the DXF file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "cad_reference",
        help="Directory for extracted CSV/JSON reference files.",
    )
    args = parser.parse_args()
    outputs = analyze_dxf_reference(args.dxf_path, args.output_dir)
    for key, value in outputs.items():
        if key.endswith("_data"):
            continue
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

