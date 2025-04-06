"""
This code produces table for counterfactural trials of adjustment costs
"""

import pandas as pd

from HR import HR
from calibration import read_result, _solve_model


pd.set_option('max_colwidth', None)

output_path = "../Tables/"


def table_counterfactural(res_all, col_names):
    index = [
        "$w^*$",
        r"$\bar{s}^*$ (mean)",
        "Entry Rate, \%",
        "Exit Rate, \%",
        "Avg. Entry Size",
        # "Avg. Entry Size (post-exit)",
        "Avg. Est. Size",
        "LifeCycle Growth Rate 10y, \%",
        "LifeCycle Growth Rate 20y, \%",
        # "LifeCycle Survival Rate 10y",
        # "LifeCycle Survival Rate 20y",
        "Job Turnover Rate, \%"
    ]
    df = pd.DataFrame()
    for res in res_all:
        ds = pd.Series([
            res.w,
            res.x_mean,
            res.entry_rate,
            res.exit_rate,
            res.average_entrant_size_include_cf,
            # res.average_entrant_survivor_size_include_cf,
            res.average_firm_size_include_cf,
            res.lifecycle_growth_rate_10_year,
            res.lifecycle_growth_rate_20_year,
            # res.lifecycle_survival_rate_10_year,
            # res.lifecycle_survival_rate_20_year,
            res.job_turnover_rate
        ])
        df = pd.concat([df, ds], axis=1).fillna("-")
    df = df.applymap(lambda x: '{:.2f}'.format(x) if type(x) == float else x)
    df.index = index
    df.columns = col_names
    df.to_latex(output_path+'counterfactural_adjust.tex',
                index=True,
                column_format='l'+'c'*len(res_all),
                escape=False,
                multicolumn=True,
                multicolumn_format='c'
                )


def _solove_model_HR(x,
                     eta=0.02, delta=0, vx=0, tau_l=1, gamma_l=0,
                     tau_adj=0, labor_adj="Firing"
                     ):
    # same function as the one in calibration but replace Hopenhyan with HR
    ce, cf, G_mu, G_sigma, a, rho, sigma = x
    model = HR(
        ce=ce,
        cf=cf,
        a=a,
        rho=rho,
        sigma=sigma,
        G_mu=G_mu,
        G_sigma=G_sigma,
        s_size=240,
        A=0,
        eta=eta,  # long-run labor growth rate
        delta=delta,  # if 0 no exogenous exit
        vx=vx,  # exit value
        tau_l=tau_l,
        gamma_l=gamma_l,
        equilibrium="BGP",
        cf_in_labor=1,
        w_solver="brentq",
        m_solver="newton",
        suppress_fail=True,
        # HR para
        n_size=101,
        n_max=5000,
        tau_adj=tau_adj,
        labor_adj=labor_adj,
    )
    res = model.solve_model()
    return res


def counterfactural_adjustment_cost():
    x = read_result()[:-1]
    res_bm = _solove_model_HR(x)

    tau_adjs = [0.25, 0.5, ]
    res_trials_f = [_solove_model_HR(x, tau_adj=t) for t in tau_adjs]
    # res_trials_h = [_solove_model_HR(x, tau_adj=t, labor_adj="Hiring") for t in tau_adjs]
    res_trials_a = [_solove_model_HR(x, tau_adj=t, labor_adj="Full") for t in tau_adjs]

    res_all = ([res_bm] + res_trials_f
            #    + res_trials_h
               + res_trials_a)
    mode_names = ["Benchmark"] + [r.labor_adj for r in res_all[1:]]
    mode_dict = {"Firing": "Firing Cost", "Hiring": "Hiring Cost", "Full": "Firing + Hiring Cost"}
    mode_names = [mode_dict.get(item, item) for item in mode_names]
    para_names = [r'$\tau^a$='+f'{r.tau_adj:.2f}' for r in res_all]
    res_names = pd.MultiIndex.from_tuples(list(zip(mode_names, para_names)))
    return res_all, res_names


def main():

    res_all, res_names = counterfactural_adjustment_cost()
    table_counterfactural(res_all, col_names=res_names)


if __name__ == "__main__":
    main()
