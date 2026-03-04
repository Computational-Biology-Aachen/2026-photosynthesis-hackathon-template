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

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import numpy as np
import pandas as pd
from sklearn.feature_selection import f_oneway
from sklearn.linear_model import ElasticNet, LinearRegression

from src.plot import FigAxs, fig_axs

__all__ = [
    "Heritabilities",
    "Heritability",
    "heritability",
    "heritability_elastic_net",
    "heritability_with_covariates",
]

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class Heritability:
    """Result container for heritability analyses."""

    heritability: float
    heritability_adj: float
    genetic_variance: float
    environmental_variance: float
    residual_variance: float
    f_statistics: float
    p_value: float
    ss_between: float
    ss_within: float
    ss_env: float


def _nan_or_else(value: float, default: float) -> float:
    if math.isnan(value):
        return default
    return value


@dataclass
class Heritabilities:
    """Result container for heritability analyses."""

    _raw: dict[str, Heritability]

    def as_frame(self) -> pd.DataFrame:
        """Return as pandas.DataFrame."""
        return pd.DataFrame(
            {
                param: {
                    "H2": _nan_or_else(res.heritability_adj, res.heritability),
                    "F_stat": res.f_statistics,
                    "p_value": res.p_value,
                }
                for param, res in self._raw.items()
            }
        ).T.sort_values("H2")

    def as_debug_frame(self) -> pd.DataFrame:
        """Return as pandas.DataFrame with additional debug info."""
        return pd.DataFrame(
            {
                param: {
                    "H2": res.heritability,
                    "H2_adj": res.heritability_adj,
                    "ss_between": res.ss_between,
                    "ss_within": res.ss_within,
                    "ss_env": res.ss_env,
                    "genetic_variance": res.genetic_variance,
                    "environmental_variance": res.environmental_variance,
                    "residual_variance": res.residual_variance,
                    "F_stat": res.f_statistics,
                    "p_value": res.p_value,
                }
                for param, res in self._raw.items()
            }
        ).T.sort_values("H2")

    def plot(self) -> FigAxs:
        """Plot the results."""
        frame = self.as_frame()

        fig, axs = fig_axs(ncols=3, figsize=(8, 3))
        for ax, (name, s) in zip(
            axs, frame.loc[:, ["H2", "F_stat", "p_value"]].items(), strict=True
        ):
            s.plot(title=cast(str, name), ax=ax, kind="bar")
        return fig, axs


def _splitby(s: pd.Series, cond: pd.Series) -> Iterable[np.ndarray]:
    return [s[v].to_numpy().reshape(-1, 1) for v in s.groupby(cond).groups.values()]


