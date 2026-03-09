"""Helper functions for direct interaction with databricks."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyspark.sql.connect.session import SparkSession

__all__ = [
    "CATALOG",
    "load",
    "load2",
    "load_aardaker",
    "load_barley_hvdrr",
    "load_barley_imagic",
    "load_barley_qtl",
    "load_bean_gart",
    "load_cowpea_iita",
    "load_grebbedijk",
    "load_potato_ambit",
]

if TYPE_CHECKING:
    import pandas as pd

CATALOG = "open_jii_data_hackathon.default"

# NOTE: we ever only call the functions below when we determined this is not None
# before, so for here this cast should be fine
spark = cast(SparkSession, SparkSession.getActiveSession())


def load(table: str) -> pd.DataFrame:
    """Load a table as a pandas DataFrame, excluding the ``sample_raw`` column.

    The ``sample_raw`` column contains the full raw MultispeQ measurement trace
    stored as a VARIANT type, which is not supported by Databricks Connect.
    To work with raw traces, query the table directly via PySpark::

        spark.table("open_jii_data_hackathon.default.grebbedijk_measurements")
    """
    return spark.sql(
        f"SELECT * EXCEPT(sample_raw) FROM {CATALOG}.{table}"  # noqa: S608
    ).toPandas()


def load2(table: str) -> pd.DataFrame:
    """Load a table as a pandas DataFrame, excluding the ``sample_raw`` column.

    The ``sample_raw`` column contains the full raw MultispeQ measurement trace
    stored as a VARIANT type, which is not supported by Databricks Connect.
    To work with raw traces, query the table directly via PySpark::

        spark.table("open_jii_data_hackathon.default.grebbedijk_measurements")
    """
    return spark.sql(
        f"SELECT * FROM {CATALOG}.{table}"  # noqa: S608
    ).toPandas()


def load_grebbedijk() -> pd.DataFrame:
    return load("grebbedijk_measurements")


def load_bean_gart() -> pd.DataFrame:
    return load("bean_gart_35462_35509")


def load_barley_qtl() -> pd.DataFrame:
    return load("barley_qtl_32593_32742")


def load_aardaker() -> pd.DataFrame:
    return load("aardaker_nergena_29273")


def load_potato_ambit() -> tuple[pd.DataFrame, pd.DataFrame]:
    return load2("potato_ambyte_ambit"), load("potato_ambyte_ambit_silver")


def load_barley_imagic() -> pd.DataFrame:
    return load("barley_imagic_17237_18685")


def load_barley_hvdrr() -> pd.DataFrame:
    return load("barley_hvdrr_12922_16934")


def load_cowpea_iita() -> tuple[pd.DataFrame, pd.DataFrame]:
    return load2("cowpea_iita_measurements"), load2("cowpea_iita_snp")
