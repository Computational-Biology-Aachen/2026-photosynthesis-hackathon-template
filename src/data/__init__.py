"""Convenience routines to load all data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

try:
    from pyspark.sql.connect.session import SparkSession

    _IN_DATABRICKS = SparkSession.getActiveSession() is not None
except Exception:
    _IN_DATABRICKS = False


def _load(data: Path, table: str) -> pd.DataFrame:
    if _IN_DATABRICKS:
        from src.data import _databricks

        return _databricks.load(table)
    return pd.read_parquet(data / f"{table}.parquet")


def load_grebbedijk(data: Path) -> pd.DataFrame:
    return _load(data, "grebbedijk_measurements")


def load_bean_gart(data: Path) -> pd.DataFrame:
    return _load(data, "bean_gart_35462_35509")


def load_barley_qtl(data: Path) -> pd.DataFrame:
    return _load(data, "barley_qtl_32593_32742")


def load_aardaker(data: Path) -> pd.DataFrame:
    return _load(data, "aardaker_nergena_29273")


def load_potato_ambit() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not _IN_DATABRICKS:
        msg = "Potato ambit data is not available offline"
        raise FileNotFoundError(msg)
    from src.data import _databricks

    return _databricks.load_potato_ambit()


def load_barley_imagic(data: Path) -> pd.DataFrame:
    return _load(data, "barley_imagic_17237_18685")


def load_barley_hvdrr(data: Path) -> pd.DataFrame:
    return _load(data, "barley_hvdrr_12922_16934")


def load_cowpea_iita(data: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        _load(data, "cowpea_iita_measurements"),
        _load(data, "cowpea_iita_snp"),
    )
