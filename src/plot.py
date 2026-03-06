"""Helper for easy plotting."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Union, cast, overload

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from wadler_lindig import pformat

__all__ = [
    "Axs",
    "Color",
    "FigAx",
    "FigAxs",
    "Linestyle",
    "RGB",
    "RGBA",
    "add_grid",
    "fig_ax",
    "fig_axs",
    "grid_labels",
    "reset_prop_cycle",
    "rotate_xlabels",
]

if TYPE_CHECKING:
    from collections.abc import Iterator

    import numpy as np
    from numpy.typing import NDArray


@dataclass
class Axs:
    """Convenience container  axes."""

    axs: NDArray[np.object_]

    def __iter__(self) -> Iterator[Axes]:
        """Get flat axes."""
        yield from cast(list[Axes], self.axs.flatten())

    def __len__(self) -> int:
        """Length of axes."""
        return len(self.axs.flatten())

    def __repr__(self) -> str:
        """Return default representation."""
        return pformat(self)

    @overload
    def __getitem__(self, row_col: int) -> Axes: ...

    @overload
    def __getitem__(self, row_col: slice) -> NDArray[np.object_]: ...

    @overload
    def __getitem__(self, row_col: tuple[int, int]) -> Axes: ...

    @overload
    def __getitem__(self, row_col: tuple[slice, int]) -> NDArray[np.object_]: ...

    @overload
    def __getitem__(self, row_col: tuple[int, slice]) -> NDArray[np.object_]: ...

    def __getitem__(
        self, row_col: int | slice | tuple[int | slice, int | slice]
    ) -> Axes | NDArray[np.object_]:
        """Get Axes or Array of Axes."""
        return cast(Axes, self.axs[row_col])


FigAx = tuple[Figure, Axes]
FigAxs = tuple[Figure, Axs]

Linestyle = Literal[
    "solid",
    "dotted",
    "dashed",
    "dashdot",
]


RGB = tuple[float, float, float]
RGBA = tuple[float, float, float, float]
Color = Union[str, RGB, RGBA]


def add_grid(ax: Axes) -> Axes:
    """Add a grid to the given axis."""
    ax.grid(visible=True)
    ax.set_axisbelow(b=True)
    return ax


def grid_labels(
    axs: Axs,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> None:
    """Apply labels to left and bottom axes."""
    for ax in axs[-1, :]:
        ax.set_xlabel(xlabel)
    for ax in axs[:, 0]:
        ax.set_ylabel(ylabel)


def rotate_xlabels(
    ax: Axes,
    rotation: float = 45,
    ha: Literal["left", "center", "right"] = "right",
) -> Axes:
    """Rotate the x-axis labels of the given axis.

    Args:
        ax: Axis to rotate the labels of.
        rotation: Rotation angle in degrees (default: 45).
        ha: Horizontal alignment of the labels (default

    Returns:
        Axes object for object chaining

    """
    for label in ax.get_xticklabels():
        label.set_rotation(rotation)
        label.set_horizontalalignment(ha)
    return ax


def reset_prop_cycle(ax: Axes) -> None:
    """Reset the property cycle of the given axis.

    Args:
        ax: Axis to reset the property cycle of.

    """
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])


def fig_ax(
    *,
    ax: Axes | None,
    grid: bool,
    figsize: tuple[float, float] | None = None,
) -> FigAx:
    """Create a figure and axes if none are provided.

    Args:
        ax: Axis to use for the plot.
        grid: Whether to add a grid to the plot.
        figsize: Size of the figure (default: None).

    Returns:
        Figure and Axes objects for the plot.

    """
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
    else:
        fig = cast(Figure, ax.get_figure())

    if grid:
        add_grid(ax)
    return fig, ax


def fig_axs(
    *,
    ncols: int,
    nrows: int = 1,
    figsize: tuple[float, float] | None,
    grid: bool = True,
    sharex: bool = True,
    sharey: bool = False,
) -> FigAxs:
    """Create a figure and multiple axes if none are provided.

    Args:
        axs: Axes to use for the plot.
        ncols: Number of columns for the plot.
        nrows: Number of rows for the plot.
        figsize: Size of the figure (default: None).
        grid: Whether to add a grid to the plot.
        sharex: Whether to share the x-axis between the axes.
        sharey: Whether to share the y-axis between the axes.

    Returns:
        Figure and Axes objects for the plot.

    """
    fig, axs_array = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        sharex=sharex,
        sharey=sharey,
        figsize=figsize,
        squeeze=False,
        layout="constrained",
    )
    axs = Axs(axs_array)

    if grid:
        for ax in axs:
            add_grid(ax)
    return fig, axs
