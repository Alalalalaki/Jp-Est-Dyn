"""
This code interpolate average size at birth in early period by using life cycle growth
"""

import matplotlib.pyplot as plt

import project_path

from Figure_General import set_style, set_axes, set_size, save_fig, get_colors
from Figure_avgsize_trend import plot_avgsize_trend_by_age
from Figure_life_cycle_growth import output_life_growth

from moments import Moments
from calibration import read_result, _solve_model

def conjecture_birth_avgsize(age, growth="model"):
    years = [1981, 1986, 1991, 1996, 2001, 2006] # use years after 1980 to aviod shocks on lifecycle growth
    birth_years = [y-age+1 for y in years]
    birth_avgsizes = []

    if growth=="model":
        x = read_result()[:-1]
        res = _solve_model(x)
        growth_rate = 1 + res.calculate_survival_stat(age=age)[1] / 100
    elif growth =="data":
        age = 26 if age >= 26 else age
        moment = Moments()
        growth_rate = 1 + moment.get_avg_life_growth(age=(1, age), years=(1969, 1972, 1975, 1981,)) / 100
    else:
        raise ValueError("growth must be either model or data")

    for year in years:
        life_age, life_size = output_life_growth(cohort=[year, age], ind="NALL", org="employer")
        birth_avgsize = life_size[life_age.index(age)] / growth_rate
        birth_avgsizes.append(birth_avgsize)
    return birth_years, birth_avgsizes


def plot_avgsize_birth():
    fig, ax = plt.subplots()



    # calculate the value in 1953
    birth_years_, birth_avgsizes_ = conjecture_birth_avgsize(age=29, growth="model")
    # calculate other values
    birth_years, birth_avgsizes = conjecture_birth_avgsize(age=26, growth="model")
    # combine
    birth_years, birth_avgsizes = birth_years_[0:1] + birth_years, birth_avgsizes_[0:1] + birth_avgsizes

    ax.plot(birth_years, birth_avgsizes, marker='o',  linestyle='--', markerfacecolor='None')

    plot_avgsize_trend_by_age(["1"], ind="NALL", _ax=ax)

    return fig, ax


def set_avgsize_birth(ax):
    ax.set_xlabel('')
    ax.set_ylabel('Avg. Est. Size (Employee)')
    ax.legend(['Conjectured Value', 'Data: Age 1 Avg. Size'], loc='best', frameon=False)


def main():

    set_style()

    fig, ax = plot_avgsize_birth()
    set_avgsize_birth(ax)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'birth_avgsize.pdf')


if __name__ == "__main__":
    main()