def _heritability(var_gen: float, var_total: float) -> float:
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
    n_gtypes = len(gtype.unique())

    for name, variable in data.items():
        # Overall mean
        grand_mean = variable.mean()

        # Between-genotype variance (genetic variance)
        genotype_means = variable.groupby(gtype).mean()
        genotype_sizes = variable.groupby(gtype).size()
        ss_between: float = np.sum(genotype_sizes * (genotype_means - grand_mean) ** 2)
        ms_between: float = ss_between / (n_gtypes - 1)

        # Within-genotype variance (environmental variance)
        ss_within = variable.groupby(gtype).aggregate(
            lambda x: np.sum(np.square(x - x.mean()))
        )
        # FIXME: in _with_covariates, the -1 is missing. Why?
        ms_within: float = ss_within.sum() / (len(variable) - n_gtypes - 1)

        # Genetic variance
        n_harmonic: float = n_gtypes / np.sum(1.0 / genotype_sizes)
        sigma2_genetic = max(0, (ms_between - ms_within) / n_harmonic)
        sigma2_environmental = ms_within

        # Additional info
        f_stat, p_value = f_oneway(*_splitby(variable, gtype))
        f_stat = float(f_stat[0])  # type: ignore
        p_value = float(p_value[0])  # type: ignore
        total_var = sigma2_genetic + sigma2_environmental

        # Store results
        heritability_results[name] = Heritability(
            heritability=_heritability(
                sigma2_genetic,
                total_var,
            ),
            heritability_adj=np.nan,
            genetic_variance=sigma2_genetic,
            environmental_variance=sigma2_environmental,
            residual_variance=np.nan,
            f_statistics=f_stat,
            p_value=p_value,
            ss_within=ss_within.sum(),
            ss_between=ss_between,
            ss_env=np.nan,
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
    n_gtypes = len(gtype.unique())

    for name, variable in data.items():
        var_pred = LinearRegression().fit(env_factors, variable).predict(env_factors)
        res_env = variable - var_pred

        # Between-genotype variance (genetic variance) via residuals
        grand_mean_residuals = res_env.mean()
        genotype_means = res_env.groupby(gtype).mean()
        genotype_sizes = res_env.groupby(gtype).size()
        ss_between = np.sum(
            genotype_sizes * (genotype_means - grand_mean_residuals) ** 2
        )
        ms_between = ss_between / (n_gtypes - 1)

        # Within-genotype variance
        ss_within = res_env.groupby(gtype).aggregate(
            lambda x: np.sum(np.square(x - x.mean()))
        )
        # FIXME: why not -1 here?
        ms_within: float = ss_within.sum() / (len(variable) - n_gtypes)

        # Genetic variance
        n_harmonic: float = n_gtypes / np.sum(1.0 / genotype_sizes)
        sigma2_genetic = max(0, (ms_between - ms_within) / n_harmonic)
        sigma2_residual = ms_within

        # Additional info
        f_stat, p_value = f_oneway(*_splitby(res_env, gtype))
        f_stat = float(f_stat[0])  # type: ignore
        p_value = float(p_value[0])  # type: ignore

        ss_env = ((var_pred - variable.mean()) ** 2).sum()
        sigma2_environmental = ss_env / (len(variable) - len(env_factors.columns) - 1)
        total_var = sigma2_genetic + sigma2_environmental + sigma2_residual
        total_var_adj = sigma2_genetic + sigma2_residual

        # Store results
        heritability_results[name] = Heritability(
            heritability=_heritability(
                sigma2_genetic,
                total_var,
            ),
            heritability_adj=_heritability(
                sigma2_genetic,
                total_var_adj,
            ),
            genetic_variance=sigma2_genetic,
            environmental_variance=sigma2_environmental,
            residual_variance=sigma2_residual,
            f_statistics=f_stat,
            p_value=p_value,
            ss_within=ss_within.sum(),
            ss_between=ss_between,
            ss_env=ss_env,
        )

    return Heritabilities(heritability_results)


def heritability_elastic_net(
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
    n_gtypes = len(gtype.unique())

    for name, variable in data.items():
        var_pred = ElasticNet().fit(env_factors, variable).predict(env_factors)
        res_env = variable - var_pred

        # Between-genotype variance (genetic variance) via residuals
        grand_mean_residuals = res_env.mean()
        genotype_means = res_env.groupby(gtype).mean()
        genotype_sizes = res_env.groupby(gtype).size()
        ss_between = np.sum(
            genotype_sizes * (genotype_means - grand_mean_residuals) ** 2
        )
        ms_between = ss_between / (n_gtypes - 1)

        # Within-genotype variance
        ss_within = res_env.groupby(gtype).aggregate(
            lambda x: np.sum(np.square(x - x.mean()))
        )
        # FIXME: why not -1 here?
        ms_within: float = ss_within.sum() / (len(variable) - n_gtypes)

        # Genetic variance
        n_harmonic: float = n_gtypes / np.sum(1.0 / genotype_sizes)
        sigma2_genetic = max(0, (ms_between - ms_within) / n_harmonic)
        sigma2_residual = ms_within

        # Additional info
        f_stat, p_value = f_oneway(*_splitby(res_env, gtype))
        f_stat = float(f_stat[0])  # type: ignore
        p_value = float(p_value[0])  # type: ignore

        ss_env = ((var_pred - variable.mean()) ** 2).sum()
        sigma2_environmental = ss_env / (len(variable) - len(env_factors.columns) - 1)
        total_var = sigma2_genetic + sigma2_environmental + sigma2_residual
        total_var_adj = sigma2_genetic + sigma2_residual

        # Store results
        heritability_results[name] = Heritability(
            heritability=_heritability(
                sigma2_genetic,
                total_var,
            ),
            heritability_adj=_heritability(
                sigma2_genetic,
                total_var_adj,
            ),
            genetic_variance=sigma2_genetic,
            environmental_variance=sigma2_environmental,
            residual_variance=sigma2_residual,
            f_statistics=f_stat,
            p_value=p_value,
            ss_within=ss_within.sum(),
            ss_between=ss_between,
            ss_env=ss_env,
        )

    return Heritabilities(heritability_results)
