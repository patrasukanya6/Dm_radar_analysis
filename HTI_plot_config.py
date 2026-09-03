"""Visualization defaults for the HTI quicklook plots.

Keep plot-specific presentation choices here so the plotting routine can focus
on preparing data and arranging the figure.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class PlotConfig:
    """Colormap and color scale used for one plotted variable."""

    output_path: str = "/home"
    colormap: str = "turbo"
    vmin: float = -50
    vmax: float = 30
    colorbar_label: str = ""


_DEFAULT_RANGES = {
    "SW": (0, 1),
    "WIDTH": (0, 1),
    "RMS": (0, 1),
    "RMSg": (0, 1),
    "sRMSg": (0, 1),
    "LDR": (-35, -5),
    "sLDR": (-35, -5),
    "sLDR_w": (-35, -5),
    "LDRg": (-35, -5),
    "DLDR": (-35, -5),
    "MDV": (-5, 3),
    "VEL": (-8, 3),
    "VELg": (-8, 3),
    "sVELg": (-8, 3),
    "V": (-6, 2),
    "LWC": (0, 1),
    "RR": (0, 20),
    "SKWg": (-1, 1),
    "SK": (-1, 1),
    "Sk": (-1, 1),
    "rc_signal": (-7, -4),
    "ZDR": (-1, 4),
    "KDP": (-1, 4),
    "RHV": (0.85, 1),
    "sZDRmax": (-1, 4),
    "Dm": (0, 2),
}

_LABELS = {
    "Ze": "Z$_e$(dBZ$_e$)",
    "Zg": "Z$_e$(dBZ$_e$)",
    "Z": "Z$_e$(dBZ$_e$)",
    "sZg": "Z$_e$(dBZ$_e$)",
    "SW": "SW (m$^{-1}$)",
    "WIDTH": "SW (m$^{-1}$)",
    "RMS": "SW (m$^{-1}$)",
    "RMSg": "SW (m$^{-1}$)",
    "sRMSg": "SW (m$^{-1}$)",
    "V": "Vel(ms$^{-1}$)",
    "MDV": "Vel(ms$^{-1}$)",
    "VEL": "Vel(ms$^{-1}$)",
    "VELg": "Vel(ms$^{-1}$)",
    "sVELg": "Vel(ms$^{-1}$)",
    "LDR": "slanted LDR(dB)",
    "LDRg": "slanted LDR(dB)",
    "sLDR": "slanted LDR(dB)",
    "RR": "Rain Rate (mm h$^{-1}$)",
    "LWC": "LWC (gm m$^{-3}$)",
    "SKWg": "Skewness",
    "SK": "Skewness",
    "Sk": "Skewness",
    "rc_signal": "log(rc_signal) @1064 nm",
    "ZDR": "ZDR(dB)",
    "KDP": "KDP(°km$^{-1}$)",
    "RHV": "RhoHV",
    "sZDRmax": "sZDR$_m$$_a$$_x$(dB)",
    "Dm": "Dm (mm)",
}


def _derived_scale(variable_name: str) -> Optional[Tuple[float, float]]:
    if variable_name.startswith("DWR"):
        return -5, 10
    if variable_name.startswith(("DDV", "DSW")):
        return -0.3, 0.3
    if variable_name.startswith("DSK"):
        return -1, 1
    if variable_name.startswith("DLDR"):
        return -35, -5
    return _DEFAULT_RANGES.get(variable_name)


def _derived_label(variable_name: str) -> str:
    if variable_name == "DLDR_35_94":
        return "DLDR$_3$$_5$$_-$$_9$$_4$(dB)"

    unit = ""
    if variable_name.startswith("DWR"):
        unit = "(dB)"
    elif variable_name.startswith(("DDV", "DSW")):
        unit = "(ms$^{-1}$)"

    for suffix, formatted_suffix in (
        ("_35_94", "$_3$$_5$$_-$$_9$$_4$"),
        ("_10_35", "$_1$$_0$$_-$$_3$$_5$"),
        ("_10_94", "$_1$$_0$$_-$$_9$$_4$"),
    ):
        if variable_name.endswith(suffix):
            return f"{variable_name[:-6]}{formatted_suffix}{unit}"

    return _LABELS.get(variable_name, variable_name)


def get_plot_config(
    variable_name: str,
    title: str = "",
    overrides: Optional[Mapping[str, Any]] = None,
) -> PlotConfig:
    """Return defaults merged with optional per-call plotting overrides."""
    overrides = overrides or {}
    scale = _derived_scale(variable_name) or (-50, 30)
    if variable_name == "Ze" and "mrr" in title:
        scale = (-20, 60)
    elif variable_name == "Ze" and "W" in title:
        scale = (-50, 30) if overrides.get("diff_radar") else (-50, 20)
    vmin = overrides.get("vmin", overrides.get("Vmin", scale[0]))
    vmax = overrides.get("vmax", overrides.get("Vmax", scale[1]))
    return PlotConfig(
        output_path=overrides.get("pathOutputPlots", "/home"),
        colormap=overrides.get("colormap", "turbo"),
        vmin=vmin,
        vmax=vmax,
        colorbar_label=overrides.get(
            "colorbarLabel",
            overrides.get("ColorbarLabel", _derived_label(variable_name)),
        ),
    )
