"""Colorbar layout helpers for HTI plots."""

from typing import Any, Mapping, Tuple

import matplotlib.pyplot as plt


def create_plot_colorbar(
    fig: Any,
    plot: Any,
    args: Mapping[str, Any],
    row: int,
    subplot_pos: int,
    label: str,
) -> Tuple[Any, Any]:
    """Create and label a colorbar using the layout for the current plot."""
    if args.get("row"):
        colorbar_positions = {
            4: [0.94, 0.76 - ((subplot_pos - 1) * 0.70 / (row - 1)), 0.015, 0.21],
            3: [0.94, 0.68 - ((subplot_pos - 1) * 0.60 / (row - 1)), 0.015, 0.27],
            2: [0.94, 0.50 - ((subplot_pos - 1) * 0.38 / (row - 1)), 0.015, 0.32],
        }
        position = colorbar_positions.get(row)
        if position is not None:
            colorbar_axes = fig.add_axes(position)
            colorbar = plt.colorbar(plot, cax=colorbar_axes)
            colorbar.set_label(label, fontsize=38 if args.get("met_schau") else 12)
            return colorbar_axes, colorbar

    if args.get("met_schau"):
        colorbar_axes = fig.add_axes([0.955, 0.08, 0.013, 0.87])
    else:
        colorbar_axes = fig.add_axes([0.94, 0.12, 0.015, 0.72])

    colorbar = plt.colorbar(plot, cax=colorbar_axes)
    colorbar.set_label(label, fontsize=38 if args.get("met_schau") else 12)
    return colorbar_axes, colorbar
