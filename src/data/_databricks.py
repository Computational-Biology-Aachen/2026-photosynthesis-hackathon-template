"""Helper functions for direct interaction with databricks."""

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, cast

from pyspark.sql import functions as F  # noqa: N812
from pyspark.sql.connect.session import SparkSession

__all__ = ["VOLUME_PATH", "load_ambit", "load_cowpea_iita", "load_multispeq"]

if TYPE_CHECKING:
    import pandas as pd

VOLUME_PATH = "/Volumes/open_jii_data_hackathon/default/hackathon_data_volume/v2_data"

spark = cast(SparkSession, SparkSession.getActiveSession())


def load_multispeq() -> pd.DataFrame:
    """Load multispeq data from databricks."""
    raise NotImplementedError


def load_ambit() -> NoReturn:
    """Load ambit data from databricks."""
    raise NotImplementedError


def _cowpea_iita_multispeq(*, add_metadata: bool = False) -> pd.DataFrame:
    pdf = spark.read.parquet(f"{VOLUME_PATH}/cowpea_iita_measurements.parquet")

    if add_metadata:
        pdf = (
            pdf.withColumn(
                "project_description",
                F.lit("IITA cowpea drought stress trial Nigeria 2020-2022"),
            )
            .withColumn("crop", F.lit("Cowpea"))
            .withColumn("data_source", F.lit("MultispeQ"))
        )

    multispeq = pdf.toPandas().set_index("row_number", drop=True)
    multispeq.index.name = None
    return multispeq


def _cowpea_iita_snp() -> pd.DataFrame:
    snp = spark.read.parquet(f"{VOLUME_PATH}/cowpea_iita_snp.parquet")
    return snp.toPandas()


def load_cowpea_iita(
    *, add_metadata: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        _cowpea_iita_multispeq(add_metadata=add_metadata),
        _cowpea_iita_snp(),
    )
