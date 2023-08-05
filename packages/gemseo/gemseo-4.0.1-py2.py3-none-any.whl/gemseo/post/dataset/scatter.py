# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Contributors:
#    INITIAL AUTHORS - initial API and implementation and/or initial
#                           documentation
#        :author: Matthias De Lozzo
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
r"""Draw a scatter plot from a :class:`.Dataset`.

A :class:`.Scatter` plot represents a set of points
:math:`\{x_i,y_i\}_{1\leq i \leq n}` as markers on a classical plot
where the color of points can be heterogeneous.
"""
from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from gemseo.core.dataset import Dataset
from gemseo.post.dataset.dataset_plot import DatasetPlot


class Scatter(DatasetPlot):
    """Plot curve y versus x."""

    def __init__(
        self,
        dataset: Dataset,
        x: str,
        y: str,
        x_comp: str = 0,
        y_comp: str = 0,
    ) -> None:
        """
        Args:
            x: The name of the variable on the x-axis.
            y: The name of the variable on the y-axis.
            x_comp: The component of x.
            y_comp: The component of y.
        """
        super().__init__(dataset, x=x, y=y, x_comp=x_comp, y_comp=y_comp)

    def _plot(
        self,
        fig: None | Figure = None,
        axes: None | Axes = None,
    ) -> list[Figure]:
        x = self._param.x
        y = self._param.y
        x_comp = self._param.x_comp
        y_comp = self._param.y_comp
        color = self.color or "blue"
        x_data = self.dataset[x][:, x_comp]
        y_data = self.dataset[y][:, y_comp]

        fig, axes = self._get_figure_and_axes(fig, axes)
        axes.scatter(x_data, y_data, color=color)

        if self.dataset.sizes[x] == 1:
            axes.set_xlabel(self.xlabel or x)
        else:
            axes.set_xlabel(self.xlabel or f"{x}({x_comp})")

        if self.dataset.sizes[y] == 1:
            axes.set_ylabel(self.ylabel or y)
        else:
            axes.set_ylabel(self.ylabel or f"{y}({y_comp})")

        axes.set_title(self.title)

        return [fig]
