from plotting.scattering.setup_test_scattering import BaseTestFluidScattering

from osaft import (
    FluidScatteringPlot,
    doinikov1994compressible,
    doinikov1994rigid,
    hasegawa1969,
    king1934,
)


class TestKingPressureFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()

        self.sol = king1934.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.sol, r_max=r_max,
        )

        self.fcn_plot = self.fluid_plot.plot_pressure
        self.fcn_plot_evolution = self.fluid_plot.plot_pressure_evolution
        self.fcn_animate = self.fluid_plot.animate_pressure
        self._name_prefix = 'King1934_FluidPressure_'


class TestHasegawaPressureFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()

        self.E_s = 70e9
        self.nu_s = 1 / 3

        self.sol = hasegawa1969.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, E_s=self.c_s, nu_s=self.nu_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.sol, r_max=r_max,
        )

        self.fcn_plot = self.fluid_plot.plot_pressure
        self.fcn_plot_evolution = self.fluid_plot.plot_pressure_evolution
        self.fcn_animate = self.fluid_plot.animate_pressure
        self._name_prefix = 'Hasegawa1969_FluidPressure_'


class TestDoiniRigidPressureFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()

        self.eta_f = 0.89e-3
        self.zeta_f = 2.4e-3

        self.sol = doinikov1994rigid.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s,
            rho_f=self.rho_f, c_f=self.c_f,
            eta_f=self.eta_f, zeta_f=self.zeta_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.sol, r_max=r_max,
        )

        self.fcn_plot = self.fluid_plot.plot_pressure
        self.fcn_plot_evolution = self.fluid_plot.plot_pressure_evolution
        self.fcn_animate = self.fluid_plot.animate_pressure
        self._name_prefix = 'Doini1994Rigid_FluidPressure_'


class TestDoiniCompressiblePressureFluidScattering(BaseTestFluidScattering):

    def setUp(self):
        super().setUp()

        self.eta_f = 0.89e-3
        self.zeta_f = 2.4e-3
        self.eta_s = 1e-3
        self.zeta_s = 1e-3

        self.sol = doinikov1994compressible.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, c_s=self.c_s,
            eta_s=self.eta_s, zeta_s=self.zeta_s,
            rho_f=self.rho_f, c_f=self.c_f,
            eta_f=self.eta_f, zeta_f=self.zeta_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.sol, r_max=r_max,
        )

        self.fcn_plot = self.fluid_plot.plot_pressure
        self.fcn_plot_evolution = self.fluid_plot.plot_pressure_evolution
        self.fcn_animate = self.fluid_plot.animate_pressure
        self._name_prefix = 'Doini1994Compressible_FluidPressure_'
