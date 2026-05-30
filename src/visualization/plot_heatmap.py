from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.io.export_results import ensure_dir


def plot_sunlight_heatmap(sunlight: pd.DataFrame, output_path: Path, title: str) -> Path:
    """Plot sunlight hours as a ground heatmap-style scatter figure."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=180)
    points = ax.scatter(
        sunlight["x"],
        sunlight["y"],
        c=sunlight["sunlight_hours"],
        cmap="viridis",
        s=46,
        edgecolors="none",
    )
    dark = sunlight[sunlight["is_dark_zone"]]
    if not dark.empty:
        ax.scatter(
            dark["x"],
            dark["y"],
            facecolors="none",
            edgecolors="#d62728",
            s=70,
            linewidths=0.8,
            label="dark zone",
        )

    ax.set_title(title)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    if not dark.empty:
        ax.legend(loc="upper right", frameon=False)
    colorbar = fig.colorbar(points, ax=ax)
    colorbar.set_label("sunlight hours")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path

