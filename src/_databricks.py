"""Helper functions for direct interaction with databricks."""

from typing import TYPE_CHECKING, NoReturn

__all__ = ["load_ambit", "load_multispeq"]

if TYPE_CHECKING:
    import pandas as pd


def load_multispeq() -> pd.DataFrame:
    """Load multispeq data from databricks."""
    raise NotImplementedError


def load_ambit() -> NoReturn:
    """Load ambit data from databricks."""
    raise NotImplementedError
