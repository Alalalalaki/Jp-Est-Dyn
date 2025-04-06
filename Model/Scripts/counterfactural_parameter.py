"""
This code produces counterfactural trials of changes on parameter
"""

import scipy as sp

from moments import Moments
from calibration import read_result, _solve_model


def counterfactural_entry_decline(entry_target=None, para_index=0, max_iter=200, search_scrope=4,
                                  eta=None
                                  ):
    x = read_result()[:-1]
    p_init = x[para_index]

    def diff_func(p, para_index, entry_target, x):
        x[para_index] = p
        if eta is None:
            res = _solve_model(x)
        else:
            res = _solve_model(x, eta=eta)
        diff = res.entry_rate - entry_target
        return diff

    p, res = sp.optimize.brentq(
        diff_func, p_init*(1/search_scrope), p_init*search_scrope,
        args=(para_index, entry_target, x),
        xtol=0.001,
        maxiter=max_iter, full_output=True
    )
    assert res.converged, "Failed to converge in parameter finding!"

    x[para_index] = p
    if eta is None:
        new_res = _solve_model(x)
    else:
        new_res = _solve_model(x, eta=eta)
    return new_res


def counterfactural_entry_decline_vx(entry_target=None, max_iter=200, search_scrope=(-40, 0),
                                     eta=None
                                     ):
    # similar to counterfactural_entry_decline but search for vx
    x = read_result()[:-1]

    def diff_func(vx, entry_target, x):
        if eta is None:
            res = _solve_model(x, vx=vx)
        else:
            res = _solve_model(x, eta=eta, vx=vx)
        diff = res.entry_rate - entry_target
        return diff

    vx, res = sp.optimize.brentq(
        diff_func, search_scrope[0], search_scrope[1],
        args=(entry_target, x),
        xtol=0.001,
        maxiter=max_iter, full_output=True
    )
    assert res.converged, "Failed to converge in parameter finding!"

    if eta is None:
        new_res = _solve_model(x, vx=vx)
    else:
        new_res = _solve_model(x, eta=eta, vx=vx)
    return new_res


def counterfactural_entry_decline_eta(entry_target=None, max_iter=200, search_scrope=(0, .02)):
    # similar to counterfactural_entry_decline but search for eta
    x = read_result()[:-1]

    def diff_func(eta, entry_target, x):
        res = _solve_model(x, eta=eta)
        diff = res.entry_rate - entry_target
        return diff

    eta, res = sp.optimize.brentq(
        diff_func, search_scrope[0], search_scrope[1],
        args=(entry_target, x),
        xtol=0.001,
        maxiter=max_iter, full_output=True
    )
    assert res.converged, "Failed to converge in parameter finding!"

    new_res = _solve_model(x, eta=eta)
    return new_res


def counterfactural_avgsize_decline(avgsize_target=None, para_index=0, max_iter=200, search_scrope=4):
    # exactly the same code except for avgsize
    x = read_result()[:-1]
    p_init = x[para_index]

    def diff_func(p, para_index, avgsize_target, x):
        x[para_index] = p
        res = _solve_model(x)
        diff = res.average_firm_size_include_cf - avgsize_target
        return diff

    p, res = sp.optimize.brentq(
        diff_func, p_init*(1/search_scrope), p_init*search_scrope,
        args=(para_index, avgsize_target, x),
        xtol=0.001,
        maxiter=max_iter, full_output=True
    )
    assert res.converged, "Failed to converge in parameter finding!"

    x[para_index] = p
    new_res = _solve_model(x)
    return new_res


def counterfactural_para_change(para_index=0, para_ratio=1.1):
    assert para_index in [2,3,4,5,6] # ce, cf, G_mu, G_sigma, a, rho, sigma = x
    x = read_result()[:-1]
    p_init = x[para_index]

    x[para_index] = p_init * para_ratio
    new_res = _solve_model(x)
    return new_res


def counterfactural_gamma_l(w_diff_ratio_target=2, max_iter=200, search_scrope=(0, 0.5)):
    x = read_result()[:-1]

    def diff_func(gamma_l, avgsize_taw_diff_ratio_target, x):
        res = _solve_model(x, gamma_l=gamma_l)
        diff = res.w_vals[-1] / res.w_vals[0] - avgsize_taw_diff_ratio_target
        return diff

    gamma_l, res = sp.optimize.brentq(
        diff_func, search_scrope[0], search_scrope[1],
        args=(w_diff_ratio_target, x),
        xtol=0.001,
        maxiter=max_iter, full_output=True
    )
    assert res.converged, "Failed to converge in parameter finding!"

    new_res = _solve_model(x, gamma_l=gamma_l)
    return new_res


def main():

    res = counterfactural_entry_decline(entry_target=3, para_index=0)
    res = counterfactural_gamma_l(w_diff_ratio_target=2)
    print(res.stat)


if __name__ == "__main__":
    main()
