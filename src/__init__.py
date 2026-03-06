"""Common routines for data analyses."""

from __future__ import annotations

from typing import Any, cast

import numpy as np
import pandas as pd

from src import data, plot
from src._heritability import (
    heritability,
    heritability_elastic_net,
    heritability_with_covariates,
)

__all__ = [
    "data",
    "heritability",
    "heritability_elastic_net",
    "heritability_with_covariates",
    "plot",
]


def drop_na_multiple(*containers: Any) -> tuple[Any, ...]:
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
