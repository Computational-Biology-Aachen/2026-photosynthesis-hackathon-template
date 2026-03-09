"""Common routines for data analyses."""

from __future__ import annotations

from typing import Any, cast

import numpy as np
import pandas as pd

from src import data, plot, protocol
from src._heritability import (
    heritability,
    heritability_elastic_net,
    heritability_with_covariates,
)
from src.data import in_databricks, load_table

__all__ = [
    "data",
    "heritability",
    "heritability_elastic_net",
    "heritability_with_covariates",
    "in_databricks",
    "load_table",
    "plot",
    "protocol",
]


def drop_na_multiple(*containers: Any) -> tuple[Any, ...]:
    """Drop rows of multiple pandas containers if one of the entries is N/A."""
    mask = np.logical_and.reduce(
        np.array(
            [
                (
                    c.notna()
                    if isinstance(c, pd.Series)
                    else cast(pd.DataFrame, c).notna().all(axis=1)
                )
                for c in containers
            ]
        )
    )
    return tuple(cast(pd.Series, c)[mask] for c in containers)
