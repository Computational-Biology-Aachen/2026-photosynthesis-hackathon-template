"""Common routines for data analyses."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd

from src import _databricks, plot
from src._heritability import (
    heritability,
    heritability_elastic_net,
    heritability_with_covariates,
)

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "_databricks",
    "heritability",
    "heritability_elastic_net",
    "heritability_with_covariates",
    "plot",
]


def _drop_into_df(df: pd.DataFrame, column: str) -> pd.DataFrame:
    new = pd.DataFrame({k: np.array(v) for k, v in df[column].items()}).T
    df.drop(columns=[column], inplace=True)  # noqa: PD002
    return new


def drop_na_multiple[*Ts](*containers: *Ts) -> tuple[*Ts]:
    """Drop rows of multiple pandas containers if one of the entries is N/A."""
    mask = np.logical_and.reduce(
        [
            c.notna()
            if isinstance(c, pd.Series)
            else cast(pd.DataFrame, c).notna().all(axis=1)
            for c in containers
        ]
    )
    return tuple(cast(pd.Series, c)[mask] for c in containers)


def load_jii_ambit(
    data: Path,
    *,
    load_local: bool = True,
) -> pd.DataFrame:
    """Load the multispeq data provided by the JII."""
    return (
        pd.read_csv(data / "jii-ambit.csv", index_col=0)
        if load_local
        else _databricks.load_ambit()
    )


def load_jii_multispeq(
    data: Path,
    *,
    load_local: bool = True,
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
    main = (
        pd.read_json(
            data / "jii-multispeq.json",
            dtype={"measurement_time": float},
        )
        if load_local
        else _databricks.load_multispeq()
    )

    main = main.drop(
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


def load_iita_cowpea(
    data: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the cowpea data provided by the IITA."""
    # MetaData explains variables of the other two sheets
    desc = pd.read_excel(data / "iita-cowpea.xlsx", sheet_name="MetaData")

    # Sheet 1 contains MultiseQ data
    s1 = pd.read_excel(data / "iita-cowpea.xlsx", sheet_name="Sheet 1")

    # Format str(G1-G112) as int(1-112)
    s1["GEN"] = s1["GEN"].str.slice(1).astype(int)
    s1 = s1.drop(columns=["S/N"])

    # Sheet 2 contains genomic information
    s2 = pd.read_excel(data / "iita-cowpea.xlsx", sheet_name="Sheet 2")

    return desc, s1, s2
