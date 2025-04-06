"""
This code produces table for counterfactural trials of of parameter changes on size-related labor tax
"""

import pandas as pd

from calibration import read_result, _solve_model
from counterfactural_parameter import counterfactural_gamma_l


pd.set_option('max_colwidth', None)

output_path = "../Tables/"


def table_counterfactural(res_all, col_names):
    index = [
        "$w^*$",
        "$w$ min",
        "$w$ max",
        "$w$ max / $w$ min",
        "$w$ (mean)",
        "$w$ (entry mean)",
        r"$\bar{s}^*$",
        "Entry Rate, \%",
        "Exit Rate, \%",
        "Avg. Entry Size",
        # "Avg. Entry Size (post-exit)",
        "Avg. Est. Size",
        "LifeCycle Growth Rate 10y, \%",
        "LifeCycle Growth Rate 20y, \%",
        # "LifeCycle Survival Rate 10y",
        # "LifeCycle Survival Rate 20y",
    ]
    df = pd.DataFrame()
    for res in res_all:
        ds = pd.Series([
            res.w,
            res.w_vals[0],
            res.w_vals[-1],
            res.w_vals[-1] / res.w_vals[0],
            res.w_vals @ res.mu_pmf,
            res.w_vals @ res.nu,
            res.x,
            res.entry_rate,
            res.exit_rate,
            res.average_entrant_size_include_cf,
            # res.average_entrant_survivor_size_include_cf,
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
    df.to_latex(output_path+'counterfactural_distortion.tex',
                index=True,
                column_format='l'+'c'*len(res_all),
                escape=False
                )


def counterfactural_labor_distortion():
    x = read_result()[:-1]
    res_bm = _solve_model(x)

    wage_diff_ratios = [1.25, 1.5, 2, 3]
    res_trials = [counterfactural_gamma_l(w_diff_ratio_target=r) for r in wage_diff_ratios]

    res_all = [res_bm] + res_trials
    res_names = ["Benchmark"] + [r'$\gamma$='+f'{r.gamma_l:.2f}' for r in res_trials]
    return res_all, res_names


def main():

    res_all, res_names = counterfactural_labor_distortion()
    table_counterfactural(res_all, col_names=res_names)


if __name__ == "__main__":
    main()
