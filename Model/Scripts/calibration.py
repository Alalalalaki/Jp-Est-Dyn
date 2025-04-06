"""
This code calibrate the parameters to data moments
"""


import numpy as np
import scipy as sp
from datetime import datetime


from hopenhayn import Hopenhayn
from moments import Moments


output_path_gs = "../Output/global_search/"
output_path_ls = "../Output/local_search/"


class _data_moments:
    """
    This data_moments class produce either period average moments or moment of a specific year
    avg_years
        - if False, then use moments at "year"
        - "full", i.e. (1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006)
        - "69-81", i.e. (1969, 1972, 1975, 1981)
    """

    def __init__(self, year=1969, avg_years="full", use_avg=True, growth_years=(1969, 1972, 1975, 1981,), drop_moments=["growth_26"]):
        self.year = year
        self.avg_years = (1969, 1972, 1975, 1981) if avg_years == "69-81" else avg_years
        self.use_avg = use_avg
        self.growth_years = growth_years
        self.drop_moments = drop_moments
        self._moment = Moments(year=self.year, avg_years=self.avg_years)

        # Default moment configuration if none provided
        moment_config = [
            ("entry", lambda m: m.entry_rate),
            ("avgsize", lambda m: m.avgsize),
            ("e_avgsize", lambda m: m.entrant_avgsize),
            ("growth_10", lambda m, y=growth_years: self._moment.get_avg_life_growth(age=(1, 10), years=y)),
            ("growth_20", lambda m, y=growth_years: self._moment.get_avg_life_growth(age=(1, 20), years=y)),
            ("growth_26", lambda m, y=growth_years: self._moment.get_avg_life_growth(age=(1, 26), years=y)),
            ("num_share_1_9", lambda m: m.num_share_1_9 / 10),
            ("emp_share_1_9", lambda m: m.emp_share_1_9 / 10),
            ("e_num_share_1_9", lambda m: m.entrant_num_share_1_9 / 10),
            ("e_emp_share_1_9", lambda m: m.entrant_emp_share_1_9 / 10),
        ]
        self.moment_config = [(n,f) for n,f in moment_config if n not in drop_moments]
        self.moment_names = ", ".join(name for name, _ in self.moment_config)

        if self.use_avg:
            self.info_ = f"avgmoments (avg_years: {avg_years}; growth: {growth_years}): "
            m = self._moment.avgmoment
        else:
            self.info_ = f"avgmoments (year: {year}; growth: {growth_years}): "
            m = self._moment.moment

        self.info = self.info_ + self.moment_names
        self.moments = np.array([func(m) for _, func in self.moment_config])
        self.info_full = self.info_ + "; ".join([f"{n}:{v}" for n, v in zip(self.moment_names.split(","), self.moments)])


def _model_moments(res, drop_moments=["growth_26"]):
    model_moments = [
            ("entry", res.stat.entry_rate),
            ("avgsize", res.stat.average_firm_size_include_cf),
            ("e_avgsize", res.stat.average_entrant_size_include_cf),
            ("growth_10", res.calculate_survival_stat(age=10)[1]),
            ("growth_20", res.calculate_survival_stat(age=20)[1]),
            ("growth_26", res.calculate_survival_stat(age=26)[1]),
            ("num_share_1_9", res.stat_size_dist.loc["num_include_cf", "~10"] / 10),
            ("emp_share_1_9", res.stat_size_dist.loc["emp_include_cf", "~10"] / 10),
            # ("emp_share_100_", res.stat_size_dist.loc["emp_include_cf", "100~"] / 10),
            ("e_num_share_1_9", res.stat_size_dist.loc["num_include_cf_entrant", "~10"] / 10),
            ("e_emp_share_1_9", res.stat_size_dist.loc["emp_include_cf_entrant", "~10"] / 10),
        ]
    model_moments = np.array([m for n,m in model_moments if n not in drop_moments])
    return model_moments


def _solve_model(x, model_params=None
                 ):
    ce, cf, G_mu, G_sigma, a, rho, sigma = x
    # ce, cf, G_mu, G_sigma, a, rho, sigma, delta = x  # @ calibrate additional delta
    # ce, cf, G_mu, G_sigma, a, rho, sigma, gamma_l = x  # @ calibrate additional gamma

    # Default parameters
    default_params = {
        'eta': 0.02, # setting the labor growth rate is somehow arbitrary
        'delta': 0, # if 0 no exogenous exit
        # 'vx': 0, # exit value
        'tau_l': 1,
        'gamma_l': 0
    }
    if model_params is not None:
        default_params.update(model_params)

    model = Hopenhayn(
        ce=ce,
        cf=cf,
        a=a,
        rho=rho,
        sigma=sigma,
        G_mu=G_mu,
        G_sigma=G_sigma,
        s_size=240,
        vx=0,
        A=0,
        **default_params,  # Unpack all model parameters
        equilibrium="BGP",
        cf_in_labor=1,
        w_solver="brentq",
        m_solver="newton",
        suppress_fail=True,
    )
    res = model.solve_model()
    return res


def _target_moments(x, data_moments, res_file_path, model_params=None, drop_moments=None):
    res = _solve_model(x, model_params)
    if res == None:
        # print(x, "Fail!")
        return 1e7
    model_moments = _model_moments(res, drop_moments)
    diff = model_moments - data_moments
    diff = diff / data_moments # normalize moment differences
    diff = diff @ diff
    # diff = np.sum(np.abs(diff)) # alternatively use linear sum of absolute diffs
    # print(x, diff)
    if res_file_path:
        append_file(res_file_path, f"\n{','.join(map(str, x))},{diff}")
    return diff


