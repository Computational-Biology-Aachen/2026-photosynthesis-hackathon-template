"""Convenience routines to load all data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pyspark.sql.connect.session import SparkSession

from src.data import _databricks

if TYPE_CHECKING:
    from pathlib import Path

_IN_DATABRICKS = SparkSession.getActiveSession() is not None


def _drop_into_df(df: pd.DataFrame, column: str) -> pd.DataFrame:
    new = pd.DataFrame({k: np.array(v) for k, v in df[column].items()}).T
    df.drop(columns=[column], inplace=True)  # noqa: PD002
    return new


def load_potato_grebbedijk(data: Path) -> pd.DataFrame:
    """Load the multispeq data provided by the JII."""
    return (
        _databricks.load_ambit()
        if _IN_DATABRICKS
        else pd.read_csv(data / "01-potato-grebbedijk.csv", index_col=0)
    )


def load_potato_ambit(
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
    main = (
        _databricks.load_multispeq()
        if _IN_DATABRICKS
        else pd.read_json(
            data / "05-potato-ambit.json",
            dtype={"measurement_time": float},
        )
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


def load_cowpea_iita(data: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the cowpea data provided by the IITA."""
    if _IN_DATABRICKS:
        return _databricks.load_cowpea_iita()

    multispeq = pd.read_csv(data / "08-cowpea-iita-multispeq.csv", index_col=0)
    # Format str(G1-G112) as int(1-112)
    # multispeq["genotype"] = multispeq["genotype"].str.slice(1).astype(int)

    snp = pd.read_csv(data / "08-cowpea-iita-snp.csv", index_col=0)
    return multispeq, snp
