"""Axis formatting helpers for HTI plots."""

from typing import Any, Mapping

import numpy as np
from matplotlib.ticker import MultipleLocator


def format_plot_axes(
    ax: Any,
    dataset: Any,
    input_data: Any,
    x_ticks: Any,
    args: Mapping[str, Any],
    height: Any,
) -> None:
    """Apply shading, ticks, grid, limits, and tick locators."""
    nan_index = dataset["nan_index"]
    if np.nanmean(nan_index.values) != 0:
        facecolor = "whitesmoke" if args.get("met_schau") else "lightgrey"
        ax.axvspan(
            nan_index[0].values,
            nan_index[-1].values,
            facecolor=facecolor,
            alpha=0.8,
        )

    ax.set_xticks(x_ticks)
    if args.get("met_schau"):
        ax.grid(color="k", linestyle="--", linewidth=2)
    else:
        ax.grid(linestyle="--")
    ax.set_xlim(0, input_data.shape[0])

    if args.get("met_schau"):
        ax.tick_params(axis="both", labelsize=38)
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))
    elif args.get("offset_corrected_zoom"):
        ax.set_ylim(0, 1)
        ax.tick_params(axis="both", labelsize=15)
        ax.yaxis.set_major_locator(MultipleLocator(0.4))
        ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    else:
        ax.tick_params(axis="both", labelsize=15)
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_minor_locator(MultipleLocator(1))

    if np.nanmax(height) < 5:
        ax.yaxis.set_major_locator(MultipleLocator(0.4))
        ax.yaxis.set_minor_locator(MultipleLocator(0.2))
