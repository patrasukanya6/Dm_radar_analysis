"""Time-axis preparation helpers for HTI plots."""

from typing import Any, Mapping, Optional, Tuple

import numpy as np


TimePlotData = Tuple[str, Any, Any, Any, Any, Optional[str]]


def prepare_time_plot_data(
    fn: str,
    dataset: Any,
    input_data: Any,
    title: str,
    args: Mapping[str, Any],
    time_labels: list[str],
) -> TimePlotData:
    """Prepare time values, labels, and filtered input for an HTI plot."""
    time_notation = "Days" if "Days" in dataset.coords else "[UTC]"
    xtick = None
    xticklabels = None
    date = None
    time_values = None
    plot_input = input_data

    if time_notation == "Days":
        xtick = np.arange(24, input_data.shape[0] + 24, 24)
        xticklabels = np.arange(1, len(xtick) + 1)
        time_values = dataset["time"].values
    elif "Nan_Data" in title:
        time_values = _clock_strings(dataset["time"].values)
    elif "W" in title:
        ze = dataset["Ze"]
        time_values = dataset["time"].values
        date = fn[-26:-18]
        if "nan_data" not in args:
            valid = ~np.isnan(ze).all(axis=1)
            plot_input = input_data[valid, :]
            time_values = time_values[valid]
        time_values = _clock_strings(time_values)
    elif "Ka" in title:
        time_values = _clock_strings(dataset["time"].values)
        date = fn[-23:-15]
    elif "X" in title:
        time_values = _clock_strings(dataset["time"].values)
        date = fn[-22:-14]
    elif "mrr" in title:
        time_values = dataset["time"].values
        date = fn[-21:-13]
    elif "ceilometer" in title:
        time_values = dataset["time"].values
        date = fn[-28:-20]

    if args.get("met_schau"):
        indices = [np.where(time_values == value)[0][0] for value in time_labels[::2]]
        indices.append(len(time_values))
        xtick = indices
        xticklabels = [value[:2] for value in time_labels[::2]] + ["24"]
    else:
        indices = [np.where(time_values == value)[0][0] for value in time_labels]
        xtick = indices
        xticklabels = [value[:2] for value in time_labels]

    return time_notation, plot_input, time_values, xtick, xticklabels, date


def _clock_strings(values: Any) -> np.ndarray:
    return np.asarray([value.astype(str)[11:16] for value in values])
