"""Sunrise and sunset marker helpers for HTI plots."""

from typing import Any, Mapping, Tuple

import ephem
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


_EMPTY_INDICES = (np.array([], dtype=int),)


def _plot_marker(
    index: int,
    height: np.ndarray,
    title: str,
    met_schau: bool,
    duplicate_ceilometer_marker: bool = False,
) -> None:
    marker_x = np.ones(height.shape[1]) * index
    if met_schau:
        color = "w" if "ceilometer" in title else "k"
        plt.plot(marker_x, height[0, :], color, linestyle="dashed", linewidth=7)
        return

    plt.plot(marker_x, height[0, :], "k", linestyle="dashed")
    if duplicate_ceilometer_marker and "ceilometer" in title:
        plt.plot(marker_x, height[0, :], "w", linestyle="dashed", linewidth=7)


def plot_sunrise_sunset(
    date: Any,
    time_values: np.ndarray,
    height: np.ndarray,
    title: str,
    args: Mapping[str, Any],
) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
    """Plot sunrise/sunset markers and return their matching time indices."""
    sunrise_indices = _EMPTY_INDICES
    sunset_indices = _EMPTY_INDICES

    try:
        observer = ephem.Observer()
        observer.date = pd.to_datetime(date).strftime("20%y/%m/%d %H:%M:%S")
        observer.lon = "11.57"
        observer.lat = "48.13"
        sun = ephem.Sun()

        sunrise = pd.to_datetime(str(observer.next_rising(sun))).strftime("%H:%M")
        sunset = pd.to_datetime(str(observer.next_setting(sun))).strftime("%H:%M")
        sunrise_indices = np.where(time_values == sunrise)
        sunset_indices = np.where(time_values == sunset)
        met_schau = bool(args.get("met_schau"))

        if len(sunrise_indices[0]) != 0:
            _plot_marker(
                sunrise_indices[0][0],
                height,
                title,
                met_schau,
            )
        if len(sunset_indices[0]) != 0:
            _plot_marker(
                sunset_indices[0][0],
                height,
                title,
                met_schau,
                duplicate_ceilometer_marker=True,
            )
    except Exception:
        print("No data has been plotted")

    return sunrise_indices, sunset_indices
