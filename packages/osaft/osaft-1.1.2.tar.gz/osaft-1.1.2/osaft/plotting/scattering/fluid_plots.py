from collections.abc import Callable
from functools import partial
from typing import Optional, Union

import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.cm import ScalarMappable

from osaft.core.functions import pi, sqrt
from osaft.plotting.datacontainers.scattering_datacontainer import (
    FluidScatteringData,
)
from osaft.plotting.scattering.tri_plotter import TriangulationPlotter
from osaft.solutions.base_scattering import BaseScattering

np_arr = np.ndarray


class FluidScatteringPlot:
    """Class for plotting scattering field of the fluid

    Plots the acoustic field inside the particle using Matplotlib
    tricontourf or tripcolor plotting methods.

    :param sol: solution to be plotted
    :param r_max: radial limit of plot range
    :param theta_min: lower limit for tangential plot range
    :param theta_max: upper limit for tangential plot range
    :param resolution: if tuple (radial resolution, tangential resolution)
    :param cmap: color map
    :param div_cmap: diverging color map
    """

    def __init__(
            self,
            sol: BaseScattering,
            r_max: float,
            theta_min: float = 0,
            theta_max: float = pi,
            resolution: Union[int, tuple[int, int]] = 100,
            cmap: str = 'winter',
            div_cmap: str = 'coolwarm',
    ):
        """Constructor method
        """
        self.data = FluidScatteringData(
            sol, sqrt(2) * r_max, theta_min,
            theta_max,
            res=resolution,
        )
        self.plotter = TriangulationPlotter(False, cmap, div_cmap)

    # -------------------------------------------------------------------------
    # Attributes
    # -------------------------------------------------------------------------

    @property
    def cmap(self) -> str:
        """Colormap for plotting

        :getter: return the colormap choice
        :setter: sets the colormap choice
        """
        return self.plotter.cmap

    @cmap.setter
    def cmap(self, value: str) -> None:
        self.plotter.cmap = value

    @property
    def div_cmap(self) -> str:
        """Diverging Colormap for plotting

        :getter: return the diverging colormap choice
        :setter: sets the diverging colormap choice
        """
        return self.plotter.div_cmap

    @div_cmap.setter
    def div_cmap(self, value: str) -> None:
        self.plotter.div_cmap = value

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def plot_velocity_potential(
            self,
            inst: bool = True,
            phase: float = 0,
            symmetric: bool = True,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf plot for acoustic velocity potential

        Plots the velocity amplitude of the first-order acoustic velocity field
        of the fluid using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param inst: if `True` instantaneous amplitude is plotted
        :param phase: phase [0, 2 * pi]
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        data = self.data.get_velocity_potential(
            inst, phase, mode, scattered, incident,
        )

        abs_max = np.abs(data[-1]).max()
        divnorm = colors.TwoSlopeNorm(vmin=-abs_max, vcenter=0., vmax=abs_max)

        return self._triangulation_plot(
            data=data,
            cbar_label='Acoustic Velocity Potential [m^2/s]',
            tripcolor=tripcolor,
            mode=mode,
            symmetric=symmetric,
            use_diverging_cmap=True,
            ax=ax,
            norm=divnorm,
            ** kwargs
        )

    def plot_pressure(
            self,
            inst: bool = True,
            phase: float = 0,
            symmetric: bool = True,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf plot for acoustic pressure

        Plots the velocity amplitude of the first-order acoustic velocity field
        of the fluid using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param inst: if `True` instantaneous amplitude is plotted
        :param phase: phase [0, 2 * pi]
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        data = self.data.get_pressure(
            inst, phase, mode, scattered, incident,
        )

        abs_max = np.abs(data[-1]).max()
        if inst:
            norm = colors.TwoSlopeNorm(
                vmin=-abs_max, vcenter=0.,
                vmax=abs_max,
            )
            use_div_cmap = True
        else:
            norm = colors.Normalize(vmin=0, vmax=abs_max)
            use_div_cmap = False

        return self._triangulation_plot(
            data=data,
            cbar_label='Acoustic Pressure [Pa]',
            tripcolor=tripcolor,
            mode=mode,
            symmetric=symmetric,
            use_diverging_cmap=use_div_cmap,
            ax=ax,
            norm=norm,
            **kwargs
        )

    def plot_velocity(
            self,
            inst: bool = True,
            phase: float = 0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf plot for acoustic velocity field of the fluid

        Plots the velocity amplitude of the first-order acoustic velocity field
        of the fluid using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param inst: if `True` instantaneous amplitude is plotted
        :param phase: phase [0, 2 * pi]
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        data = self.data.get_velocity_magnitude(
            inst, phase, mode, scattered, incident,
        )

        return self._triangulation_plot(
            data=data,
            cbar_label='Acoustic Velocity [m/s]',
            tripcolor=tripcolor,
            mode=mode,
            symmetric=symmetric,
            use_diverging_cmap=False,
            ax=ax,
            **kwargs
        )

    def animate_pressure(
            self,
            frames: int = 64,
            interval: float = 100.0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Tricontourf animation for acoustic pressure of the fluid

        Animates the pressure of the first-order acoustic velocity
        field of the fluid over one period using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        data_meth = self.data.get_pressure

        return self._triangulation_animation(
            data_meth,
            tripcolor=tripcolor,
            frames=frames,
            interval=interval,
            mode=mode,
            scattered=scattered,
            incident=incident,
            symmetric=symmetric,
            ax=ax,
            cbar_label='Acoustic Pressure [Pa]',
            use_diverging_cmap=True,
            **kwargs,
        )

    def animate_velocity_potential(
            self,
            frames: int = 64,
            interval: float = 100.0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Tricontourf animation for acoustic velocity potential of the fluid

        Animates the velocity potential of the first-order acoustic velocity
        field of the fluid over one period using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        data_meth = self.data.get_velocity_potential

        return self._triangulation_animation(
            data_meth,
            tripcolor=tripcolor,
            frames=frames,
            interval=interval,
            mode=mode,
            scattered=scattered,
            incident=incident,
            symmetric=symmetric,
            ax=ax,
            cbar_label='Acoustic Velocity Potential [m^2/s]',
            use_diverging_cmap=True,
            **kwargs,
        )

    def animate_velocity(
            self,
            frames: int = 64,
            interval: float = 100.0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Tricontourf animation for acoustic velocity field of the fluid

        Animates the velocity amplitude of the first-order acoustic velocity
        field of the fluid over one period using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """

        data_meth = self.data.get_velocity_magnitude

        return self._triangulation_animation(
            data_meth,
            tripcolor=tripcolor,
            frames=frames,
            interval=interval,
            mode=mode,
            scattered=scattered,
            incident=incident,
            symmetric=symmetric,
            ax=ax,
            cbar_label='Acoustic Velocity [m/s]',
            ** kwargs,
        )

    def plot_pressure_evolution(
            self,
            inst: bool = True,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            layout: tuple[int, int] = (3, 3),
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf for acoustic pressure evolution of the fluid

        Plots the pressure amplitude of the first-order acoustic pressure field
        of the fluid over one period at different phases using
        Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`.

        The first phase value is always :math:`0\\pi` and the last one
        :math:`2\\pi`. The total number of plots and, hence, also the steps
        between the different phase values is the defined by the product of the
        ``layout`` tuple.

        :param inst: if `True` instantaneous amplitude is plotted
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param layout: number of rows and columns for plotting
        :param kwargs: passed through to the parent subplots command
        """

        n_row, n_col, phases = self._evo_compute_layout(layout)

        fig, axes = self._evo_create_subplots(n_row, n_col, **kwargs)

        get_data = partial(
            self.data.get_pressure,
            incident=incident, scattered=scattered,
        )

        # Get velocity norm, needed to make colormap of the right range
        X, Z, C_norm = get_data(instantaneous=False, mode=mode, phase=0)

        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Z) < self.data.r_max,
            C_norm, 0,
        )

        vmax = 1.01 * np.abs(C_norm).max()
        vmin = -vmax

        # Color bar label
        cbar_label = 'Acoustic Pressure [Pa]'

        for i, phase in enumerate(phases):

            row = i // n_col
            col = i % n_col
            ax = axes.flat[i]

            X, Z, C = get_data(instantaneous=True, mode=mode, phase=phase)
            self._evo_plot(
                X=Z, Y=X, C=C,
                symmetric=symmetric, tripcolor=tripcolor,
                cbar_label=cbar_label, use_diverging_cmap=True,
                ax=ax, vmin=vmin, vmax=vmax,
            )
            self._evo_clean_axis(ax, phase, row, col, n_row)

        norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        self._evo_create_cbar(
            fig, axes, cbar_label, self.plotter.div_cmap, norm,
        )

        return fig, axes

    def plot_velocity_potential_evolution(
            self,
            inst: bool = True,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            layout: tuple[int, int] = (3, 3),
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf for acoustic velocity potential evolution of the fluid

        Plots the velocity potential amplitude of the first-order acoustic
        velocity potential field of the fluid over one period at different
        phases using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`.

        The first phase value is always :math:`0\\pi` and the last one
        :math:`2\\pi`. The total number of plots and, hence, also the steps
        between the different phase values is the defined by the product of the
        ``layout`` tuple.

        :param inst: if `True` instantaneous amplitude is plotted
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param layout: number of rows and columns for plotting
        :param kwargs: passed through to the parent subplots command
        """
        n_row, n_col, phases = self._evo_compute_layout(layout)

        fig, axes = self._evo_create_subplots(n_row, n_col, **kwargs)

        get_data = partial(
            self.data.get_velocity_potential,
            incident=incident, scattered=scattered,
        )

        X, Z, C_norm = get_data(instantaneous=False, mode=mode, phase=0)

        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Z) < self.data.r_max,
            C_norm, 0,
        )

        vmax = 1.01 * np.abs(C_norm).max()
        vmin = -vmax

        # Color bar label
        cbar_label = 'Acoustic Velocity Potential [m^2/s]'

        for i, phase in enumerate(phases):

            row = i // n_col
            col = i % n_col
            ax = axes.flat[i]

            X, Z, C = get_data(instantaneous=True, mode=mode, phase=phase)
            self._evo_plot(
                X=Z, Y=X, C=C,
                symmetric=symmetric, tripcolor=tripcolor,
                cbar_label=cbar_label, use_diverging_cmap=True,
                ax=ax, vmin=vmin, vmax=vmax,
            )
            self._evo_clean_axis(ax, phase, row, col, n_row)

        norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        self._evo_create_cbar(
            fig, axes, cbar_label, self.plotter.div_cmap, norm,
        )

        return fig, axes

    def plot_velocity_evolution(
            self,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            layout: tuple[int, int] = (3, 3),
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf for acoustic velocity field evolution of the fluid

        Plots the velocity amplitude of the first-order acoustic velocity
        field of the fluid over one period at different phases using
        Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`.

        The first phase value is always :math:`0\\pi` and the last one
        :math:`2\\pi`. The total number of plots and, hence, also the steps
        between the different phase values is the defined by the product of the
        ``layout`` tuple.

        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param layout: number of rows and columns for plotting
        :param kwargs: passed through to the parent subplots command
        """
        n_row, n_col, phases = self._evo_compute_layout(layout)

        fig, axes = self._evo_create_subplots(n_row, n_col, **kwargs)

        get_data = partial(
            self.data.get_velocity_magnitude,
            incident=incident, scattered=scattered,
        )

        X, Z, C_norm = get_data(instantaneous=False, mode=mode, phase=0)

        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Z) < self.data.r_max,
            C_norm, 0,
        )

        vmin = 0
        vmax = 1.01 * C_norm.max()

        # Color bar label
        cbar_label = 'Acoustic Velocity [m/s]'

        for i, phase in enumerate(phases):

            row = i // n_col
            col = i % n_col
            ax = axes.flat[i]

            X, Z, C = get_data(instantaneous=True, mode=mode, phase=phase)
            self._evo_plot(
                X=Z, Y=X, C=C,
                symmetric=symmetric, tripcolor=tripcolor,
                cbar_label=cbar_label, use_diverging_cmap=False,
                ax=ax, vmin=vmin, vmax=vmax,
            )
            self._evo_clean_axis(ax, phase, row, col, n_row)

        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        self._evo_create_cbar(fig, axes, cbar_label, self.plotter.cmap, norm)

        return fig, axes

    # -------------------------------------------------------------------------
    # Private Methods for evolution plots
    # -------------------------------------------------------------------------
    def _evo_plot(
            self, X: np_arr, Y: np_arr, C: np_arr,
            symmetric: bool, tripcolor: bool,
            cbar_label: str, use_diverging_cmap: bool,
            ax: plt.Axes, vmin: float, vmax: float,
    ) -> None:
        # Plot
        _, _, _, cbar, _ = self.plotter.plot(
            X=X, Y=Y, C=C,
            radius=self.data.sol.R_0,
            symmetric=symmetric, tripcolor=tripcolor,
            cbar_label=cbar_label, use_diverging_cmap=use_diverging_cmap,
            ax=ax, vmin=vmin, vmax=vmax,
        )

        cbar.remove()

    @staticmethod
    def _evo_create_cbar(
            fig: plt.Figure, axes: plt.Axes,
            cbar_label: str, cmap: str, norm: colors.Normalize,
    ) -> None:
        fig.tight_layout()
        cm = ScalarMappable(norm, cmap)
        cbar = fig.colorbar(cm, ax=axes.ravel().tolist())
        cbar.ax.set_ylabel(cbar_label)

    @staticmethod
    def _evo_create_subplots(
            n_row: int, n_col: int, **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        fig, axes = plt.subplots(
            n_row, n_col,
            sharex=True, sharey=True,
            **kwargs,
        )
        return fig, axes

    @staticmethod
    def _evo_compute_layout(layout: tuple[int, int]) -> tuple[int, int, float]:
        n_row, n_col = layout
        n = n_col * n_row

        phases = np.linspace(0, 2 * np.pi, num=n)
        return n_row, n_col, phases

    def _evo_clean_axis(
        self, ax: plt.Axes, phase: float, row: int, col: int, n_row: int,
    ) -> None:
        ticks = self.data.sol.R_0 * np.asarray([-1, 1])
        labels = [-1, 1]

        ax.set_title(f'{phase/np.pi:.2f}' + r'$\pi$')

        if row != (n_row - 1):
            ax.set_xlabel('')
        if col > 0:
            ax.set_ylabel('')

        ax.set_xticks(ticks, labels=labels)
        ax.set_yticks(ticks, labels=labels)

        # set aspect ratio to 1:1
        ax.set_aspect(1)

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _triangulation_plot(
            self,
            data: tuple[np_arr, np_arr, np_arr],
            cbar_label: str,
            tripcolor: bool,
            symmetric: bool,
            use_diverging_cmap: bool,
            ax: Optional[plt.Axes],
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Helper function for tripcolor/tricontourf plot

        :param data: data to be plotted (X, Z, plot_data)
        :param cbar_label: label for the colorbar
        :param tripcolor: if `True` tripcolor, else tricontourf plot
        :param symmetric: if `True` the symmetry of the solution is used
        :param ax: Axes object
        :param kwargs: passed through to plotting method
        """
        kwargs.pop('mode', None)

        X, Z, C = data

        # Plot
        fig, ax, _, _, _ = self.plotter.plot(
            X=Z,
            Y=X,
            C=C,
            radius=self.data.sol.R_0,
            symmetric=symmetric,
            tripcolor=tripcolor,
            cbar_label=cbar_label,
            ax=ax,
            use_diverging_cmap=use_diverging_cmap,
            **kwargs,
        )
        return fig, ax

    def _triangulation_animation(
            self,
            data_meth: Callable[
                [bool, float, int, bool, bool],
                tuple[np_arr, np_arr, np_arr],
            ],
            tripcolor: bool,
            frames: int,
            interval: float,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            cbar_label: str = '',
            use_diverging_cmap: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Helper function for tripcolor/tricontourf animation

        :param data_meth: method for getting the plotting data
        :param tripcolor: if `True` tripcolor, else tricontourf plot
        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param cbar_label: label of colorbar
        :param use_diverging_cmap: use :attr:`div_cmap` as colormap
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        # Data function for animation
        animate_meth = lambda phase: data_meth(
            phase=phase, instantaneous=True, mode=mode,
            scattered=scattered, incident=incident,
        )

        # Get velocity norm, needed to make colormap of the right range
        X, Y, C_norm = data_meth(
            instantaneous=False, mode=mode,
            scattered=scattered, incident=incident,
        )
        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Y) < self.data.r_max,
            C_norm, 0,
        )

        return self.plotter.animate(
            frames=frames,
            interval=interval,
            tripcolor=tripcolor,
            symmetric=symmetric,
            cbar_label=cbar_label,
            use_diverging_cmap=use_diverging_cmap,
            animate_meth=animate_meth,
            C_norm=C_norm,
            radius=self.data.sol.R_0,
            ax=ax,
            **kwargs
        )


if __name__ == '__main__':
    pass
