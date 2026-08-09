"""Shared plotting style used by every chart in this project."""

from __future__ import annotations

import io

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image

FORMULA_COLORS = {
    "lgd_basic_error": "#154785",
    "lgd_lgc_error": "#e07030",
    "lgd_prd_error": "#159568",
    "lgd_new_error": "#f5c136",
}

FORMULA_LABELS = {
    "lgd_basic_error": "Basic two-factor",
    "lgd_lgc_error": "With loss-given-cure",
    "lgd_prd_error": "With Prd correction",
    "lgd_new_error": "Re-default-aware (new)",
}

FORMULA_LINESTYLES = {
    "lgd_basic_error": "--",
    "lgd_lgc_error": "-.",
    "lgd_prd_error": (0, (3, 1, 1, 1)),
    "lgd_new_error": "-",
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
            "axes.grid": False,
            "figure.figsize": FIGURE_SIZE,
            "figure.dpi": FIGURE_DPI,
            "legend.frameon": False,
        }
    )


def _draw_lgd_levels(ax: Axes, summary: pd.DataFrame, sweep_param: str, x_as_percent: bool) -> None:
    """Draw each formula's mean predicted LGD, then LGD_true emphasized on top, onto an existing Axes."""
    x = summary[sweep_param]
    for formula, color in FORMULA_COLORS.items():
        value_column = formula.removesuffix("_error")
        ax.plot(
            x,
            summary[f"{value_column}_mean"],
            label=FORMULA_LABELS[formula],
            color=color,
            linewidth=2,
            linestyle=FORMULA_LINESTYLES[formula],
        )
    ax.plot(
        x,
        summary["lgd_true_mean"],
        label="True LGD",
        color="#0b0b0b",
        linewidth=3,
        linestyle=":",
        zorder=10,
    )
    ax.set_ylabel("LGD")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
    if x_as_percent:
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))


def _draw_bias_sweep(ax: Axes, summary: pd.DataFrame, sweep_param: str, x_as_percent: bool) -> None:
    """Draw each formula's mean relative error against a swept DGP parameter, onto an existing Axes."""
    x = summary[sweep_param]
    for formula, color in FORMULA_COLORS.items():
        ax.plot(
            x,
            summary[f"{formula}_mean"],
            label=FORMULA_LABELS[formula],
            color=color,
            linewidth=2,
            linestyle=FORMULA_LINESTYLES[formula],
        )
    ax.set_ylabel("Relative error")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
    if x_as_percent:
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))


def plot_lgd_levels(
    summary: pd.DataFrame, sweep_param: str, x_label: str, title: str, x_as_percent: bool = True
) -> Figure:
    """Plot LGD_true and each formula's mean predicted LGD against a swept DGP parameter.

    Args:
        summary: Output of `metrics.summarize`, one row per sweep value.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Chart title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, ax = plt.subplots()
    _draw_lgd_levels(ax, summary, sweep_param, x_as_percent)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_bias_sweep(
    summary: pd.DataFrame, sweep_param: str, x_label: str, title: str, x_as_percent: bool = True
) -> Figure:
    """Plot each formula's mean relative error against a swept DGP parameter.

    Args:
        summary: Output of `metrics.summarize`, one row per sweep value.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Chart title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, ax = plt.subplots()
    _draw_bias_sweep(ax, summary, sweep_param, x_as_percent)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_sweep_grid(sweeps: list[dict]) -> Figure:
    """Compose several sweeps' LGD-level and bias charts into one grid figure.

    One column per sweep, LGD levels on the top row and relative error on the
    bottom row, all sharing one legend.

    Args:
        sweeps: One dict per sweep, each with keys "summary" (output of
            `metrics.summarize`), "sweep_param", "x_label", "title", and
            optionally "x_as_percent" (defaults to `True`).

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    n = len(sweeps)
    fig, axes = plt.subplots(
        2,
        n,
        figsize=(FIGURE_SIZE[0] / 2 * n, FIGURE_SIZE[1] * 1.3),
        gridspec_kw={"height_ratios": [1, 1.2]},
    )

    for col, sweep in enumerate(sweeps):
        x_as_percent = sweep.get("x_as_percent", True)
        ax_levels, ax_error = axes[0, col], axes[1, col]

        _draw_lgd_levels(ax_levels, sweep["summary"], sweep["sweep_param"], x_as_percent)
        ax_levels.set_title(sweep["title"])

        _draw_bias_sweep(ax_error, sweep["summary"], sweep["sweep_param"], x_as_percent)
        ax_error.set_xlabel(sweep["x_label"])

        if col > 0:
            ax_levels.set_ylabel(None)
            ax_error.set_ylabel(None)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def save_grayscale_check(fig: Figure, path: str) -> None:
    """Save a grayscale rendering of a figure, to check that lines stay distinguishable without color.

    Renders the figure exactly as `savefig` would, then converts it to
    grayscale, so a project convention (colors and line styles both carry
    each series' identity) can be verified against the figure actually
    produced, rather than reasoned about in the abstract.

    Args:
        fig: The figure to check.
        path: Where to save the grayscale PNG.
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=FIGURE_DPI)
    buffer.seek(0)
    Image.open(buffer).convert("L").save(path)
