"""
Draw imputed life-cycle growth based on EEC data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle, add_super_label_for_multi_axes,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df, age_cohorts, get_age_mean, get_industry, get_industry_name


dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

def output_life_growth(df=dfa, cohort=[1969, 1], ind="NALL", org="employer"):
    """
    Return the age and average size for a cohort in its cohort and later years
    """
    years = [1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006]
    assert cohort[0] in years, f"cohort start year must be in {years}"
    assert cohort[1] >= 0, "cohort start age must be >= 0"
    cohorts = age_cohorts()
    life = [y-cohort[0]+cohort[1] for y in years]
    life_age = []
    life_size = []
    for year, age in zip(years, life):
        data = (
            df.query('organization == @org & industry == @ind & size == "ALL" ')
            .query('year == @year ')
            .filter(['year', 'age', 'num', 'employment'])
            .eval('average_size = employment / num ')
            .set_index('age').reindex(cohorts[year])
            .reset_index().pipe(get_age_mean)
            .set_index('age_mean')
            ['average_size']
        )
        if age >= 0:
            age_size = np.interp(age, data.index, data.values, right=np.nan)
            life_age.append(age)
            life_size.append(age_size)
    return life_age, life_size


def plot_life_cycle_growth(df=dfa, age=1, ind="NALL", org="employer",
                           years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, ],
                           color=None, alpha=None, label=True, _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    for year in years:
        life_age, life_size = output_life_growth(df, cohort=[year, age], ind=ind, org=org)
        # When set age large it can be trace back to starting age earlier.
        life_age = [a for a in life_age if a >= age]
        life_size = life_size[-1*len(life_age):]
        label = year if label else None
        if age>1:
            label = str(year) + ' (' + str(year-age) + ')'
        ax.plot(life_age, life_size, label=label, color=color, alpha=alpha)
    if not _ax:
        return fig, ax


def set_life_cycle_growth(ax):
    # ax.set_title(f'Growth Path of Age {age} Cohort Started At Different Period - {ind}')
    ax.set_xlabel('Age')
    ax.set_ylabel('Average Est. Size (Employment)')
    ax.legend(loc='best', frameon=False, handlelength=0.5, bbox_to_anchor=(1, .95))  # , bbox_to_anchor=(1, .95)


def plot_life_cycle_growth_by_industry(df=dfa, age=1, org="employer",
                                       years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, ]):
    # use exactly the same code to plot except put into a ind loop
    inds = get_industry()
    fig, axes = plt.subplots(2, 3)
    axes = axes.flatten()
    for ind, ax in zip(inds, axes):
        for year in years:
            life_age, life_size = output_life_growth(df, cohort=[year, age], ind=ind, org=org)
            # When set age large it can be trace back to starting age earlier.
            life_age = [a for a in life_age if a >= age]
            life_size = life_size[-1*len(life_age):]
            ax.plot(life_age, life_size, label=False,)
            ax.set_title(get_industry_name(ind))
    return fig, axes


def set_life_cycle_growth_by_industry(axes, fig, xticks=[0, 10, 20, 30]):
    for i, ax in enumerate(axes):
        ax.set_xlabel('')
        ax.set_xticks(xticks)

    add_super_label_for_multi_axes(fig, ylabel="Average Est. Size (Employment)", xlabel='Age')


def main():

    set_style()

    # plot life cyle growth for cohort at age = 1
    fig, ax = plot_life_cycle_growth(years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])  # 2001
    set_life_cycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'life_cycle_growth.pdf')

    # plot life cyle growth for cohort at age = 5
    fig, ax = plot_life_cycle_growth(age=5, years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'life_cycle_growth_age5.pdf')

    # plot life cyle growth for cohort at age = 10
    fig, ax = plot_life_cycle_growth(age=10, years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'life_cycle_growth_age10.pdf')

    # plot life cyle growth for cohort at age = 20
    fig, ax = plot_life_cycle_growth(age=20, years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'life_cycle_growth_age20.pdf')

    # plot life cyle growth for cohort at age = 26
    fig, ax = plot_life_cycle_growth(age=26, years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'life_cycle_growth_age26.pdf')

    # plot life cyle growth for cohort at age = 1 by industry
    fig, axes = plot_life_cycle_growth_by_industry(years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth_by_industry(axes, fig)
    set_size(fig, fraction=1, row=1, w_pad=.5)
    save_fig(fig, 'life_cycle_growth_by_ind.pdf')

    # plot life cyle growth for cohort at age = 20 by industry
    fig, axes = plot_life_cycle_growth_by_industry(age=20, years=[1969, 1972, 1975, 1981, 1986, 1991, 1996, ])
    set_life_cycle_growth_by_industry(axes, fig, xticks=[20, 30, 40])
    set_size(fig, fraction=1, row=1, w_pad=.5)
    save_fig(fig, 'life_cycle_growth_age20_by_ind.pdf')


if __name__ == "__main__":
    main()
