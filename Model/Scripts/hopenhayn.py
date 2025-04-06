"""
This code solves the industry equilibrium given calibrated parameters
"""


from dataclasses import dataclass
from typing import Any

import numpy as np
import scipy as sp
from scipy.stats import lognorm  # , norm, uniform, pareto, gaussian_kde
from quantecon import markov
# from interpolation import mlinterp, interp
# from numba import njit, prange, vectorize, jitclass

import pandas as pd
import matplotlib.pyplot as plt

Array = Any


@dataclass
class Hopenhayn:
    """
    A class to calculate the steady state equilibrium for Hopenhayn model,
    where the only state varaible is the productivity.
    """
    # model primitives
    cf: float  # production fixed cost period
    ce: float  # entry cost
    s_size: int  # grid size of productivity

    # parameters in idiosyncratic shock markov process
    a: float  # drift parameter of markov process
    rho: float  # persistence parameter of markov process
    sigma: float  # std of error in markov process

    # parameters in entrants' productivity
    G_mu: float  # lognormal mean
    G_sigma: float  # lognormal std
    # xi: float # alternatively use pareto distribution with parameter

    # commom parameters
    beta: float = .96  # discount rate
    theta: float = .64  # production function curvature

    # model choice
    equilibrium: str = "GE"  # PE / GE / BGP
    cf_in_labor: int = 1  # 1 if cf is in unit of labor and enter labor market clearing, otherwise 0
    alt_timing: bool = False  # default Hopenhayn 1992 timing, alternative HVS2020 timing

    # parameters in labor supply
    zeta: float = 2  # labor elasticity in PE, following CP2016 use L = w**zeta
    A: float = .6  # labor parameter in GE, pins down to employment to population ratio
    eta: float = .0  # labor supply growth rate in BGP

    # extention parameter
    vx: float = 0  # exit value
    delta: float = 0  # exogenous exit rate
    #     cf_a:float = 0
    #     cf_b:float = 1
    kappa: float = 2 # the cost parameter of initial investment

    # distortion parameter
    tau_l: float = 1  # additional labor wage tax on wage
    gamma_l: float = 0  # distortion parameter for labor wage tax

    # iteration parameters
    w_solver: str = "brentq"
    m_solver: str = "newton"
    w_ini: float = 1
    w_min: float = 0.1
    w_max: float = 10
    m_ini: float = 0.1
    m_min: float = 1e-7
    m_max: float = 10
    tol: float = 1e-7
    max_iter: int = 2000
    max_iter_: int = 500
    verbose: bool = False
    print_skip: int = 100
    suppress_fail: bool = False

    def __post_init__(self):

        assert self.cf_in_labor in [0, 1], 'cf_in_labor must be either 1 (labor) or 0 (product).'
        assert self.w_solver in ['newton', 'brentq'], 'optimal solver must be either newton or brentq.'
        assert self.m_solver in ['newton', 'brentq'], 'optimal solver must be either newton or brentq.'
        assert self.equilibrium in ['PE', 'GE', 'BGP'], 'equilibrium must be either PE, GE or BGP.'
        if self.equilibrium == 'GE':
            assert self.A > 0, 'under GE, A must be greater than 0.'
            assert self.eta == 0, 'under GE, population growth eta must be 0.'
        if self.equilibrium == 'BGP':
            # can we set labor supply growth to be negative?
            assert self.eta >= 0, 'under BGP, population growth eta must be greater than 0.'
            assert self.A == 0, 'under BGP, A in utility function has no effect. Please set A to 0.'

        # create state grids from tauchen approximation
        # https://quanteconpy.readthedocs.io/en/latest/markov/approximation.html#quantecon.markov.approximation.tauchen
        self.mc = markov.tauchen(
            rho=self.rho, sigma=self.sigma, mu=self.a, n_std=4, n=self.s_size
        )
        self.s_vals = np.exp(self.mc.state_values)
        # conditional probabilities
        self.F = self.mc.P

        self.nu = self._set_entrant_grid()

    def _set_entrant_grid(self):
        # get pmf of state grids for entrants
        # Problem: if the grid from tauchen is too sparse for entry cohort,
        # most entrants would likely to have the same value?
        G = lognorm(s=self.G_sigma, scale=np.e**(self.G_mu))
        pdf_entry = G.pdf(self.s_vals)
        nu = pdf_entry / np.sum(pdf_entry)  # not sure correct, or use cdf?
        return nu

    def solve_employment(self, s, w):
        if self.gamma_l != 0:
            w = w * self.tau_l * (s**self.gamma_l)  # when tau_l=1 & gamma_l=0, w=w
        n = (self.theta * s / w) ** (1 / (1 - self.theta))
        return n

    def production_func(self, s, n):
        f = s * (n ** self.theta)
        return f

    #     def cf_funtion(self, s):
    #         cf = self.cf_a + self.cf_b *(s**(1/(1-self.theta)))
    #         return cf

    def profit_func(self, f, w, n, s, c_extra=0):
        if self.gamma_l != 0:
            w = w * self.tau_l * (s**self.gamma_l)
        p_temp = w if self.cf_in_labor else 1  # if paid in labor or product
        pi = f - w * n - p_temp * self.cf - c_extra
        return pi

    def T_value_operator(self, v, w):

        v_new = np.empty_like(v)

        integral = self.F @ v
        # for the case of exogenous exit
        integral = integral * (1 - self.delta) + self.delta * self.vx # if vx = 0, no last term

        s_vals = self.s_vals
        n_vals = self.solve_employment(s_vals, w)
        f_vals = self.production_func(s_vals, n_vals)

        v_new = self.profit_func(f_vals, w, n_vals, s_vals) + self.beta * integral.clip(min=self.vx)

        if self.alt_timing:
            v_new = (self.profit_func(f_vals, w, n_vals, s_vals) + self.beta * integral).clip(min=self.vx)

        return v_new

    def value_func_iteration(self, w):

        # Initialize v
        v = np.ones_like(self.s_vals)

        # Set up loop
        i = 0
        error = self.tol + 1

        while i < self.max_iter and error > self.tol:
            v_new = self.T_value_operator(v, w)
            error = np.max(np.abs(v - v_new))
            i += 1
            if self.verbose and i % self.print_skip == 0:
                print(f"Error at iteration {i} is {error}.")
            v = v_new

        if i == self.max_iter:
            print("Failed to converge value!")

        if self.verbose and i < self.max_iter:
            print(f"Value converged in {i} iterations.")

        return v  # , error, i

    def entry_clearing(self, w,):
        v = self.value_func_iteration(w)
        v_entry = np.sum(v * self.nu)  # * self.beta if not operate in entry period
        error = v_entry - self.ce   # self.ce * w if ce unit in labor // no need - self.vx
        return error

    def solve_wage(self,):
        if self.w_solver == "newton":
            w, res = sp.optimize.newton(self.entry_clearing, self.w_ini, full_output=True, maxiter=self.max_iter_)
        elif self.w_solver == "brentq":
            w, res = sp.optimize.brentq(self.entry_clearing, self.w_min, self.w_max,
                                        maxiter=self.max_iter_, full_output=True)
        assert res.converged, "Failed to converge price!"
        v = self.value_func_iteration(w)
        return w, v

    def solve_exit_decision(self, v, w,):
        """
        Note:
          - 0 is the normalized exit value
          - if 0 is larger than all values in v_next, the function will return IndexError since x is not in s_vals
        """
        v_next = self.F @ v
        x_index = np.searchsorted(v_next, self.vx)

        if self.alt_timing:
            n_vals = self.solve_employment(self.s_vals, w)
            f_vals = self.production_func(self.s_vals, n_vals)
            pi_vals = self.profit_func(f_vals, w, n_vals, self.s_vals)
            v_operate = pi_vals + self.beta*v
            x_index = np.searchsorted(v_operate, self.vx)

        x = self.s_vals[x_index]
        X = np.where(self.s_vals < x, 1, 0)

        return x, X

    def solve_mu(self, m, X):
        P_x = (self.F * (1 - X).reshape(self.s_size, 1)).T

        # eta for the case of BGP, if GE eta=0 and nothing changes
        # delta for the case of exogenous exit
        P_x = P_x * ((1 - self.delta) / (1 + self.eta))

        I = np.eye(self.s_size)
        temp = sp.linalg.inv(I - P_x)
        mu = m * (temp @ self.nu)

        if self.alt_timing:
            temp = sp.linalg.inv(I - self.F.T)
            mu = m * (temp @ self.nu) * (1 - X)
        return mu

    def labor_market_clearing(self, m, mu_m1, w, n_vals, f_vals):
        mu = m * mu_m1

        cf_sum = self.cf * mu.sum()
        L_d = mu @ n_vals + self.cf_in_labor * cf_sum  # + self.ce * m if ce unit in labor

        if self.equilibrium == "GE":
            # labor supply is elastic, follow HR1993 lottery method
            Y = mu @ f_vals
            p_temp = w if self.cf_in_labor else 1
            Pi = Y - w * L_d - p_temp * cf_sum - self.ce * m
            L_s = 1 / self.A - Pi / w  # C = wN + Pi , C = w/A

        if self.equilibrium == "BGP":
            # labor supply is inelastic
            # note in BGP, the calculated m and mu are normalized by L
            L_s = 1

        if self.equilibrium == "PE":
            L_s = w**self.zeta

        error = L_s - L_d
        return error

    def solve_m(self, w, X, n_vals, f_vals):
        mu_m1 = self.solve_mu(1, X)

        if self.m_solver == "newton":
            m, res = sp.optimize.newton(
                self.labor_market_clearing, self.m_ini,
                args=(mu_m1, w, n_vals, f_vals), maxiter=self.max_iter_, full_output=True
            )
        elif self.m_solver == "brentq":
            m, res = sp.optimize.brentq(
                self.labor_market_clearing, self.m_min, self.m_max,
                args=(mu_m1, w, n_vals, f_vals), maxiter=self.max_iter_, full_output=True
            )

        assert res.converged, "Failed to converge entrant mass!"

        mu = m * mu_m1
        return m, mu

    def solve_model(self):
        try:
            w, v = self.solve_wage()
        except (RuntimeError, ValueError) as e:
            if not self.suppress_fail:
                raise e
            return None
        if w <= 0:
            if not self.suppress_fail:
                raise ValueError("w converges to less 0 value.")
            return None

        try:
            x, X = self.solve_exit_decision(v, w)
        except (IndexError) as e:
            if not self.suppress_fail:
                raise e
            return None
        if np.sum(X) == 0:  # no firm in the productivity grid would leave
            if not self.suppress_fail:
                print("Caution: there is no exit in the model")
            return None

        n_vals = self.solve_employment(self.s_vals, w)
        f_vals = self.production_func(self.s_vals, n_vals)

        m, mu = self.solve_m(w, X, n_vals, f_vals)
        if m <= 0:
            if not self.suppress_fail:
                raise ValueError("m converges to less 0 value.")
            return None

        if self.alt_timing:
            m = sum((1-X) * self.nu) * m  # entry mass exclude ones that exit immediately

        return Result(
            w=w,
            v=v,
            x=x,
            X=X,
            mu=mu,
            m=m,
            n_vals=n_vals,
            f_vals=f_vals,

            # primitives
            theta=self.theta,
            s_vals=self.s_vals,
            F=self.F,
            nu=self.nu,
            ce=self.ce,
            cf=self.cf,
            a=self.a,
            rho=self.rho,
            sigma=self.sigma,
            G_mu=self.G_mu,
            G_sigma=self.G_sigma,
            eta=self.eta,
            delta=self.delta,
            vx=self.vx,
            tau_l=self.tau_l,
            gamma_l=self.gamma_l,
            kappa=self.kappa,


            # mode
            equilibrium=self.equilibrium,
            cf_in_labor=self.cf_in_labor,
        )


