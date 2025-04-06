"""
This code examine the counterfactural of labor growth
"""

import numpy as np
import pandas as pd
import math

from moments import Moments
from calibration import read_result, _solve_model


def _solve_evolution(mu_t0, L_s, res):

    P_x = (res.F * (1 - res.X).reshape(len(res.X), 1)).T
    mu_t1_incumbent = P_x @ mu_t0

    L_d_t1_incumbent = mu_t1_incumbent @ res.n_vals_plus_cf
    L_d_t1_entrant = L_s - L_d_t1_incumbent
    m_t1 = L_d_t1_entrant / res.average_entrant_size_include_cf

    mu_t1 = mu_t1_incumbent + m_t1 * res.nu
    return m_t1, mu_t1


def calculate_transition_path(labor_supply="employee_NALL", year_ini=1953, year_end=2006):
    """
    employee_NALL labor force data start at 1953 and end at 2018
    """

    x = read_result()[:-1]
    res = _solve_model(x)
    assert res.equilibrium == "BGP", "The model must be in BGP to calculate transitional path"

    moment = Moments()
    L_s_growth_rate = moment.LSgrowth[labor_supply].loc[year_ini+1:year_end].values/100 + 1
    # L_s_growth_rate = np.ones_like(L_s_growth_rate) * 1.02 # for test
    L_s_vals = np.cumprod(L_s_growth_rate)
    L_s_vals = np.r_[([1], L_s_vals)]  # add L_s = L_d = 1 in BGP at t=0
    T = len(L_s_vals)

    mu_path = list(np.empty(T))
    mu_path[0] = res.mu
    m_path = np.empty(T)
    m_path[0] = res.m

    for t in range(len(L_s_vals)-1):
        m_t1, mu_t1 = _solve_evolution(mu_path[t], L_s_vals[t+1], res=res)
        m_path[t+1] = m_t1
        mu_path[t+1] = mu_t1

    mass_path = np.array([np.sum(mu) for mu in mu_path])
    mu_pmf_path = [mu/mass for mu, mass in zip(mu_path, mass_path)]
    entry_rate_path = np.empty(T)
    entry_rate_path[0] = res.entry_rate
    entry_rate_path[1:] = m_path[1:] / mass_path[:-1] * 100
    # alternative entry rate calculation
    # entry_rate_path = m_path / mass_path * 100
    # assert math.isclose(entry_rate_path[0], res.entry_rate), "Entry rate calucation failed!"
    exit_rate_path = np.array([np.sum(res.X * mu_pmf) for mu_pmf in mu_pmf_path]) * 100
    exit_rate_path = exit_rate_path + (100 - exit_rate_path) * res.delta
    assert math.isclose(exit_rate_path[0], res.exit_rate), "Exit rate calucation failed!"
    avgsize_path = np.array([np.sum(mu_pmf * res.n_vals_plus_cf) for mu_pmf in mu_pmf_path])
    assert math.isclose(avgsize_path[0], res.average_firm_size_include_cf), "Average size calucation failed!"

    transition_path_stat = pd.DataFrame({
        "mass": mass_path,
        "entry_rate": entry_rate_path,
        "exit_rate": exit_rate_path,
        "avgsize": avgsize_path,
        labor_supply: moment.LSgrowth[labor_supply].loc[year_ini:year_end]
    }, index=range(year_ini, year_end+1))

    return transition_path_stat, mu_path


def main():
    transition_path_stat, _ = calculate_transition_path(labor_supply="employee_NALL", year_end=2006)
    # print(transition_path_stat)
    print(transition_path_stat.loc[[1960, 1969, 1970, 2001, 2002, 2004, 2006]])
    transition_path_stat, _ = calculate_transition_path(labor_supply="employee_NALL_hp", year_end=2006)
    print(transition_path_stat.loc[[1960, 1969, 1970, 2001, 2002, 2004, 2006]])


if __name__ == "__main__":
    main()
