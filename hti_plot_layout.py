"""Figure and axes layout helpers for HTI plots."""

from typing import Any, Mapping, Optional, Tuple

import matplotlib.pyplot as plt


LayoutResult = Tuple[Any, Any, Optional[int], Optional[int], Optional[int]]


def create_plot_axes(args: Mapping[str, Any]) -> LayoutResult:
    """Create the figure and axes for a standard or meteorological plot."""
    try:
        row = args["row"]
        col = args["col"]
        subplot_pos = args["subplot_pos"]

        if col == 1:
            if subplot_pos == 1:
                fig, ax = plt.subplots(
                    row,
                    col,
                    figsize=args.get("figsize", (15, 10)),
                )
            else:
                fig = plt.gcf()

            ax = plt.subplot(row, col, subplot_pos)
            if row == 4:
                ax.set_position(
                    [0.05, 0.76 - ((subplot_pos - 1) * 0.70 / (row - 1)), 0.88, 0.21]
                )
            elif row == 3:
                ax.set_position(
                    [0.05, 0.68 - ((subplot_pos - 1) * 0.60 / (row - 1)), 0.88, 0.26]
                )
            elif row == 2:
                ax.set_position(
                    [0.05, 0.50 - ((subplot_pos - 1) * 0.38 / (row - 1)), 0.88, 0.32]
                )

            return fig, ax, row, col, subplot_pos
    except (KeyError, TypeError, ValueError):
        pass

    if args.get("met_schau"):
        fig, ax = plt.subplots(1, 1, figsize=(60.3, 16.48))
        ax.set_position([0.126, 0.12, 0.867, 0.77])
    else:
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.set_position([0.09, 0.10, 0.84, 0.75])

    return fig, ax, None, None, None