@dataclass
class Result():
    w: float  # stationary wage
    v: Array  # incumbent value
    x: float  # exit threshold
    X: Array  # exit choice
    mu: Array  # stationary distribution over firm size
    m: float  # entrant mass
    n_vals: Array  # employment grid in steady state
    f_vals: Array  # output grid in steady state

    # primitives
    theta: float
    s_vals: Array  # state grid
    F: Array
    nu: Array
    ce: float
    cf: float
    a: float
    rho: float
    sigma: float
    G_mu: float
    G_sigma: float
    eta: float
    delta: float
    vx: float
    tau_l: float
    gamma_l: float
    kappa: float

    # mode
    equilibrium: str
    cf_in_labor: int

    def __post_init__(self, inherit=False):

        # calculate statistics
        self.aggregate_firm_mass = np.sum(self.mu)

        self.w_vals = self.w * self.tau_l * (self.s_vals**self.gamma_l)
        p_temp = self.w_vals if self.cf_in_labor else 1

        self.mu_pmf = self.mu / self.aggregate_firm_mass
        self.n_vals_plus_cf = self.n_vals + self.cf

        self.aggregate_employment_production = np.sum(self.mu * self.n_vals)
        self.aggregate_employment_production_entrant = np.sum(self.m * self.nu * self.n_vals)
        if self.cf_in_labor:
            self.aggregate_employment_overhead = self.cf * self.aggregate_firm_mass
            self.aggregate_employment_include_cf = np.sum(self.mu * self.n_vals_plus_cf)
            self.aggregate_employment_overhead_entrant = self.cf * self.m
            self.aggregate_employment_include_cf_entrant = np.sum(
                self.m * self.nu * self.n_vals_plus_cf)
        else:
            self.aggregate_employment_overhead = None
            self.aggregate_employment_include_cf = None
            self.aggregate_employment_overhead_entrant = None
            self.aggregate_employment_include_cf_entrant = None

        self.aggregate_output = np.sum(self.mu * self.f_vals)
        self.aggregate_profit = self.aggregate_output - np.sum(self.w_vals * self.n_vals * self.mu
                                                               ) - np.sum(p_temp * self.cf * self.mu)  # - np.sum(self.ce * self.nu)
        self.aggregate_productivity = np.sum(self.mu_pmf * self.s_vals)
        self.aggregate_productivity_ = self.aggregate_output / (self.aggregate_employment_production ** self.theta)
        self.aggregate_valuation = np.sum(self.mu_pmf * self.v)

        self.average_output = self.aggregate_output / self.aggregate_firm_mass
        self.average_profit = self.aggregate_profit / self.aggregate_firm_mass
        self.average_productivity = self.aggregate_productivity / self.aggregate_firm_mass
        self.average_valuation = self.aggregate_valuation / self.aggregate_firm_mass

        # in BGP entry rate depends on the denominator be either this year mass or last year mass, in later case should * (1 + self.eta)
        self.entry_rate = self.m / self.aggregate_firm_mass * 100 * (1 + self.eta)
        self.exit_rate_no_delta = np.sum(self.X * self.mu_pmf) * 100
        self.exit_rate = self.exit_rate_no_delta + (100 - self.exit_rate_no_delta) * self.delta
        self.gross_turnover_rate = self.entry_rate + self.exit_rate

        self.average_firm_size_prod = self.aggregate_employment_production / self.aggregate_firm_mass
        self.average_entrant_size_prod = np.sum(self.nu * self.n_vals)
        temp_pdf = self.nu * (1-self.X)
        entrant_survivor_pdf = temp_pdf / temp_pdf.sum()
        self.average_entrant_survivor_size_prod = np.sum(entrant_survivor_pdf * self.n_vals)
        self.average_exitor_size_prod = np.sum(self.mu * self.X * self.n_vals) / np.sum(self.mu * self.X)

        if self.cf_in_labor:
            self.average_firm_size_include_cf = self.aggregate_employment_include_cf / self.aggregate_firm_mass
            self.average_entrant_size_include_cf = np.sum(self.nu * self.n_vals_plus_cf)
            self.average_entrant_survivor_size_include_cf = np.sum(entrant_survivor_pdf * self.n_vals_plus_cf)
            self.average_exitor_size_include_cf = np.sum(self.mu * self.X * self.n_vals_plus_cf
                                                         ) / np.sum(self.mu * self.X)
        else:
            self.average_firm_size_include_cf = None
            self.average_entrant_size_include_cf = None
            self.average_entrant_survivor_size_include_cf = None
            self.average_exitor_size_include_cf = None

        # in case of HR1993 with sxn 2-D states
        self.x_mean = np.mean(self.x)

        # calculate growth rate
        self.lifecycle_survival_rate_10_year, self.lifecycle_growth_rate_10_year = self.calculate_survival_stat(age=10)
        self.lifecycle_survival_rate_20_year, self.lifecycle_growth_rate_20_year = self.calculate_survival_stat(age=20)

        # gather statistics
        if not inherit:
            self.stat = self._stat()
            self.stat_size_dist = self._stat_size_dist()

    def check_valid(self):
        ...

    def calculate_cohort_conditional_pdf(self, age):
        P_x = (self.F * (1 - self.X).reshape(len(self.X), 1)).T * (1 - self.delta)
        conditional_pdf = np.linalg.matrix_power(P_x, age-1) @ self.nu
        return conditional_pdf

    def calculate_survival_stat(self, age=10):
        conditional_pdf = self.calculate_cohort_conditional_pdf(age)
        survival_rate = np.sum(conditional_pdf)
        if self.cf_in_labor:
            life_growth_rate = np.sum(
                conditional_pdf / survival_rate * self.n_vals_plus_cf) / self.average_entrant_size_include_cf
        else:
            life_growth_rate = np.sum(conditional_pdf / survival_rate * self.n_vals) / self.average_entrant_size_prod
        life_growth_rate = life_growth_rate - 1
        return survival_rate*100, life_growth_rate*100

    def _stat_base(self):
        df = pd.Series({
            'equilibrium': self.equilibrium,
            'wage': self.w,
            'x (mean if HR)': self.x_mean,
            'entry_rate': self.entry_rate,
            'exit_rate': self.exit_rate,
            'exit_rate (minus exogenous)': self.exit_rate_no_delta,
            'entry mass': self.m,
            'aggregate_firm_mass': self.aggregate_firm_mass,
            'aggregate_employment_production': self.aggregate_employment_production,
            'aggregate_employment_overhead': self.aggregate_employment_overhead,
            'aggregate_employment_include_cf': self.aggregate_employment_include_cf,
            'aggregate_employment_production_entrant': self.aggregate_employment_production_entrant,
            'aggregate_employment_overhead_entrant': self.aggregate_employment_overhead_entrant,
            'aggregate_employment_include_cf_entrant': self.aggregate_employment_include_cf_entrant,
            'aggregate_output': self.aggregate_output,
            'aggregate_profit': self.aggregate_profit,
            'aggregate_productivity': self.aggregate_productivity,
            'aggregate_productivity (Y/L^θ)': self.aggregate_productivity_,
            'aggregate_valuation': self.aggregate_valuation,
            'average_output': self.average_output,
            'average_profit': self.average_profit,
            'average_productivity': self.average_productivity,
            'average_valuation': self.average_valuation,
            'average_firm_size_prod': self.average_firm_size_prod,
            'average_entrant_size_prod': self.average_entrant_size_prod,
            'average_entrant_survivor_size_prod': self.average_entrant_survivor_size_prod,
            'average_exitor_size_prod': self.average_exitor_size_prod,
            'average_firm_size_include_cf': self.average_firm_size_include_cf,
            'average_entrant_size_include_cf': self.average_entrant_size_include_cf,
            'average_entrant_survivor_size_include_cf': self.average_entrant_survivor_size_include_cf,
            'average_exitor_size_include_cf': self.average_exitor_size_include_cf,
            'lifecycle_growth_rate_10_year': self.lifecycle_growth_rate_10_year,
            'lifecycle_survival_rate_10_year': self.lifecycle_survival_rate_10_year,
            'lifecycle_growth_rate_20_year': self.lifecycle_growth_rate_20_year,
            'lifecycle_survival_rate_20_year': self.lifecycle_survival_rate_20_year,

        })
        return df

    def _stat(self):
        df = self._stat_base()
        return df

    def _stat_size_dist(self,):

        n_threshold = [10, 30, 100, ]  # use 9,29,99?? // alternative: 5, 20, 50, 300

        n_at = self.n_vals.searchsorted(n_threshold)
        dist_num = [np.sum(g) * 100 for g in np.split(self.mu_pmf, n_at)]
        dist_employ = [np.sum(g) * 100 / self.aggregate_employment_production for g in np.split(
            self.mu * self.n_vals, n_at)]
        dist_num_entrant = [np.sum(g) * 100 for g in np.split(self.nu, n_at)]
        dist_employ_entrant = [np.sum(g) * 100 / self.aggregate_employment_production_entrant
                               for g in np.split(self.m * self.nu * self.n_vals, n_at)]

        if self.cf_in_labor:
            n_at_include_cf = (self.n_vals + self.cf).searchsorted(n_threshold)
            dist_num_include_cf = [np.sum(g) * 100 for g in np.split(self.mu_pmf, n_at_include_cf)]
            dist_employ_include_cf = [np.sum(g) * 100 / self.aggregate_employment_include_cf
                                      for g in np.split(self.mu * self.n_vals_plus_cf, n_at_include_cf)]
            dist_num_include_cf_entrant = [np.sum(g) * 100 for g in np.split(self.nu, n_at_include_cf)]
            dist_employ_include_cf_entrant = [
                np.sum(g) *100 / self.aggregate_employment_include_cf_entrant
                for g in np.split(self.m * self.nu * self.n_vals_plus_cf, n_at_include_cf)]
        else:
            dist_num_include_cf = None
            dist_employ_include_cf = None
            dist_num_include_cf_entrant = None
            dist_employ_include_cf_entrant = None

        size_col = [str(a)+'~'+str(b) for a, b in zip(['']+n_threshold, n_threshold+[''])]
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

    def plot_distribution(self, n=1):
        fig, ax = plt.subplots()
        ax.plot(self.mu)
        ax.axvline(np.searchsorted(self.n_vals, n), color="b", label=f"n={n}")
        x_index = np.searchsorted(self.s_vals, self.x)
        ax.axvline(x_index, color='k', linestyle='--', alpha=0.7, label=f"x (n={self.n_vals[x_index]})")
        ax.legend()
        return fig, ax


def main():
    # use calibrated parameters to form and calculate
    test = Hopenhayn(
        # parameters to calibration (follow HNS 2020)
        ce=8e-5,  # match entry rate
        cf=3.7,  # match average size
        a=-.028,  # match ?
        rho=.974,  # match growth rate
        sigma=0.075**.5,  # match exit rate
        G_mu=-8,  # match average entry size
        G_sigma=3**.5,  # match concentration of entrants ?

        s_size=101,

        zeta=2,
    )
    res = test.solve_model()


if __name__ == "__main__":
    main()
