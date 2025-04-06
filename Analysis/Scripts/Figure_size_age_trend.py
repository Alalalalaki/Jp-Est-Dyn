"""
Draw trend of Num and Employment Share and Average Size by Size Categroies based on EEC data

Note:
 - for size cohorts can use simple or normal, but the latter is only a little more informative

To-do:
 - the set of the figures are arbitrary, dependent on ages cohort chosen, need to modify
 - the 6~11 in age cohorts is less informative, might remove
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df, size_cohorts


dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)


def plot_size_trend(
        df=dfa, values=['num_share', 'employment_share'],
        ages=['ALL', '0~5', '6~11', '17~26'], cat='normal', org="employer",  # 'nonemployer'
        sharey=True, trend_as_index=False,
):

    sizes = size_cohorts(cat=cat)
    fig, axes = plt.subplots(len(ages), len(sizes), sharey=sharey)
    for i, age in enumerate(ages):
        if len(ages) == 1:
            axes_row = axes
        else:
            axes_row = axes[i, :]
        for size, ax in zip(sizes, axes_row):
            temp = (df.query('organization == @org & industry == "NALL" & age == @age ')
                    .groupby('year').apply(lambda df: df.assign(
                        num_share=lambda x: x.num/np.nanmax(x.num)*100,
                        employment_share=lambda x: x.employment/np.nanmax(x.employment)*100,
                        average_size=lambda x:  x.employment/x.num,
                    )
            )
                .query('size in @sizes')
                .pivot('year', 'size', values)
                .reorder_levels([1, 0], axis=1)
                .loc[:, size]
            )
            if trend_as_index:
                temp = temp.apply(lambda x: x/x.iloc[0])
            temp.plot(title=size.replace('~', '-'), ax=ax, legend=None)
    return fig, axes


def set_size_trend(axes, shape, fig, legend, legendloc, ylabels):
    try:
        row, col = shape[0], shape[1]
    except IndexError:
        row, col = 1, shape[0]
    for i, ax in enumerate(axes):
        ax.set_xlim(1968, 2007)
        ax.set_xlabel('')
        # if i % col == 0:
        #     ax.set_ylabel(ylabels[i//col], rotation=0, horizontalalignment='right', size='large')

        # ax.set_xticks(range(1970, 2010, 10))
        ax.yaxis.set_tick_params(labelleft=True)

        if i == 0:
            handles, labels = ax.get_legend_handles_labels()
    if legend:
        fig.legend(handles, legend, bbox_to_anchor=legendloc,
                   handlelength=0.3, frameon=False)
    # fig.text(0.03, 0.97, ylabel)
    for i, l in enumerate(ylabels):
        fig.text(0.5, (1-1/row*(i)), l, horizontalalignment='center', fontsize=12)
    # fig.subplots_adjust(top=0.98)


def set_avgsize_trend(axes, shape, cat="normal"):
    try:
        row, col = shape[0], shape[1]
    except IndexError:
        row, col = 1, shape[0]
    sizes = size_cohorts(cat=cat)
    up_bound = 500 if cat == "simple" else 1000
    sizes[-1] = f'{sizes[-1][:-1]}~{up_bound}'
    for i, s in enumerate(sizes):
        temp = s.split('~')
        for a in range(i, row*col, col):
            axes[a].set_ylim(int(temp[0])*1.1, int(temp[1])*0.9)


def main():

    ages = ['ALL', '0~5', '17~26']  # '6~11',
    labels = ['Age: '+a.replace('~', '-') for a in ages]

    set_style()

    # # plot num and employment share
    # fig, axes = plot_size_trend(dfa, values=['num_share', 'employment_share'],
    #                             cat="simple")  # trend_as_index=True
    # shape = axes.shape
    # axes = axes.flatten()
    # set_size_trend(axes, shape, fig,
    #                legend=['Number', 'Employment'], legendloc=(0.59, 0.94),
    #                ylabel='%')
    # set_size(fig, fraction=1, row=2, h_pad=3)
    # save_fig(fig, 'share_trend_by_size_by_age.pdf')

    # plot num share
    fig, axes = plot_size_trend(ages=ages, values=['num_share', ], sharey='col', cat="simple")  # 'employment_share'
    shape = axes.shape
    axes = axes.flatten()
    set_size_trend(axes, shape, fig, legend=None, legendloc=None, ylabels=labels)
    set_size(fig, fraction=0.9, row=1.2, h_pad=2.5, w_pad=0.5)
    save_fig(fig, 'numshare_trend_by_size_by_age.pdf')

    # # plot entry rate by age
    # fig, axes = plot_size_trend(dfa, values=['average_size'], sharey=False, cat="simple")
    # shape = axes.shape
    # axes = axes.flatten()
    # set_size_trend(axes, shape, fig, legend=None, legendloc=None, ylabel='')
    # set_avgsize_trend(axes, shape, cat="simple")
    # set_size(fig, fraction=1, row=2, h_pad=3)
    # save_fig(fig, 'avgsize_trend_by_size_by_age.pdf')


if __name__ == "__main__":
    main()
