"""
Draw Exit rate based on EEC data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style,  set_axes, set_size, save_fig, )
from Data_General import clean_df, age_zero_adjust


def exit_rate_from_two_year(
    year1, year2, agelist1, agelist2, df, ind="NALL", org="employer", size="ALL"
):
    diff = year2 - year1
    adjust_month = ((age_zero_adjust()[year2] - age_zero_adjust()[year1])/12) + diff
    before = (
        df.query('organization == @org & industry == @ind & size == @size ')
        .query('year == @year1')
        .pivot(index='age', columns='year', values='num')
        .loc[agelist1, :]
        .reset_index()
        .rename(columns={'age': f'age_before'})
    )
    after = (
        df.query('organization == @org & industry == @ind & size == @size ')
        .query('year == @year2')
        .pivot(index='age', columns='year', values='num')
        .loc[agelist2, :]
        .reset_index()
        .rename(columns={'age': f'age_after'})
    )
    exit_rate = (
        before.join(after)
        .assign(exit_rate=lambda x: (1 - (x[year2] / x[year1])) * 100)
        .eval('exit_rate_per_year=exit_rate/@adjust_month')
        .replace('~', '-', regex=True)
    )
    # print(exit_rate)
    return exit_rate


def plot_exit_rate(df, ax=None, var='exit_rate_per_year', group=1, ):
    year1 = df.columns[1]
    year2 = df.columns[-3]
    diff = year2 - year1
    width = len(df)/24
    # to make bar not duplicated, don't know why not work
    cohorts = df.age_before.unique()
    cohorts_map = dict(zip(cohorts, np.arange(len(cohorts))))
    df = df.assign(x=lambda df: df.age_before.map(cohorts_map)+(width*(group-1)))
    ax.bar(df['x'], df[var], width=width,)
    ax.set_title(f'{year1}-{year2} ({str(diff)}yr avg)')
    ax.set_xticks(df.x - (width / 2))
    ax.set_xticklabels(cohorts, rotation=45,)


def plot_exit_rates(df, orgs = ['employer', 'nonemployer',],
                    groups = [1, 2]  # use to plot columned bars
                    ):

    fig, axes = plt.subplots(3, 3, sharey=True)
    for org, g, in zip(orgs, groups):
        axes = axes.flatten(order='C') # I fogot why I set it to 'F' which is column-order but now I feel raw-order is better

        age1969b = ['1', '2', '3~5', '6~8', '9~11', '12~14', '15~17', '18~24', '25+']
        age1972a = ['4', '5', '6~8', '9~11', '12~14', '15~17', '18~20', '21~27', '28+', ]
        exit_rate_from_two_year(1969, 1972, age1969b, age1972a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[0])

        age1972b = ['1', '2', '3~5', '6~8', '9~11', '12~14', '15~17', '18~20', '21~27', '28+']
        age1975a = ['4', '5', '6~8', '9~11', '12~14', '15~17', '18~20', '21~23', '24~30', '31+', ]
        exit_rate_from_two_year(1972, 1975, age1972b, age1975a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[1])

        age1975b = ['3~20', '21~30', '31+']
        age1978a = ['6~23', '24~33', '34+', ]
        exit_rate_from_two_year(1975, 1978, age1975b, age1978a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[2])

        age1978b = ['3~5', '6~23', '24~33', '34+']
        age1981a = ['6~8', '9~26', '27~36', '37+']
        exit_rate_from_two_year(1978, 1981, age1978b, age1981a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[3])

        age1981b = ['1', '2~16', '17~26', '27+']
        age1986a = ['6', '7~21', '22~31', '32+']
        exit_rate_from_two_year(1981, 1986, age1981b, age1986a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[4])

        age1986b = ['1', '2~11', '12~21', '22~31', '32+']
        age1991a = ['6', '7~16', '17~26', '27~36', '37+']
        exit_rate_from_two_year(1986, 1991, age1986b, age1991a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[5])

        age1991b = ['1', '2~6', '7~16', '17~26', '27~36', '37+']
        age1996a = ['6', '7~11', '12~21', '22~31', '32~41', '42+']
        exit_rate_from_two_year(1991, 1996, age1991b, age1996a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[6])

        age1996b = ['1', '2~11', '12~21', '22~31', '32~41', '42+']
        age2001a = ['6', '7~16', '17~26', '27~36', '37~46', '47+']
        exit_rate_from_two_year(1996, 2001, age1996b, age2001a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[7])

        age2001b = ['1', '2~6', '7~16', '17~26', '27~36', '37~46', '47+']
        age2006a = ['6', '7~11', '12~21', '22~31', '32~41', '42~51', '52+']
        exit_rate_from_two_year(2001, 2006, age2001b, age2006a, df=df, org=org).pipe(
            plot_exit_rate, group=g, ax=axes[8])

        # age2004a = ['4', '5~9', '10~19', '20~29', '30~39', '40~49', '50+']
        # exit_rate_from_two_year(2001, 2004, age2001b, age2004a, df=df, org=org).pipe(
        #     plot_exit_rate, group=g, ax=axes[7])
        # age2004b = ['1', '2~4', '5~9', '10~19', '20~29', '30~39', '40~49', '50+']
        # age2006a2 = ['3', '4~6', '7~11', '12~21', '22~31', '32~41', '42~51', '52+']
        # exit_rate_from_two_year(2004, 2006, age2004b, age2006a2, df=df, org=org).pipe(
        #     plot_exit_rate, group=g, ax=axes[8])

    return fig, axes


def set_exit_rate(axes, fig, labels=['Employer', 'Nonemployer']):
    for i, ax in enumerate(axes):
        ax.set_xlabel('')
        ax.set_ylim(-4, 12)
        if i == 4:
            ax.legend(labels, loc='upper center', frameon=False,)


def main():
    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

    set_style()

    # plot entry rate by org
    fig, axes = plot_exit_rates(dfa,)
    set_exit_rate(axes, fig)
    set_axes(axes)
    set_size(fig, fraction=1, row=1.618)
    save_fig(fig, 'exit_rate_by_age_by_org.pdf')

    fig, axes = plot_exit_rates(dfa,orgs=['employer', 'ALL',])
    set_exit_rate(axes, fig, labels=['Employer', 'All Est.'])
    set_axes(axes)
    set_size(fig, fraction=1, row=1.618)
    save_fig(fig, 'exit_rate_by_age.pdf')

if __name__ == "__main__":
    main()
