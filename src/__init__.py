"""Common routines for data analyses."""

from typing import TYPE_CHECKING, NoReturn, cast

import numpy as np
import pandas as pd

from src import databricks, plot
from src.heritability import heritability, heritability_with_covariates

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "databricks",
    "heritability",
    "heritability_with_covariates",
    "plot",
]


def _drop_into_df(df: pd.DataFrame, column: str) -> pd.DataFrame:
    new = pd.DataFrame({k: np.array(v) for k, v in df[column].items()}).T
    df.drop(columns=[column], inplace=True)  # noqa: PD002
    return new


def drop_na_multiple[*Ts](*containers: *Ts) -> tuple[*Ts]:
    mask = np.logical_and.reduce(
        [
            c.notna()
            if isinstance(c, pd.Series)
            else cast(pd.DataFrame, c).notna().all(axis=1)
            for c in containers
        ]
    )
    return tuple(cast(pd.Series, c)[mask] for c in containers)


def load_jii_ambit(data: Path) -> NoReturn:
    """Load the multispeq data provided by the JII."""
    raise NotImplementedError


def load_jii_multispeq(
    data: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load the multispeq data provided by the JII."""
    main = pd.read_json(
        data / "multispeq.json", dtype={"measurement_time": float}
    ).drop(
        columns=[
            "project_id",
            "user_id",
            "measurement_time_parsed",
            "status",
            "notes",
            "autogain",
            "settings",
            "order",
            "ri",
            "v_arrays",
        ]
    )
    main["measurement_time"] = pd.to_datetime(main["measurement_time"], unit="ms")

    a820_fr = _drop_into_df(main, "A820_FR_0")
    abs820_ambient = _drop_into_df(main, "abs820_ambient")
    abs820_high = _drop_into_df(main, "abs820_high")
    pirk_ambient = _drop_into_df(main, "PIRK_ambient")
    pirk_high = _drop_into_df(main, "PIRK_high")
    fluo_ambient = _drop_into_df(main, "fluo_ambient")
    fluo_high = _drop_into_df(main, "fluo_high")
    fluor_fr_0 = _drop_into_df(main, "fluor_FR_0")

    return (
        main,
        a820_fr,
        abs820_ambient,
        abs820_high,
        pirk_ambient,
        pirk_high,
        fluo_ambient,
        fluo_high,
        fluor_fr_0,
    )


def load_iita_cowpea(data: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the cowpea data provided by the IITA."""
    # MetaData explains variables of the other two sheets
    desc = pd.read_excel(data / "cowpea-sansa.xlsx", sheet_name="MetaData")

    # Sheet 1 contains MultiseQ data
    s1 = pd.read_excel(data / "cowpea-sansa.xlsx", sheet_name="Sheet 1")

    # Format str(G1-G112) as int(1-112)
    s1["GEN"] = s1["GEN"].str.slice(1).astype(int)

    # Sheet 2 contains genomic information
    s2 = pd.read_excel(data / "cowpea-sansa.xlsx", sheet_name="Sheet 2")

    return desc, s1, s2
