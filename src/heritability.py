"""Functions to calculate heritability.

General heritability formula: H² = σ²_G / (σ²_G + σ²_E)
Where:
- σ²_G = genetic variance (between genotype variance)
- σ²_E = environmental variance (within genotype variance)


Broad-sense heritability (H²) accounting for environmental factors.
Adjusted heritability: H²_adj = σ²_G / (σ²_G + σ²_residual)
Where:
- σ²_G = genetic variance (between genotype variance)
- σ²_residual = Residual variance (unexplained within-genotype variation)

"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd
from sklearn.feature_selection import f_oneway
from sklearn.linear_model import LinearRegression

from src.plot import FigAxs, fig_axs

__all__ = [
    "Heritabilities",
    "Heritability",
    "heritability",
    "heritability_with_covariates",
]

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class Heritability:
    """Result container for heritability analyses."""

    heritability: float
    f_statistics: float
    p_value: float


@dataclass
class Heritabilities:
    """Result container for heritability analyses."""

    _raw: dict[str, Heritability]

    def as_frame(self) -> pd.DataFrame:
        """Return as pandas.DataFrame."""
        return pd.DataFrame(
            {
                param: {
                    "H²": res.heritability,
                    "F_stat": res.f_statistics,
                    "p_value": res.p_value,
                }
                for param, res in self._raw.items()
            }
        ).T.sort_values("H²")

    def plot(self) -> FigAxs:
        """Plot the results."""
        fig, axs = fig_axs(nrows=3, figsize=(8, 3))
        frame = self.as_frame()

        for ax, (name, s) in zip(axs, frame.items(), strict=True):
            s.plot(title=cast(str, name), ax=ax, kind="bar")
        return fig, axs


def _splitby(s: pd.Series, cond: pd.Series) -> Iterable[np.ndarray]:
    return [s[v].to_numpy().reshape(-1, 1) for v in s.groupby(cond).groups.values()]


def _adjusted_heritability(var_gen: float, var_total: float) -> float:
    if var_total > 0.0:
        return var_gen / var_total
    return 0.0


def heritability(
    data: pd.DataFrame,
    gtype: pd.Series,
) -> Heritabilities:
    """Calculate heritability based on variances within and between genotypes.

    Formula: H² = σ²_G / (σ²_G + σ²_E).
    Where:
    - σ²_G = genetic variance (between genotype variance)
    - σ²_E = environmental variance (within genotype variance)
    """
    heritability_results = {}
    valid_genotypes = len(gtype.unique())

    for name, variable in data.items():
        # Overall mean
        grand_mean = variable.mean()

        # Between-genotype variance (genetic variance)
        genotype_means = variable.groupby(gtype).mean()
        genotype_sizes = variable.groupby(gtype).size()
        ms_between: float = np.sum(
            genotype_sizes * (genotype_means - grand_mean) ** 2
        ) / (valid_genotypes - 1)

        # Within-genotype variance (environmental variance)
        ss_within = variable.groupby(gtype).aggregate(
            lambda x: np.sum(np.square(x - x.mean()))
        )
        ms_within = ss_within.sum() / (len(ss_within) - 1)

        # Genetic variance
        n_harmonic: float = valid_genotypes / np.sum(1.0 / genotype_sizes)
        sigma2_genetic = (ms_between - ms_within) / n_harmonic
        sigma2_environmental = ms_within

        # Additional info
        f_stat, p_value = f_oneway(*_splitby(variable, gtype))

        # Store results
        heritability_results[name] = Heritability(
            heritability=_adjusted_heritability(
                sigma2_genetic,
                sigma2_genetic + sigma2_environmental,
            ),
            f_statistics=float(f_stat[0]),  # type: ignore
            p_value=float(p_value[0]),  # type: ignore
        )

    return Heritabilities(heritability_results)


def heritability_with_covariates(
    data: pd.DataFrame,
    env_factors: pd.DataFrame,
    gtype: pd.Series,
) -> Heritabilities:
    """Calculate heritability based on variances within and between genotypes.

    Formula: H² = σ²_G / (σ²_G + σ²_E).
    Where:
    - σ²_G = genetic variance (between genotype variance)
    - σ²_E = environmental variance (within genotype variance)

    """
    heritability_results = {}
    valid_genotypes = len(gtype.unique())

    for name, variable in data.items():
        valid_genotypes = len(gtype.unique())

        var_pred = LinearRegression().fit(env_factors, variable).predict(env_factors)
        res_env = variable - var_pred

        # Between-genotype variance (genetic variance) via residuals
        grand_mean_residuals = variable.mean()
        genotype_means = variable.groupby(gtype).mean()
        genotype_sizes = variable.groupby(gtype).size()
        ss_between = np.sum(
            genotype_sizes * (genotype_means - grand_mean_residuals) ** 2
        )
        df_between = valid_genotypes - 1
        ms_between = ss_between / df_between if df_between > 0 else 0

        # Within-genotype variance
        ss_within = res_env.groupby(gtype).aggregate(
            lambda x: np.sum(np.square(x - x.mean()))
        )
        ms_within = ss_within.sum() / (len(ss_within) - 1)

        # Genetic variance
        n_harmonic: float = valid_genotypes / np.sum(1.0 / genotype_sizes)
        sigma2_genetic = (ms_between - ms_within) / n_harmonic
        sigma2_residual = ms_within

        # Additional info
        f_stat, p_value = f_oneway(*_splitby(res_env, gtype))

        # Store results
        heritability_results[name] = Heritability(
            heritability=_adjusted_heritability(
                sigma2_genetic,
                sigma2_genetic + sigma2_residual,
            ),
            f_statistics=float(f_stat[0]),  # type: ignore
            p_value=float(p_value[0]),  # type: ignore
        )

    return Heritabilities(heritability_results)
