import unittest

from plotting.scattering.setup_test_scattering import BaseTestFluidScattering


class TestVelocityFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()
        self.fcn_plot = self.fluid_plot.plot_velocity
        self.fcn_plot_evolution = self.fluid_plot.plot_velocity_evolution
        self.fcn_animate = self.fluid_plot.animate_velocity
        self._name_prefix = 'Yosioka1955_FluidVelocity_'


class TestVelocityPotentialFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()
        self.fcn_plot = self.fluid_plot.plot_velocity_potential
        self.fcn_plot_evolution = (
            self.fluid_plot.plot_velocity_potential_evolution
        )
        self.fcn_animate = self.fluid_plot.animate_velocity_potential
        self._name_prefix = 'Yosioka1955_FluidVelocityPotential_'


class TestPressureFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()
        self.fcn_plot = self.fluid_plot.plot_pressure
        self.fcn_plot_evolution = self.fluid_plot.plot_pressure_evolution
        self.fcn_animate = self.fluid_plot.animate_pressure
        self._name_prefix = 'Yosioka1955_FluidPressure_'


if __name__ == '__main__':
    unittest.main()
