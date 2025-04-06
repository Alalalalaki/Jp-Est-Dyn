"""
This code solves the HR model given calibrated parameters, i.e.
Hopenhayn model in general equilibrium with firing cost.
"""


from dataclasses import dataclass
from typing import Any

import numpy as np
import scipy as sp
import pandas as pd

from hopenhayn import Hopenhayn, Result

Array = Any


@dataclass
class HR(Hopenhayn):

    # additional parameters in firing cost
    n_size: int = 250
    n_max: int = 5000
    tau_adj: float = 0
    labor_adj: str = "Firing"

    def __post_init__(self):

        assert self.equilibrium in ["GE", "BGP"], 'HR model applies to only GE or BGP.'
        assert self.alt_timing == False, 'HR model is not applied to altnative timing right now.'
        assert self.vx == 0, 'HR model is not applied to changing exit value right now.'
        assert self.gamma_l == 0, 'HR model is not applied to wage distortion right now.'
        assert self.labor_adj in ["Firing", "Full", "Hiring"
                                         ], 'Adjustment cost must be either Firing, Full, or Hiring.'

        super().__post_init__()

        # expand vals to 2d, i.e. s_grid * n_grid
        self.s_grid = self.s_vals
        self.s_vals = np.tile(self.s_vals.reshape(-1, 1), self.n_size)

        # For n_grid use an exponential grid with shape parameter 0.3
        # , which seems to be more realistic than a log scale below
        # but the result should be insensitive to either way
        self.n_grid = np.linspace(1e-8, self.n_max**.3, num=self.n_size)**(1/.3)
        # self.n_grid = np.geomspace(1e-8, self.n_max, num=self.n_size)

        temp = np.zeros_like(self.s_vals)
        temp[:, 0] = self.nu
        self.nu = temp

    def adjustment_cost_func(self, n1, n0,):
        if self.labor_adj == "Firing":
            c_adjust = self.tau_adj * (n0 - n1).clip(min=0)
        elif self.labor_adj == "Full":
            c_adjust = self.tau_adj * np.abs(n0 - n1)
        elif self.labor_adj == "Hiring":
            c_adjust = self.tau_adj * (n1 - n0).clip(min=0)
        return c_adjust

    def T_value_operator(self, v, w):

        s_grid, n_grid = self.s_grid, self.n_grid

        # Note: 3-D matrix: x=s, y=n0, z=n1

        f_vals = self.production_func(s_grid.reshape((-1, 1, 1)), n_grid.reshape((1, 1, -1)))
        c_adjust_vals = self.adjustment_cost_func(n_grid.reshape((1, 1, -1)), n_grid.reshape((1, -1, 1)))
        pi_vals = self.profit_func(f_vals, w, n_grid.reshape((1, 1, -1)), None, c_extra=c_adjust_vals)


        exit_cost = self.adjustment_cost_func(0, n_grid.reshape((1, 1, -1)))

        integral = (self.F @ v)[:, np.newaxis, :]
        # for the case of exogenous exit, with no need to pay firing cost
        # otherwise need to + self.delta * exit_cost
        integral = integral * (1 - self.delta)

        v1 = self.beta * np.maximum(-exit_cost, integral)

        v_new = np.max(pi_vals + v1, axis=2)

        # # old loop version
        # v_new = np.empty_like(v)
        # for i in range(self.s_size):
        #     for j in range(self.n_size):
        #         f_vals = self.production_func(s_grid[i], n_grid)
        #         c_fire_vals = self.adjustment_cost_func(n_grid, n_grid[j])
        #         pi_vals = self.profit_func(f_vals, w, n_grid, c_=c_fire_vals)

        #         integral = self.F[i, :] @ v
        #         exit_cost = self.adjustment_cost_func(0, n_grid)
        #         v1 = self.beta * np.maximum(-exit_cost, integral)

        #         Tv = np.max(pi_vals + v1)
        #         v_new[i, j] = Tv

        return v_new

    def solve_labor_decision(self, v, w):
        # the same as T_value_operator except last lines

        s_grid, n_grid = self.s_grid, self.n_grid

        f_vals = self.production_func(s_grid.reshape((-1, 1, 1)), n_grid.reshape((1, 1, -1)))
        c_adjust_vals = self.adjustment_cost_func(n_grid.reshape((1, 1, -1)), n_grid.reshape((1, -1, 1)))
        pi_vals = self.profit_func(f_vals, w, n_grid.reshape((1, 1, -1)), None, c_extra=c_adjust_vals)

        integral = (self.F @ v)[:, np.newaxis, :] * (1 - self.delta)
        exit_cost = self.adjustment_cost_func(0, n_grid.reshape((1, 1, -1)))
        v1 = self.beta * np.maximum(-exit_cost, integral)

        n1_index = np.argmax(pi_vals + v1, axis=2)

        # n1_index = np.empty_like(v)

        # for i in range(self.s_size):
        #     for j in range(self.n_size):
        #         f_vals = self.production_func(s_grid[i], n_grid)
        #         c_fire_vals = self.adjustment_cost_func(n_grid, n_grid[j])
        #         pi_vals = self.profit_func(f_vals, w, n_grid, c_=c_fire_vals)

        #         integral = self.F[i, :] @ v
        #         exit_cost = self.adjustment_cost_func(0, n_grid)
        #         v1 = self.beta * np.maximum(-exit_cost, integral)

        #         ind = np.argmax(pi_vals + v1)
        #         n1_index[i, j] = ind

        return n1_index

    def solve_exit_decision(self, v, w, n1_index):
        X = np.empty_like(v)

        s_grid, n_grid = self.s_grid, self.n_grid

        for i in range(self.s_size):
            for j in range(self.n_size):
                n1_j = n1_index[i, j]
                integral = v[:, n1_j] @ self.F[i, :]
                exit_cost = self.adjustment_cost_func(0, n_grid[n1_j])
                X[i, j] = int(-exit_cost > integral)

        x_index = np.argmin(X, axis=0)
        x = s_grid[x_index]

        return x, X

    def T_dist_operator(self, mu, n1_index, X, m):

        mu_new = np.zeros_like(mu)

        mu = (1 - X) * mu

        # eta for the case of BGP, if GE eta=0 and nothing changes
        # delta for the case of exogenous exit
        mu = mu * ((1 - self.delta) / (1 + self.eta))

        for i in range(self.s_size):
            for j in range(self.n_size):
                mu_new[:, n1_index[i, j]] += mu[i, j] * self.F[i, :]

        mu_new += m * self.nu

        return mu_new

    def dist_func_iteration(self, m, n1_index, X):

        # Initialize mu
        mu = np.zeros_like(self.s_vals)

        # Set up loop
        i = 0
        error = self.tol + 1

        while i < self.max_iter and error > self.tol:
            mu_new = self.T_dist_operator(mu, n1_index, X, m)
            error = np.max(np.abs(mu - mu_new))
            i += 1
            if self.verbose and i % self.print_skip == 0:
                print(f"Error at iteration {i} is {error}.")
            mu = mu_new

        if i == self.max_iter:
            print("Failed to converge distribution!")

        if self.verbose and i < self.max_iter:
            print(f"Distribution converged in {i} iterations.")

        return mu  # , error, i

    def calculate_aggregate_adjustment_cost(self, mu, n_vals, X):
        adj_vals = self.adjustment_cost_func(n_vals, self.n_grid)
        R = np.sum(mu * adj_vals)  # include the adjustment costs paid by entrant with n0=0 if allow hiring cost
        adj_exit_vals = X * self.adjustment_cost_func(0, n_vals)
        R_exit = np.sum(mu * adj_exit_vals)
        return R + R_exit

    def labor_market_clearing(self, m, mu_m1, w, X, n_vals, f_vals):
        mu = m * mu_m1

        cf_sum = self.cf * mu.sum()
        L_d = np.sum(mu * n_vals) + self.cf_in_labor * cf_sum  # + R if adjustment cost unit in labor

        if self.equilibrium == "GE":
            Y = np.sum(mu * f_vals)
            R = self.calculate_aggregate_adjustment_cost(mu, n_vals, X)
            p_temp = w if self.cf_in_labor else 1
            Pi = Y - w * L_d - p_temp * cf_sum - self.ce * m - R
            L_s = 1 / self.A - Pi / w  # C = wN + Pi , C = w/A

        if self.equilibrium == "BGP":
            L_s = 1

        error = L_s - L_d
        return error

    def solve_m(self, w, n1_index, X, n_vals, f_vals):
        mu_m1 = self.dist_func_iteration(1, n1_index, X)
        if self.m_solver == "newton":
            m, res = sp.optimize.newton(self.labor_market_clearing, self.m_ini, args=(mu_m1, w, X, n_vals, f_vals),
                                        maxiter=self.max_iter_, full_output=True)
        elif self.m_solver == "brentq":
            m, res = sp.optimize.brentq(self.labor_market_clearing, self.m_min, self.m_max,
                                        args=(mu_m1, w, X, n_vals, f_vals),
                                        maxiter=self.max_iter_, full_output=True)
        assert res.converged, "Failed to converge entrant mass!"

        mu = m * mu_m1
        return m, mu

    def solve_model(self):
        w, v = self.solve_wage()
        n1_index = self.solve_labor_decision(v, w).astype(int)
        x, X = self.solve_exit_decision(v, w, n1_index)

        n_vals = self.n_grid[n1_index]
        f_vals = self.production_func(self.s_vals, n_vals)

        m, mu = self.solve_m(w, n1_index, X, n_vals, f_vals)

        R = self.calculate_aggregate_adjustment_cost(mu, n_vals, X)

        return Result_HR(
            w=w,
            v=v,
            x=x,
            X=X,
            mu=mu,
            m=m,
            n_vals=n_vals,
            f_vals=f_vals,

            # HR results
            n1_index=n1_index,
            R=R,

            # primitives
            theta=self.theta,
            s_vals=self.s_vals,
            s_grid=self.s_grid,
            n_grid=self.n_grid,
            F=self.F,
            nu=self.nu,
            ce=self.ce,
            cf=self.cf,
            eta=self.eta,
            delta=self.delta,
            # not allowed para
            vx=self.vx,
            tau_l=self.tau_l,
            gamma_l=self.gamma_l,
            kappa=self.kappa,

            # mode
            equilibrium=self.equilibrium,
            cf_in_labor=self.cf_in_labor,

            # HR adj para
            tau_adj=self.tau_adj,
            labor_adj=self.labor_adj,
        )


