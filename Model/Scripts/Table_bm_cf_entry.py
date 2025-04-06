"""
This code produces table for counterfactural trials of parameter changes on entry rate
"""

import pandas as pd

from calibration import read_result, _solve_model
from counterfactural_parameter import counterfactural_entry_decline, counterfactural_entry_decline_vx, counterfactural_entry_decline_eta

pd.set_option('max_colwidth', None)

output_path = "../Tables/"


def table_counterfactural_para(res_all, col_names, table_name):
    index = [
        r"$\eta$, \%",
        "$c_e$",
        "$V^x$", # (in unit of $w$)
        "$c_f$",
        "$w^*$",
        r"$\bar{s}^*$",
        r"Entry Rate, \%",
        r"Exit Rate, \%",
        "Avg. Entry Size",
        "Avg. Entry Size (post-exit)",
        "Avg. Est. Size",
        r"LifeCycle Growth Rate 10y, \%",
        r"LifeCycle Growth Rate 20y, \%",
        # "LifeCycle Survival Rate 10y",
        # "LifeCycle Survival Rate 20y",
    ]
    res_bm = res_all[0]
    df = pd.DataFrame()
    for i, res in enumerate(res_all):
        eta = res.eta * 100 if (i == 0) or (res.eta-res_bm.eta != 0) else None
        ce = res.ce if (i == 0) or (res.ce-res_bm.ce != 0) else None
        cf = res.cf if (i == 0) or (res.cf-res_bm.cf != 0) else None
        vx = res.vx if (i == 0) or (res.vx-res_bm.vx != 0) else None  # / res.w if in terms of wage

        ds = pd.Series([
            eta,
            ce,
            vx,
            cf,
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
    df.to_latex(output_path+f'counterfactural_entry_{table_name}.tex',
                index=True,
                column_format='l'+'c'*len(res_all),
                escape=False
                )


def counterfactural_entry_decline_eta_change(eta=0):
    x = read_result()[:-1]
    res_bm = _solve_model(x)
    # counterfactural result of labor force growth change
    res_lf = _solve_model(x, eta=eta)

    res_ce = counterfactural_entry_decline(entry_target=res_lf.entry_rate, para_index=0)
    res_cf = counterfactural_entry_decline(entry_target=res_lf.entry_rate, para_index=1)
    res_vx = counterfactural_entry_decline_vx(entry_target=res_lf.entry_rate)

    res_all = [res_bm, res_lf, res_ce, res_vx, res_cf]
    res_names = ["Benchmark", "Labor Growth", "Entry Cost", "Exit Value", "Fixed Cost"]
    return res_all, res_names


def counterfactural_entry_decline_entry_change(entry_deline=1, combined=True, eta=None):
    x = read_result()[:-1]
    res_bm = _solve_model(x)
    if combined:
        res_lf = _solve_model(x, eta=eta)
        entry_target = res_lf.entry_rate - entry_deline
    else:
        # counterfactural result of a entry rate decline
        entry_target = res_bm.entry_rate - entry_deline
        res_lf = counterfactural_entry_decline_eta(entry_target=entry_target)

    res_ce = counterfactural_entry_decline(entry_target=entry_target, para_index=0, eta=eta)
    res_cf = counterfactural_entry_decline(entry_target=entry_target, para_index=1, eta=eta)
    res_vx = counterfactural_entry_decline_vx(entry_target=entry_target, eta=eta)

    res_all = [res_bm, res_lf, res_ce, res_vx, res_cf]
    res_names = ["Benchmark", "Labor Growth", "Entry Cost", "Exit Value", "Fixed Cost"]
    return res_all, res_names


def main():

    res_all, res_names = counterfactural_entry_decline_eta_change(eta=0)
    table_counterfactural_para(res_all, col_names=res_names, table_name="eta_change")

    res_all, res_names = counterfactural_entry_decline_entry_change(combined=False)
    table_counterfactural_para(res_all, col_names=res_names, table_name="entry_change")

    res_all, res_names = counterfactural_entry_decline_entry_change(combined=True, eta=0)
    table_counterfactural_para(res_all, col_names=res_names, table_name="combined_change")

if __name__ == "__main__":
    main()
