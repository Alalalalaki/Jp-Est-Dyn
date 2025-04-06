"""
This code creates the table for calibration method and results
"""

import pandas as pd

from calibration import output_path_ls, read_result, output_path_gs, _data_moments, _solve_model, _model_moments

pd.set_option('max_colwidth', None)

output_path = "../Tables/"


def table_calibration_parameter(x, suffix=""):
    col = ["Parameters", "Values", "Definition", "Calibration"]
    rows = [
        [r"$\beta$", "0.96", "Discounter factor", "Assigned"],
        [r"$\theta$", "0.64", "Labor share (\"span of control\")", "Assigned"],
        [r"$\eta$", "0.02", "Average labor force growth rate", "Assigned"],
        [r"$c_e$", x[0], "Entry cost (in unit of product)", "Jointly Calibrated"],
        [r"$c_f$", x[1], "Operation cost (in unit of labor)", "Jointly Calibrated"],
        [r"$a$", x[4], "Drift in AR(1)", "Jointly Calibrated"],
        [r"$\rho$", x[5], "Persistence in AR(1)", "Jointly Calibrated"],
        [r"$\sigma_{\varepsilon}$", x[6], "Std. of AR(1) shocks", "Jointly Calibrated"],
        [r"$\mu_{G}$", x[2], "Mean of entrant productivity (log normal)", "Jointly Calibrated"],
        [r"$\sigma_{G}$", x[3], "Std. of entrant productivity (log normal)", "Jointly Calibrated"],
    ]
    df = pd.DataFrame(rows, columns=col)
    df.Values = df.Values.map(lambda x: '{:.3f}'.format(x) if type(x) == float else x)
    df.to_latex(output_path+f'calibration_parameter{suffix}.tex',
                index=False,
                column_format='cclc',
                escape=False
                )


def table_calibration_moment(x, dm, suffix="", model_params=None):
    """
    Caution: for untargeted moments, must make sure to use the same data_moment
    """

    data_moments = dm.moments
    dmr = dm._moment.avgmoment if dm.use_avg else dm._moment.moment
    res = _solve_model(x, model_params)
    model_moments = _model_moments(res, dm.drop_moments)
    rsd = res.stat_size_dist

    h = r"\hspace{10mm}"

    col = ["Moments", "Data", "Model", ""]
    rows = [
        [r"Entry rate, \%", data_moments[0], model_moments[0], "Target"],
        # [r"Exit rate, \%", dmr.exit_rate, res.exit_rate, ""],
        [r"Exit rate, \%", data_moments[0]-res.eta*100, res.exit_rate, ""],
        ["Average establishment size", data_moments[1], model_moments[1], "Target"],
        ["Average entrant size", data_moments[2], model_moments[2], "Target"],
        [r"Average life-cycle growth rate, \%", "", "", ""],
        ["(conditional on survival)", "", "", ""],
        [h+"Age 1-10", data_moments[3], model_moments[3], "Target"],
        [h+"Age 1-20", data_moments[4], model_moments[4], "Target"],
        [h+"Age 1-26", data_moments[5], model_moments[5], ""],
        [r"Number share by size, \%", "", "", ""],
        [h+"Employment 1-9", dmr.num_share_1_9, rsd.loc["num_include_cf", "~10"], "Target"],
        [h+"Employment 10-29", dmr.num_share_10_29, rsd.loc["num_include_cf", "10~30"], ""],
        [h+"Employment 30-99", dmr.num_share_30_99, rsd.loc["num_include_cf", "30~100"], ""],
        [h+"Employment 100+", dmr.num_share_100_, rsd.loc["num_include_cf", "100~"], ""],
        [r"Employment share by size, \%", "", "", ""],
        [h+"Employment 1-9", dmr.emp_share_1_9, rsd.loc["emp_include_cf", "~10"], "Target"],
        [h+"Employment 10-29", dmr.emp_share_10_29, rsd.loc["emp_include_cf", "10~30"], ""],
        [h+"Employment 30-99", dmr.emp_share_30_99, rsd.loc["emp_include_cf", "30~100"], ""],
        [h+"Employment 100+", dmr.emp_share_100_, rsd.loc["emp_include_cf", "100~"], ""],
        [r"Number share of entrants by size, \%", "", "", ""],
        [h+"Employment 1-9", dmr.entrant_num_share_1_9, rsd.loc["num_include_cf_entrant", "~10"], "Target"],
        [h+"Employment 10-29", dmr.entrant_num_share_10_29, rsd.loc["num_include_cf_entrant", "10~30"], ""],
        [h+"Employment 30-99", dmr.entrant_num_share_30_99, rsd.loc["num_include_cf_entrant", "30~100"], ""],
        [h+"Employment 100+", dmr.entrant_num_share_100_, rsd.loc["num_include_cf_entrant", "100~"], ""],
        [r"Employment share of entrants by size, \%", "", "", ""],
        [h+"Employment 1-9", dmr.entrant_emp_share_1_9, rsd.loc["emp_include_cf_entrant","~10"], "Target"],
        [h+"Employment 10-29", dmr.entrant_emp_share_10_29, rsd.loc["emp_include_cf_entrant", "10~30"], ""],
        [h+"Employment 30-99", dmr.entrant_emp_share_30_99, rsd.loc["emp_include_cf_entrant", "30~100"], ""],
        [h+"Employment 100+", dmr.entrant_emp_share_100_, rsd.loc["emp_include_cf_entrant", "100~"], ""],
    ]
    df = pd.DataFrame(rows, columns=col)
    df = df.apply(lambda x: pd.to_numeric(x, errors="ignore")).fillna(" ")
    df = df.applymap(lambda x: '{:.2f}'.format(x) if type(x) == float else x)
    df.to_latex(output_path+f'calibration_moment{suffix}.tex',
                index=False,
                column_format='lccc',
                escape=False
                )


def main():
    # x = read_result()[:-1]  # default use "benchmark" in localsearch
    # dm = _data_moments()

    # table_calibration_parameter(x, dm)
    # table_calibration_moment(x, dm)

    for y, year, growth_years, model_params in zip(["69", "06"], [1969,2006], [(1969, 1972),(1981, 1986, 1991, 1996,)], [None, {"eta": 0.00}]):
        x = read_result(name=f"benchmark_{y}")[:-1]  # default use "benchmark" in localsearch
        dm = _data_moments(year=year, use_avg=False, growth_years=growth_years, drop_moments=[])

        table_calibration_parameter(x, suffix=f"_{y}")
        table_calibration_moment(x, dm, suffix=f"_{y}", model_params=model_params)

if __name__ == "__main__":
    main()
