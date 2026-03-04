"""ODE functionalities."""

from __future__ import annotations

import pandas as pd

from ._matuszynska2016 import get_matuszynska_2016

__all__ = [
    "calc_pam_vals2",
    "get_matuszynska_2016",
]


def calc_pam_vals2(
    fluo_result: pd.Series,
    protocol: pd.DataFrame,
    pfd_str: str,
    sat_pulse: float = 2000,
    *,
    do_relative: bool = False,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate PAM values from fluorescence data.

    Use the fluorescence data from a PAM protocol to calculate Fm, NPQ. To find the Fm values, the protocol used for simulation is seperated into ranges between each saturating pulse. Then the maximum fluorescence value within each range is taken as Fm. Thes are then used to calculate NPQ.

    Args:
        fluo_result (pd.Series): Fluorescence data as a pd.Series from mxlpy simulation.
        protocol (pd.DataFrame): PAM protocol used for simulation. Created using make_protocol from mxlpy.
        pfd_str (str): The name of the PPFD parameter in the protocol.
        sat_pulse (float, optional): The threshold for saturating pulse in the protocol. Defaults to 2000.
        do_relative: whether to return F and FM relative to FM

    Returns:
        tuple[pd.Series, pd.Series]: Fm and NPQ as pd.Series

    """
    F = fluo_result.copy()
    F.name = "Fluorescence"

    peaks = protocol[protocol[pfd_str] >= sat_pulse].copy()
    peaks.index = peaks.index.total_seconds()  # type: ignore
    peaks = peaks.reset_index()

    Fm = {"start": [], "end": [], "time": [], "value": []}

    for idx, (time, _) in peaks.iterrows():
        if idx == 0:
            start_time = 0
        else:
            start_time = time - (time - peaks["Timedelta"].iloc[idx - 1]) / 2  # type: ignore

        if idx == len(peaks) - 1:
            end_time = fluo_result.index[-1]
        else:
            end_time = time + (peaks["Timedelta"].iloc[idx + 1] - time) / 2  # type: ignore

        Fm["start"].append(start_time)
        Fm["end"].append(end_time)
        Fm_slice = fluo_result.loc[start_time:end_time]
        Fm["time"].append(Fm_slice.idxmax())
        Fm["value"].append(Fm_slice.max())

    Fm = pd.DataFrame(Fm).set_index("time")
    Fm = Fm["value"]
    Fm.name = "Flourescence Peaks (Fm)"

    if do_relative:
        F = F / Fm.iloc[0]
        Fm = Fm / Fm.iloc[0]

    # Calculate NPQ
    NPQ = (Fm.iloc[0] - Fm) / Fm if len(Fm) > 0 else pd.Series(dtype=float)
    NPQ.name = "Non-Photochemical Quenching (NPQ)"

    return F, Fm, NPQ
