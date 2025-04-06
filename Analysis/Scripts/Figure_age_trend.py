"""
Draw Num and Employment share trend by size categroies based on EEC data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df


def plot_share_trend_by_age(df, orgs=['employer', 'nonemployer']):
    ages = ['1~5', '6~11', '12~21', '17~26', '27+', ]  # '32+'
    fig, axes = plt.subplots(len(orgs), len(ages), sharey=True, sharex=True)

    linecolors = {"num": get_colors()[0], "employment": get_colors()[1]}
    linestyles = {"num": "-", "employment": "-"} #--
    markfaces = {"num": get_colors()[0], "employment": "None"}

    for i, org in enumerate(orgs):
        if len(orgs) == 1:
            axes_row = axes
        else:
            axes_row = axes[i, :]

        for age, ax in zip(ages, axes_row):
            age_with_ALL = [age, 'ALL']
            for var in ['num', 'employment']:
                (df.query('organization == @org & industry == "NALL" & size == "ALL" ')
                    .query('age in @age_with_ALL')
                    .pivot('year', 'age', var)
                    .assign(share=lambda x: x[age]/x['ALL']*100)
                    .dropna()
                    .reset_index()
                    .plot('year', 'share',
                          color=linecolors[var], linestyle=linestyles[var],
                          marker='o', markerfacecolor=markfaces[var],
                          ax=ax, title="Age "+age.replace('~', '-'), legend=None)
                 )

    return fig, axes


def set_share_trend_by_age(axes, shape, fig):
    try:
        row, col = shape[0], shape[1]
    except IndexError:
        row, col = 1, shape[0]
    for i, ax in enumerate(axes):
        # ax.legend('')
        ax.set_xlim(1969, 2006)
        ax.set_xlabel('')
        # ax.set_xticks(range(1970, 2010, 10))
        if i == 0:
            ax.set_ylabel('%')
            handles, _ = ax.get_legend_handles_labels()
    fig.legend(handles, ['Number Share', 'Employment Share'],
               ncol=2,
               loc='lower center',
               bbox_to_anchor=(.5, -.07),
               handlelength=1, frameon=False)
    # fig.subplots_adjust(bottom=0.3, )


def main():
    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

    set_style()

    # plot entry rate by org
    fig, axes = plot_share_trend_by_age(dfa, orgs=['employer'])
    shape = axes.shape
    axes = axes.flatten()
    set_share_trend_by_age(axes, shape, fig)
    set_size(fig, fraction=0.9, row=1, w_pad=0.2)
    save_fig(fig, 'share_trend_by_age.pdf')

    # # plot age trend by org
    # fig, axes = plot_share_trend_by_age(dfa)
    # shape = axes.shape
    # axes = axes.flatten()
    # set_share_trend_by_age(axes, shape, fig)
    # set_size(fig, fraction=0.9, row=1.8, h_pad=3)
    # save_fig(fig, 'share_trend_by_age_by_org.pdf')


if __name__ == "__main__":
    main()
