"""
This code produces table for counterfactural trials of parameter changes on distribution of entry productivity and its evolution
"""

import pandas as pd

from calibration import read_result, _solve_model
from counterfactural_parameter import counterfactural_para_change


pd.set_option('max_colwidth', None)

output_path = "../Tables/"


def table_counterfactural(res_all, col_names):
    index = [
        r"$\eta$, \%",
        r'$\mu_G$',
        r'$\sigma_G$',
        "$w^*$",
        r"$\bar{s}^*$",
        "Entry Rate, \%",
        "Exit Rate, \%",
        "Avg. Entry Size",
        "Avg. Entry Size (post-exit)",
        "Avg. Est. Size",
        "LifeCycle Growth Rate 10y, \%",
        "LifeCycle Growth Rate 20y, \%",
        # "LifeCycle Survival Rate 10y",
        # "LifeCycle Survival Rate 20y",
    ]
    df = pd.DataFrame()
    for res in res_all:
        ds = pd.Series([
            res.eta * 100,
            res.G_mu,
            res.G_sigma,
            res.w,
            res.x,
            res.entry_rate,
            res.exit_rate,
            res.average_entrant_size_include_cf,
            res.average_entrant_survivor_size_include_cf,
            res.average_firm_size_include_cf,
            res.lifecycle_growth_rate_10_year,
            res.lifecycle_growth_rate_20_year,
            # res.lifecycle_survival_rate_10_year,
            # res.lifecycle_survival_rate_20_year,
        ])
        df = pd.concat([df, ds], axis=1).fillna("-")
    df = df.applymap(lambda x: '{:.2f}'.format(x) if type(x) == float else x)
    df.index = index
    df.columns = col_names
    df.to_latex(output_path+'counterfactural_heterogeneity.tex',
                index=True,
                column_format='l'+'c'*len(res_all),
                escape=False,
                multicolumn=True,
                multicolumn_format='c'
                )


def counterfactural_heterogeneity():
    x = read_result()[:-1]
    res_bm = _solve_model(x)

    G_mu_ratio = [0.8, 0.6,] # [0.9, 0.8,]
    res_trials_G_mu = [counterfactural_para_change(para_index=2, para_ratio=r) for r in G_mu_ratio]

    G_sigma_ratio = [0.8, 0.6,]
    res_trials_G_sigma = [counterfactural_para_change(para_index=3, para_ratio=r) for r in G_sigma_ratio]

    res_all = [res_bm] + res_trials_G_mu + res_trials_G_sigma
    mode_names = ["Benchmark"] + ["Location"]*len(G_mu_ratio) + ["Scale"]*len(G_sigma_ratio) # "Shift", "Scale"
    para_names = ["-"] + [r'$\mu_G\times$'+f'{r}' for r in G_mu_ratio] + [r'$\sigma_G\times$'+f'{r}' for r in G_sigma_ratio]
    res_names = pd.MultiIndex.from_tuples(list(zip(mode_names, para_names)))
    return res_all, res_names


def main():

    res_all, res_names = counterfactural_heterogeneity()
    table_counterfactural(res_all, col_names=res_names)


if __name__ == "__main__":
    main()
