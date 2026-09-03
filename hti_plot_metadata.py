"""Titles, labels, annotations, and filenames for HTI plots."""

from typing import Any, Mapping, Optional

import calendar


def configure_plot_metadata(
    ax: Any,
    fn: str,
    title: str,
    input_data: Any,
    date: Optional[str],
    time_notation: str,
    args: Mapping[str, Any],
    row: Optional[int],
    subplot_pos: Optional[int],
    xlabels: Any,
    sunrise_indices: Any,
    sunset_indices: Any,
    radar_title: Optional[str] = None,
) -> Optional[str]:
    """Apply plot labels/titles and return the output filename."""
    input_name = input_data.name
    date_text = "" if date is None else str(date)
    sunrise = sunrise_indices[0] if len(sunrise_indices) else []
    sunset = sunset_indices[0] if len(sunset_indices) else []

    if row is not None and subplot_pos == row:
        ax.set_xticklabels(xlabels)
        ax.xaxis.set_tick_params(labelleft=True, labelsize=15)
        if sunrise:
            if "mrr" in title or row == 2 or "offset_corrected_zoom" in args:
                ax.text(sunrise[0], -0.5, "sunrise", fontsize=15, ha="center")
            else:
                ax.text(sunrise[0] - 200, -2.9, "sunrise", fontsize=15)
        if sunset:
            if "mrr" in title or row == 2 or "offset_corrected_zoom" in args:
                ax.text(sunset[0], -0.5, "sunset", fontsize=15, ha="center")
            else:
                ax.text(sunset[0] - 200, -2.9, "sunset", fontsize=15)
        ax.set_xlabel(f"Time{time_notation}", fontsize=18)
        filename = _build_filename(fn, title, input_name, date_text, time_notation, args)
    else:
        ax.set_xticklabels(xlabels)
        ax.xaxis.set_tick_params(labelleft=False)
        filename = _build_filename(fn, title, input_name, date_text, time_notation, args)

        if args.get("met_schau"):
            if sunrise:
                ax.text(sunrise[0] - 100, -0.99, "sunrise", fontsize=38)
            if sunset:
                ax.text(sunset[0] - 100, -0.99, "sunset", fontsize=38)

        if radar_title:
            ax.set_title(radar_title, fontsize=18)
        _set_comparison_title(ax, title, input_name)

    if subplot_pos == 1 or (subplot_pos is None and args.get("met_schau")):
        if args.get("met_schau"):
            ax.set_xlabel(f"Time{time_notation}", fontsize=38)
        if input_name == "Dm":
            ax.set_ylim(0.5, 4)
            ax.set_title(f"Mean mass-weighted equivolume diameter on {date_text}", fontsize=18)
            ax.set_ylabel(
                "Height above ground (km)",
                fontsize=38 if args.get("met_schau") else 15,
            )
        elif args.get("met_schau"):
            ax.set_ylabel("Height above ground (km)", fontsize=38)
        else:
            ax.set_ylabel("Height above ground (km)", fontsize=18)

        if radar_title:
            ax.set_title(f"{radar_title} on {date_text}", fontsize=18)

        _set_special_title(ax, title, input_name, date_text, time_notation)

    return filename


def _set_comparison_title(ax: Any, title: str, input_name: str) -> None:
    comparison_titles = {
        "10_35": "xmacs-kamacs",
        "35_94": "kamacs-wmacs",
        "10_94": "xmacs-wmacs",
    }
    for suffix, comparison in comparison_titles.items():
        if input_name.endswith(suffix):
            ax.set_title(comparison, fontsize=18)


def _build_filename(
    fn: str,
    title: str,
    input_name: str,
    date: str,
    time_notation: str,
    args: Mapping[str, Any],
) -> str:
    if args.get("diff_radar"):
        return f"X_Ka_wmacs_{input_name}_{date}.png"
    if "mrr" in title:
        return f"MRR_variables_{date}.png"
    if "X" in title:
        return f"xmacs_HTI_Z_V_SW_LDR_{date}.png"
    if "Ka" in title:
        if time_notation == "Days":
            return f"kamacs_Moments_{date}.png"
        return f"kamacs_HTI_Z_V_SW_LDR_{date}.png"
    if input_name in {"ZDR", "ZDRmax", "KDP", "RHV"}:
        return f"wmacs_HTI_ZDR_KDP_sZDRmax_RhoHV_{date}.png"
    if "ZEN" in title and "W" in title:
        return f"wmacs_HTI_Z_V_SW_LDR_{date}.png"
    if "ceilometer" in title:
        return f"Ceilometer_RC_Signal_{fn[-28:-20]}.png"
    if input_name in {"sZg", "sRMSg", "sVELg", "sLDR_w"} and "CEL" in title:
        return f"wmacs_slanted_HTI_Z_V_SW_LDR_{date}.png"
    if input_name.endswith(("10_35", "35_94", "10_94")):
        return f"{date}_{input_name.split('_')[0]}.png"
    return f"{input_name}_{date}.png"


def _set_special_title(
    ax: Any,
    title: str,
    input_name: str,
    date: str,
    time_notation: str,
) -> None:
    if input_name in {"ZDR", "ZDRmax", "KDP", "RHV"}:
        ax.set_title(f"wmacs Polarimetric Moments on {date}", fontsize=18)
    elif input_name in {"Ze", "MDV", "WIDTH", "sLDR"} and "ZEN" in title:
        ax.set_title(f"wmacs Moments on {date}", fontsize=18)
    elif input_name in {"sZg", "sRMSg", "sVELg", "sLDR_w"} and "CEL" in title:
        ax.set_title(f"wmacs (slanted) Moments on {date}", fontsize=18)
    elif "Ka" in title and input_name != "Dm":
        if time_notation == "Days":
            month = calendar.month_name[int(title[-6:-4])]
            ax.set_title(f"{title[:-7]}{month} {title[-4:]}", fontsize=18)
        else:
            ax.set_title(f"kamacs Moments on {date}", fontsize=18)
    elif "X" in title and input_name != "Dm":
        ax.set_title(f"xmacs Moments on {date}", fontsize=18)
    elif "mrr" in title:
        ax.set_title(f"MRR variables on {date}", fontsize=18)

    comparison_titles = {
        "10_35": "xmacs-kamacs",
        "35_94": "kamacs-wmacs",
        "10_94": "xmacs-wmacs",
    }
    for suffix, comparison in comparison_titles.items():
        if input_name.endswith(suffix):
            ax.set_title(f"{date} {comparison}", fontsize=18)
