from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.io.export_results import ensure_dir


def plot_candidate_scores(scores: pd.DataFrame, output_path: Path) -> Path:
    """Plot candidate scores for quick design comparison."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=160)
    ax.bar(scores["candidate_id"], scores["total_score"], color="#3b6ea8")
    ax.set_ylabel("total score")
    ax.set_title("Algorithm B candidate scores")
    ax.grid(axis="y", linewidth=0.3, alpha=0.35)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path

