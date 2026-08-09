"""Shared plotting style used by every chart in this project."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.figure import Figure

FORMULA_COLORS = {
    "lgd_basic_error": "#2a78d6",
    "lgd_lgc_error": "#eb6834",
    "lgd_prd_error": "#1baf7a",
    "lgd_new_error": "#eda100",
}

FORMULA_LABELS = {
    "lgd_basic_error": "Basic two-factor",
    "lgd_lgc_error": "With loss-given-cure",
    "lgd_prd_error": "With Prd correction",
    "lgd_new_error": "Re-default-aware (new)",
}

FIGURE_SIZE = (10, 6)
FIGURE_DPI = 120  # 10in * 120dpi = 1200px wide, readable embedded in Markdown


def set_style() -> None:
    """Apply the shared matplotlib style used by every chart in this project."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.edgecolor": "#c3c2b7",
            "axes.grid": True,
            "grid.color": "#e1e0d9",
            "grid.linewidth": 0.6,
            "figure.figsize": FIGURE_SIZE,
            "figure.dpi": FIGURE_DPI,
            "legend.frameon": False,
        }
    )


def plot_bias_sweep(summary: pd.DataFrame, sweep_param: str, x_label: str, title: str) -> Figure:
    """Plot each formula's mean relative error against a swept DGP parameter.

    Args:
        summary: Output of `metrics.summarize`, one row per sweep value.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Chart title.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, ax = plt.subplots()

    for formula, color in FORMULA_COLORS.items():
        ax.plot(
            summary[sweep_param],
            summary[f"{formula}_mean"],
            label=FORMULA_LABELS[formula],
            color=color,
            linewidth=2,
        )

    ax.axhline(0, color="#898781", linewidth=0.8)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Mean relative error")
    ax.set_title(title)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
    ax.legend()
    fig.tight_layout()
    return fig
