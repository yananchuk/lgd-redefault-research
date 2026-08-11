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


def _draw_bias_sweep(
    ax: Axes,
    summary: pd.DataFrame,
    sweep_param: str,
    x_as_percent: bool,
    stat: str = "mean",
    x_log: bool = False,
) -> None:
    """Draw each formula's relative-error mean or SD against a swept parameter, onto an existing Axes."""
    x = summary[sweep_param]
    for formula, color in FORMULA_COLORS.items():
        ax.plot(
            x,
            summary[f"{formula}_{stat}"],
            label=FORMULA_LABELS[formula],
            color=color,
            linewidth=2,
            linestyle=FORMULA_LINESTYLES[formula],
        )
    ax.set_ylabel("Relative error" if stat == "mean" else "Error SD")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
    if x_as_percent:
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    if x_log:
        ax.set_xscale("log")


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
    summary: pd.DataFrame,
    sweep_param: str,
    x_label: str,
    title: str,
    x_as_percent: bool = True,
    stat: str = "mean",
    x_log: bool = False,
) -> Figure:
    """Plot each formula's relative-error mean or SD against a swept parameter.

    Args:
        summary: Output of `metrics.summarize`, one row per sweep value.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Chart title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.
        stat: Which per-formula statistic to plot, "mean" (bias) or "sd".
        x_log: Whether to plot the x-axis on a log scale, useful when the
            sweep spans multiple orders of magnitude.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, ax = plt.subplots()
    _draw_bias_sweep(ax, summary, sweep_param, x_as_percent, stat=stat, x_log=x_log)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_bias_variance_decomposition(
    summary: pd.DataFrame, sweep_param: str, x_label: str, title: str, x_log: bool = True
) -> Figure:
    """Plot each formula's bias and standard deviation side by side against a swept parameter.

    Args:
        summary: Output of `metrics.summarize`, one row per sweep value.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Figure title.
        x_log: Whether to plot the x-axis on a log scale, useful when the
            sweep spans multiple orders of magnitude.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, (ax_bias, ax_sd) = plt.subplots(1, 2, figsize=(FIGURE_SIZE[0] * 1.7, FIGURE_SIZE[1]))

    _draw_bias_sweep(ax_bias, summary, sweep_param, x_as_percent=False, stat="mean", x_log=x_log)
    ax_bias.set_title("Bias")
    ax_bias.set_xlabel(x_label)

    _draw_bias_sweep(ax_sd, summary, sweep_param, x_as_percent=False, stat="sd", x_log=x_log)
    ax_sd.set_title("Standard deviation")
    ax_sd.set_xlabel(x_label)
    ax_sd.set_ylabel(None)

    handles, labels = ax_bias.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.05))
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    return fig


def plot_regime_comparison(
    naive_summary: pd.DataFrame,
    compliant_summary: pd.DataFrame,
    sweep_param: str,
    x_label: str,
    title: str,
    x_as_percent: bool = True,
    left_title: str = "Naive estimation",
    right_title: str = "Compliant estimation (9-month merge)",
) -> Figure:
    """Plot each formula's bias side by side under two regimes, e.g. naive vs merge-compliant estimation.

    Args:
        naive_summary: Output of `metrics.summarize` for the left panel, e.g.
            the "naive" regime rows of `experiment.run_merge_compliance`'s
            output, or a correctly specified DGP's `run_baseline` output.
        compliant_summary: Same, for the right panel.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Figure title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.
        left_title: Left panel's own title.
        right_title: Right panel's own title.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, (ax_naive, ax_compliant) = plt.subplots(
        1, 2, figsize=(FIGURE_SIZE[0] * 1.7, FIGURE_SIZE[1])
    )

    _draw_bias_sweep(ax_naive, naive_summary, sweep_param, x_as_percent)
    ax_naive.set_title(left_title)
    ax_naive.set_xlabel(x_label)

    _draw_bias_sweep(ax_compliant, compliant_summary, sweep_param, x_as_percent)
    ax_compliant.set_title(right_title)
    ax_compliant.set_xlabel(x_label)
    ax_compliant.set_ylabel(None)

    handles, labels = ax_naive.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.05))
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    return fig


def plot_levels_regime_comparison(
    naive_summary: pd.DataFrame,
    compliant_summary: pd.DataFrame,
    sweep_param: str,
    x_label: str,
    title: str,
    x_as_percent: bool = True,
) -> Figure:
    """Plot LGD_true and each formula's predicted LGD level side by side under naive vs compliant estimation.

    Args:
        naive_summary: Output of `metrics.summarize` restricted to the "naive"
            regime rows of `experiment.run_merge_compliance`'s output.
        compliant_summary: Same, restricted to the "compliant" regime rows.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Figure title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, (ax_naive, ax_compliant) = plt.subplots(
        1, 2, figsize=(FIGURE_SIZE[0] * 1.7, FIGURE_SIZE[1])
    )

    _draw_lgd_levels(ax_naive, naive_summary, sweep_param, x_as_percent)
    ax_naive.set_title("Naive estimation")
    ax_naive.set_xlabel(x_label)

    _draw_lgd_levels(ax_compliant, compliant_summary, sweep_param, x_as_percent)
    ax_compliant.set_title("Compliant estimation (9-month merge)")
    ax_compliant.set_xlabel(x_label)
    ax_compliant.set_ylabel(None)

    handles, labels = ax_naive.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.05))
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    return fig