@dataclass
class Result_HR(Result):

    # HR results
    n1_index: Array  # index of n1 choice
    R: Array  # all adjustment cost (in unit of product)

    # HR primitives
    s_grid: Array
    n_grid: Array

    # HR adj para
    tau_adj: float
    labor_adj: str

    def __post_init__(self):
        self.s_size = len(self.s_grid)
        self.n_size = len(self.n_grid)

        super().__post_init__(inherit=True)

        self.aggregate_profit = self.aggregate_profit - self.R
        self.average_profit = self.aggregate_profit / self.aggregate_firm_mass

        self.job_turnover_rate = ((np.sum(np.abs(self.n_vals*(1-self.X) - self.n_grid) * self.mu)
                                   + np.sum(self.m*self.nu*self.n_vals))
                                  / self.aggregate_employment_production)

        # gather statistics
        self.stat = self._stat()
        self.stat_size_dist = self._stat_size_dist()

    def T_dist_operator(self, mu,):
        # copy the function in model except remove eta part and remove last line of adding new entrant
        mu_new = np.zeros_like(mu)
        mu = (1 - self.X) * mu * (1 - self.delta)
        for i in range(self.s_size):
            for j in range(self.n_size):
                mu_new[:, self.n1_index[i, j]] += mu[i, j] * self.F[i, :]
        return mu_new

    def calculate_survival_stat(self, age=10):
        conditional_pdf = self.nu
        for _ in range(age-1):
            nu_new = self.T_dist_operator(conditional_pdf)
            conditional_pdf = nu_new
        survival_rate = np.sum(conditional_pdf)
        if self.cf_in_labor:
            life_growth_rate = np.sum(
                conditional_pdf / survival_rate * self.n_vals_plus_cf) / self.average_entrant_size_include_cf
        else:
            life_growth_rate = np.sum(conditional_pdf / survival_rate * self.n_vals) / self.average_entrant_size_prod
        life_growth_rate = life_growth_rate - 1
        return survival_rate*100, life_growth_rate*100

    def _stat(self):
        df = self._stat_base()
        df['jov_turnover_rate'] = self.job_turnover_rate
        return df

    def _stat_size_dist(self,):
        """
        Calculate statistics for size distribution under sxn grids.
        Use additional column loop otherwise the same as the original cope in hopenhayn.
        """

        n_threshold = [10, 30, 100, ]  # use 9,29,99?? // alternative: 5, 20, 50, 300

        dist_num = np.zeros(len(n_threshold)+1)
        dist_employ = np.zeros_like(dist_num)
        for i in range(self.n_size):
            n_at = self.n_vals[:, i].searchsorted(n_threshold)
            dist_num += np.array([np.sum(g) for g in np.split(self.mu_pmf[:, i], n_at)])
            dist_employ += np.array([np.sum(g) / self.aggregate_employment_production for g in np.split(
                self.mu[:, i] * self.n_vals[:, i], n_at)])
        n_at = self.n_vals[:, 0].searchsorted(n_threshold)
        dist_num_entrant = [np.sum(g) * 100 for g in np.split(self.nu[:, 0], n_at)]
        dist_employ_entrant = [np.sum(g) * 100 / self.aggregate_employment_production_entrant
                               for g in np.split(self.m * self.nu[:, 0] * self.n_vals[:, 0], n_at)]

        if self.cf_in_labor:
            dist_num_include_cf = np.zeros_like(dist_num)
            dist_employ_include_cf = np.zeros_like(dist_num)
            for i in range(self.n_size):
                n_at_include_cf = self.n_vals_plus_cf[:, i].searchsorted(n_threshold)
                dist_num_include_cf += np.array([np.sum(g) for g in np.split(self.mu_pmf[:, i], n_at_include_cf)])
                dist_employ_include_cf += np.array([np.sum(g) / self.aggregate_employment_include_cf
                                                    for g in np.split(
                                                    self.mu[:, i] * self.n_vals_plus_cf[:, i], n_at_include_cf)])
            n_at_include_cf = (self.n_vals[:, 0] + self.cf).searchsorted(n_threshold)
            dist_num_include_cf_entrant = [np.sum(g) * 100 for g in np.split(self.nu[:, 0], n_at_include_cf)]
            dist_employ_include_cf_entrant = [
                np.sum(g) * 100 / self.aggregate_employment_include_cf_entrant
                for g in np.split(self.m * self.nu[:, 0] * self.n_vals_plus_cf[:, 0],
                                  n_at_include_cf)]
        else:
            dist_num_include_cf = None
            dist_employ_include_cf = None
            dist_num_include_cf_entrant = None
            dist_employ_include_cf_entrant = None

        size_col = [str(a)+'-'+str(b) for a, b in zip(['']+n_threshold, n_threshold+[''])]
        df = pd.DataFrame({
            'num_prod': dist_num,
            'emp_prod': dist_employ,
            'num_prod_entrant': dist_num_entrant,
            'emp_prod_entrant': dist_employ_entrant,
            'num_include_cf': dist_num_include_cf,
            'emp_include_cf': dist_employ_include_cf,
            'num_include_cf_entrant': dist_num_include_cf_entrant,
            'emp_include_cf_entrant': dist_employ_include_cf_entrant,
        }, index=size_col).T
        return df


def main():
    # use calibrated parameters to form and calculate
    test = HR(
        # parameters to calibration (arbitrary)
        ce=10,  # match entry rate
        cf=5,  # match average size
        a=.14,  # match ?
        rho=.9,  # match growth rate
        sigma=.2,  # match exit rate
        G_mu=1,  # match average entry size
        G_sigma=.4,  # match concentration of entrants ?
        s_size=50,
        A=1/200,  # .6

        n_size=101,
        n_max=5000,
        tau_adj=0.1,

        verbose=False,
        print_skip=100
    )
    res = test.solve_model()


if __name__ == "__main__":
    main()