def append_file(file_path, message, ini=False):
    if ini:
        m = "w"
    else:
        m = "a"
    with open(file_path, m) as file:
        file.write(message)


def global_search_brute(data_moments, prange):
    print(f"global search brute - prange: {prange}")
    res_file_path = output_path_gs + "global_search_brute_" + datetime.now().strftime("%Y%m%d%H") + ".txt"
    append_file(res_file_path, f"Para Grids: {prange}\nMoments: {data_moments.info_full}", ini=True)

    res = sp.optimize.brute(_target_moments, prange,
                            args=(data_moments.moments, res_file_path),
                            finish=None,
                            workers=-1
                            )
    append_file(res_file_path, f"\n{','.join(map(str, res[0]))},{res[1]}")


def global_search_diffevo(data_moments, prange, strategy="randtobest1bin", model_params=None,):
    print(f"global search diffevo - prange: {prange}")
    start_time =  datetime.now().strftime("%Y%m%d%H")
    res_file_path = output_path_gs + "global_search_diffevo_" + start_time + ".txt"
    append_file(res_file_path, f"Para Grids: {prange}\nMoments: {data_moments.info_full}", ini=True)
    append_file(res_file_path, f"Additional model_params: {model_params}")

    res = sp.optimize.differential_evolution(_target_moments, prange,
                                             args=(data_moments.moments, res_file_path, model_params, data_moments.drop_moments),
                                             polish=False,
                                             strategy=strategy,
                                             #   disp=True,
                                             updating="deferred",
                                             workers=-1,
                                             )
    append_file(res_file_path, f"\n{','.join(map(str, res.x))},{res.fun}")
    return res.x, start_time


def local_search(x0, data_moments, prange=None, method="L-BFGS-B", maxiter=1e4, output_time=None, model_params=None,):
    print(f"local search - \n  method: {method} \n  Bound: {prange} \n  x0: {x0}")
    output_name = "local_search_" + output_time if output_time else "local_search_" + datetime.now().strftime("%Y%m%d%H")
    res_file_path = output_path_ls + output_name + ".txt"
    append_file(res_file_path, f"Moments: {data_moments.info}\nMethod: {method} Bound: {prange}\nx0: {x0}", ini=True)
    res = sp.optimize.minimize(
        _target_moments,
        x0=x0,
        args=(data_moments.moments, None, model_params, data_moments.drop_moments),
        tol=1e-5,
        # method=method,  # "Powell"
        bounds=prange,
        # options={"maxiter": maxiter},
    )
    if res.success:
        append_file(res_file_path, f"\n{','.join(map(str, res.x))},{res.fun}")
    else:
        print("Failed to converge locally!")
        append_file(res_file_path, "Failed to converge locally! Use the global search result!")
        append_file(res_file_path, f"\n{','.join(map(str, x0))},{_target_moments(x0, data_moments.moments, False)}")

def read_result(path=output_path_ls, name="benchmark", line=-1):
    with open(path+name+".txt") as f:
        last_line = f.readlines()[line]
    res = list(map(float, last_line.split(",")))
    return res


def main():
    data_moments = _data_moments(avg_years="full", drop_moments=[])  # @ avg_years = "full" or "69-81"
    print(data_moments.info_full)


    # global search - differential_evolution
    prange_coarse = ((1, 150), (0.5, 10), (-1, 3), (0.1, 1), (-0.2, 0.2), (0.91, 0.99), (0.05, 0.5))
    prange = ((1, 120), (0.5, 5), (-0.1, 2), (0.1, 0.8), (-0.2, 0.2), (0.92, 0.996), (0.1, 0.4),)
    # prange = ((1, 120), (0.5, 5), (-.1, 2.5), (0.1, 0.8), (-0.2, 0.2), (0.92, 0.98), (0.1, 0.4), (0, 0.03))  # @ calibrate additional delta
    # prange = ((1, 120), (0.5, 5), (-.1, 2.5), (0.1, 0.8), (-0.2, 0.2), (0.92, 0.98), (0.1, 0.4), (0, 0.2))  # @ calibrate additional gamma

    x0, start_time = global_search_diffevo(data_moments, prange, strategy="randtobest1bin")
    # use global search result to do local search
    local_search(x0=x0, data_moments=data_moments, prange=prange, output_time=start_time)
    # # for separate global search and local search
    # x0 = read_result(path=output_path_gs, name="global_search_diffevo_2024112108")[:-1]
    # local_search(x0=x0, data_moments=data_moments, prange=prange, output_time="2024112108")


    # 1969
    data_moments = _data_moments(year=1969, use_avg=False, growth_years=(1969, 1972))
    print(data_moments.info_full)
    x0, start_time = global_search_diffevo(data_moments, prange, strategy="randtobest1bin")
    local_search(x0=x0, data_moments=data_moments, prange=prange, output_time=start_time)


    # 2006
    data_moments = _data_moments(year=2006, use_avg=False, growth_years=(1981, 1986, 1991, 1996,),)
    print(data_moments.info_full)
    global_search_diffevo(data_moments, prange, strategy="randtobest1bin", model_params={"eta": 0.00})
    local_search(x0=x0, data_moments=data_moments, prange=prange, output_time=start_time, model_params={"eta": 0.00})

if __name__ == "__main__":
    main()