def _draw_adjustment_comparison(
    ax: Axes, summary: pd.DataFrame, sweep_param: str, stat: str = "mean"
) -> None:
    """Draw lgd_new's relative-error mean or SD against its segmented-recovery variant's, onto an existing Axes.

    A two-series chart rather than the usual four, so it doesn't reuse
    `_draw_bias_sweep`, which iterates over the fixed `FORMULA_COLORS` set.
    """
    x = summary[sweep_param]
    ax.plot(
        x,
        summary[f"lgd_new_error_{stat}"],
        label="Re-default-aware",
        color=FORMULA_COLORS["lgd_new_error"],
        linewidth=2,
        linestyle=FORMULA_LINESTYLES["lgd_new_error"],
    )
    ax.plot(
        x,
        summary[f"lgd_new_adj_error_{stat}"],
        label="Adjusted",
        color="#7b3fa0",
        linewidth=2,
        linestyle="-.",
    )
    ax.set_ylabel("Relative error" if stat == "mean" else "Error SD")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))


def plot_adjustment_comparison(
    naive_summary: pd.DataFrame,
    compliant_summary: pd.DataFrame,
    sweep_param: str,
    x_label: str,
    title: str,
    x_as_percent: bool = True,
    left_title: str = "Naive estimation",
    right_title: str = "Compliant estimation (9-month merge)",
) -> Figure:
    """Plot `lgd_new`'s relative error against its segmented-recovery variant, under two regimes.

    Args:
        naive_summary: Aggregated per-sweep-value means for `lgd_new_error` and
            `lgd_new_adj_error` under naive estimation (see
            `experiment.run_adjustment_comparison`).
        compliant_summary: Same, under merge-compliant estimation.
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Figure title.
        x_as_percent: Whether the swept parameter is a 0-1 fraction (formatted
            as a percentage) rather than a plain count or other unit.
        left_title: Left panel's own title.
        right_title: Right panel's own title.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, (ax_naive, ax_compliant) = plt.subplots(
        1, 2, figsize=(FIGURE_SIZE[0] * 1.7, FIGURE_SIZE[1])
    )

    _draw_adjustment_comparison(ax_naive, naive_summary, sweep_param)
    ax_naive.set_title(left_title)
    ax_naive.set_xlabel(x_label)

    _draw_adjustment_comparison(ax_compliant, compliant_summary, sweep_param)
    ax_compliant.set_title(right_title)
    ax_compliant.set_xlabel(x_label)
    ax_compliant.set_ylabel(None)

    if x_as_percent:
        ax_naive.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
        ax_compliant.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))

    handles, labels = ax_naive.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.05))
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    return fig


def plot_adjustment_bias_variance_decomposition(
    summary: pd.DataFrame, sweep_param: str, x_label: str, title: str, x_log: bool = True
) -> Figure:
    """Plot `lgd_new`'s bias and SD side by side against its segmented-recovery variant's.

    Args:
        summary: Aggregated per-sweep-value mean and SD for `lgd_new_error`
            and `lgd_new_adj_error` (see `experiment.run_adjustment_complexity_sweep`).
        sweep_param: Name of the swept column, used as the x-axis values.
        x_label: Human-readable x-axis label.
        title: Figure title.
        x_log: Whether to plot the x-axis on a log scale, useful when the
            sweep spans multiple orders of magnitude.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, (ax_bias, ax_sd) = plt.subplots(1, 2, figsize=(FIGURE_SIZE[0] * 1.7, FIGURE_SIZE[1]))

    _draw_adjustment_comparison(ax_bias, summary, sweep_param, stat="mean")
    ax_bias.set_title("Bias")
    ax_bias.set_xlabel(x_label)
    if x_log:
        ax_bias.set_xscale("log")

    _draw_adjustment_comparison(ax_sd, summary, sweep_param, stat="sd")
    ax_sd.set_title("Standard deviation")
    ax_sd.set_xlabel(x_label)
    ax_sd.set_ylabel(None)
    if x_log:
        ax_sd.set_xscale("log")

    handles, labels = ax_bias.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.05))
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    return fig


def _draw_rmse_sweep(ax: Axes, summary: pd.DataFrame, x_column: str, x_log: bool) -> None:
    """Draw each formula's RMSE against a swept complexity parameter, onto an existing Axes."""
    x = summary[x_column]
    for formula, color in FORMULA_COLORS.items():
        ax.plot(
            x,
            summary[f"{formula}_rmse"],
            label=FORMULA_LABELS[formula],
            color=color,
            linewidth=2,
            linestyle=FORMULA_LINESTYLES[formula],
        )
    ax.set_ylabel("RMSE")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=2))
    if x_log:
        ax.set_xscale("log")


def plot_rmse_sweep(
    summary: pd.DataFrame, x_column: str, x_label: str, title: str, x_log: bool = True
) -> Figure:
    """Plot each formula's RMSE against a swept complexity parameter.

    Args:
        summary: Output of `metrics.summarize_rmse`, one row per sweep value.
        x_column: Name of the column to use as the x-axis (e.g. `n_exposures`
            or `n_redefault_mean`).
        x_label: Human-readable x-axis label.
        title: Chart title.
        x_log: Whether to plot the x-axis on a log scale, useful when the
            sweep spans multiple orders of magnitude.

    Returns:
        The rendered figure, ready to save or display.
    """
    set_style()
    fig, ax = plt.subplots()
    _draw_rmse_sweep(ax, summary, x_column, x_log)
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
