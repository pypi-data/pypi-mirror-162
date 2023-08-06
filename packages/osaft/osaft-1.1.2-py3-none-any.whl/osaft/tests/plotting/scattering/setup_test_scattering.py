import inspect

from matplotlib import pyplot as plt

from osaft import FluidScatteringPlot, WaveType, yosioka1955
from osaft.tests.basetest_plotting import BaseTestPlotting


class BaseTestScattering(BaseTestPlotting):

    def setUp(self) -> None:

        super().setUp()
        self.f = 10e6
        self.R_0 = 30e-6
        self.c_s = 3e2
        self.c_f = 1.5e3
        self.rho_s = 1e3
        self.rho_f = 1.5e3
        self.p_0 = 1e5
        self.wave_type = WaveType.TRAVELLING
        self.position = self.c_f / self.f / 8

        self.N_max = 10

        self.yosioka = yosioka1955.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, c_s=self.c_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )


class BaseTestFluidScattering(BaseTestScattering):

    def setUp(self) -> None:
        super().setUp()

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.yosioka, r_max=r_max,
        )
        self._name_prefix = ''

    def test_cmap(self) -> None:
        new_cmap = 'grays'
        new_div_cmap = 'RdYlBu'

        self.fluid_plot.cmap = new_cmap
        self.fluid_plot.div_cmap = new_div_cmap

        self.assertEqual(new_cmap, self.fluid_plot.cmap)
        self.assertEqual(new_div_cmap, self.fluid_plot.div_cmap)

    def _is_base_class(self) -> bool:
        return self.__class__ == BaseTestFluidScattering

    def test_tripcolor_symmetric(self):
        if self._is_base_class():
            return 1
        fig, ax = self.fcn_plot(
            tripcolor=True,
            inst=False,
            mode=None,
            phase=0,
            symmetric=True,
            incident=True,
            scattered=True,
        )
        name = inspect.stack()[0][3]  # method name
        name = self._name_prefix + name
        self.save_fig(fig, name)

    def test_tripcolor_not_symmetric(self):
        if self._is_base_class():
            return 1
        fig, ax = self.fcn_plot(
            tripcolor=True,
            inst=False,
            mode=None,
            phase=0,
            symmetric=False,
            incident=True,
            scattered=True,
        )

        name = inspect.stack()[0][3]  # method name
        name = self._name_prefix + name
        self.save_fig(fig, name)

    def test_tricontourf(self):
        if self._is_base_class():
            return 1
        fig, ax = self.fcn_plot(
            inst=True,
            mode=1,
            phase=0,
            symmetric=True,
            incident=False,
            scattered=True,
        )
        name = inspect.stack()[0][3]  # method name
        name = self._name_prefix + name
        self.save_fig(fig, name)

    def test_animation_tricontourf(self):
        if self._is_base_class():
            return 1
        anim = self.fcn_animate(
            frames=10,
            interval=100,
            symmetric=True,
            scattered=False,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tripcolor(self):
        if self._is_base_class():
            return 1
        anim = self.fcn_animate(
            tripcolor=True,
            frames=10,
            interval=100,
            symmetric=True,
            scattered=True,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tricontourf_not_symmetric(self):
        if self._is_base_class():
            return 1
        anim = self.fcn_animate(
            frames=10,
            interval=100,
            symmetric=False,
            scattered=False,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tripcolor_not_symmetric(self):
        if self._is_base_class():
            return 1
        anim = self.fcn_animate(
            tripcolor=True,
            frames=10,
            interval=100,
            symmetric=False,
            scattered=True,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_evolution_tricontourf(self):
        if self._is_base_class():
            return 1
        fig, ax = self.fcn_plot_evolution(
            symmetric=True,
            scattered=True,
            incident=False,
            mode=1,
        )
        name = inspect.stack()[0][3]  # method name
        name = self._name_prefix + name
        self.save_fig(fig, name)

    def test_evolution_tripcolor(self):
        if self._is_base_class():
            return 1
        fig, ax = self.fcn_plot_evolution(
            symmetric=True,
            scattered=True,
            incident=False,
            mode=None,
            tripcolor=True,
        )
        name = inspect.stack()[0][3]  # method name
        name = self._name_prefix + name
        self.save_fig(fig, name)


if __name__ == '__main__':
    pass
