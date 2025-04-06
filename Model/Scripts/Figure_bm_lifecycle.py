"""
This code plots the conditional lifecyle growth in benchmark model compared with data
"""

import pandas as pd
import matplotlib.pyplot as plt

import project_path
from Figure_General import set_style, set_axes, set_size, save_fig
from Figure_life_cycle_growth import plot_life_cycle_growth, set_life_cycle_growth

from calibration import read_result, _solve_model


def plot_model_lifecycle_growth(res, age=36, label="Benchmark Model", _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    plot_life_cycle_growth(years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ],
                                     color="grey", alpha=0.3, label=False, _ax=ax)

    init_avgsize = res.stat.average_entrant_size_include_cf
    lifeage = range(1, age+1)
    lifeage_label = range(0, age)
    lifecycle_growth_rate = [1+res.calculate_survival_stat(age=a)[1]/100 for a in lifeage]
    lifecycle_avgsize = [init_avgsize * g for g in lifecycle_growth_rate]
    ax.plot(lifeage_label, lifecycle_avgsize, label=label)

    if not _ax:
        return fig, ax


def set_model_lifecycle_growth(ax):
    # ax.set_title(f'Growth Path of Age {age} Cohort Started At Different Period - {ind}')
    ax.set_xlabel('Age')
    ax.set_ylabel('Avg. Est. Size (Employee)')
    ax.legend(loc='best', frameon=False, )


def plot_model_lifecycle_survival(res, age=36, label="Benchmark Model", _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    lifeage = range(1, age+1)
    lifeage_label = range(0, age)
    survival_rate = [res.calculate_survival_stat(age=a)[0] for a in lifeage]
    ax.plot(lifeage_label, survival_rate, label=label)

    if not _ax:
        return fig, ax


def set_model_lifecycle_survival(ax):
    ax.set_xlabel('Age')
    ax.set_ylabel('Survival Rate (%)')
    ax.legend(loc='best', frameon=False, )


def plot_model_lifecycle(res, age=36):
    fig, axes = plt.subplots(2, 1, sharex=True)
    plot_model_lifecycle_growth(res=res, age=age, label="Avg. Size", _ax=axes[0])
    plot_model_lifecycle_survival(res=res, age=age, label="Survival Rate", _ax=axes[1])
    return fig, axes


def set_model_lifecycle(axes):
    axes[0].set_ylabel('Avg. Est. Size (Employee)')
    axes[0].legend(loc='best', frameon=False, )

    axes[1].set_xlabel('Age')
    axes[1].set_ylabel('Survival Rate (%)')
    axes[1].legend(loc='best', frameon=False, )


def main():
    age = 36

    x = read_result()[:-1]
    res = _solve_model(x)

    set_style()

    fig, ax = plot_model_lifecycle_growth(res=res, age=age)
    set_model_lifecycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_lifecycle_growth.pdf')

    fig, ax = plot_model_lifecycle_survival(res=res, age=age)
    set_model_lifecycle_survival(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_lifecycle_survival.pdf')

    fig, axes = plot_model_lifecycle(res=res, age=age)
    set_model_lifecycle(axes)
    set_size(fig, fraction=0.7, row=1.5)
    save_fig(fig, 'benchmark_lifecycle.pdf')


if __name__ == "__main__":
    main()
