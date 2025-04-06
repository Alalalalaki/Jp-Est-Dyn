"""
Draw Age-Size relationship over time based on EEC data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle, add_super_label_for_multi_axes,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df, age_cohorts, get_age_mean


def plot_age_size_relation_trend(df, org="employer"):
    years = [1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006]  # drop 1978 as too few age cohorts
    cohorts = age_cohorts()
    fig, axes = plt.subplots(1, len(years), )
    for year, ax in zip(years, axes.flatten()):
        age_size = (
            df.query('organization == @org & industry == "NALL" & size == "ALL" ')
            .query('year == @year ')
            .filter(['year', 'age', 'num', 'employment'])
            .eval('average_size = employment / num ')
            .set_index('age').reindex(cohorts[year])
            .reset_index().pipe(get_age_mean)
            .set_index('age_mean')
            ['average_size']
        )
        age_size.plot(title=f'{year}', ax=ax, color=get_colors([0]), label=org)  # alpha=0.7

        # # mark certain age cohort
        age_marker = [0, 20]
        for a, m, c in zip(age_marker, ['o', 'o'], ['none', 'none']):
            ax.scatter(a, np.interp(a, age_size.index, age_size.values),
                       color='black', facecolors=c, label=f'Age {a}', marker=m,)
    return fig, axes


def set_age_size_relation_trend(axes, fig):
    for i, ax in enumerate(axes):
        ax.set_xlabel('')
        ax.set_xlim(0, 40)
        ax.set_xticks(range(0, 41, 20))
        ax.set_ylim(9, 26)
        # ax.set_ylim(2.4, 3.6) # for nonemployer
        if i > 0:
            ax.set_yticklabels([])
        else:
            ax.set_ylabel('Average Est. Size (Employment)')

        # if i == col-1:
        #     handles, labels = ax.get_legend_handles_labels()
        #     ax.legend(handles[1:], labels[1:], handlelength=0.2, frameon=False)
    # fig.legend(handles[2:], labels[2:], bbox_to_anchor=(0.2, 0.76),
    #            handlelength=0.2, frameon=False)

    add_super_label_for_multi_axes(fig, xlabel='Age')


def plot_age_size_relation_trend_by_ind(df):
    """Simply use above copy with minor changes"""
    org = "employer"
    inds = ["製造業", "卸売・小売業", "サービス業"]
    years = [1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006]  # drop 1978 as too few age cohorts
    cohorts = age_cohorts()
    fig, axes = plt.subplots(len(inds), len(years), )
    for i, ind in enumerate(inds):
        axes_row = axes[i, :]
        for year, ax in zip(years, axes_row.flatten()):
            age_size = (
                df.query('organization == @org & industry == @ind & size == "ALL" ')
                .query('year == @year ')
                .filter(['year', 'age', 'num', 'employment'])
                .eval('average_size = employment / num ')
                .set_index('age').reindex(cohorts[year])
                .reset_index().pipe(get_age_mean)
                .set_index('age_mean')
                ['average_size']
            )
            age_size.plot(title=f'{year}', ax=ax, color=get_colors()[i], label=org)  # alpha=0.7
            age_marker = [5, 20]
            for a, m, c in zip(age_marker, ['x', 'o'], ['black', 'none']):
                ax.scatter(a, np.interp(a, age_size.index, age_size.values),
                           color='black', facecolors=c, label=f'Age {a}', marker=m,)
    return fig, axes


def set_age_size_relation_trend_by_ind(axes, shape, fig):
    try:
        row, col = shape[0], shape[1]
    except IndexError:
        row, col = 1, shape[0]
    for i, ax in enumerate(axes):
        ax.set_xlabel('')
        ax.set_xlim(0, 40)
        ax.set_xticks(range(0, 41, 20))
        if i not in range(0, row*col, col):
            ax.set_yticklabels([])
        # if i < col*(row-1):
        #     ax.set_xticklabels([])
        if i == col-1:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[1:], labels[1:], handlelength=0.2, frameon=False)
    fig.text(0.5, 1, 'Manufacturing', horizontalalignment='center', fontsize=12)
    fig.text(0.5, 0.66, 'Retail & Wholesale', horizontalalignment='center', fontsize=12)
    fig.text(0.5, 0.33, 'Services', horizontalalignment='center', fontsize=12)
    fig.text(0.5, 0.0, 'Age', ha='center', fontsize=12)
    fig.text(0.0, 0.5, 'Average Size', va='center', rotation='vertical', fontsize=12)


def main():
    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

    set_style()  # tick_direction="in", ticksize=2,

    # plot entry rate by org
    fig, axes = plot_age_size_relation_trend(dfa,)
    shape = axes.shape
    axes = axes.flatten()
    set_age_size_relation_trend(axes, fig)
    set_size(fig, fraction=.9, row=1, w_pad=0)
    save_fig(fig, 'age_size_relation_trend.pdf')

    # # plot entry rate by ind
    # fig, axes = plot_age_size_relation_trend_by_ind(dfa)
    # shape = axes.shape
    # axes = axes.flatten()
    # set_age_size_relation_trend_by_ind(axes, shape, fig)
    # set_size(fig, fraction=1.2, row=1.4, h_pad=3)
    # save_fig(fig, 'age_size_relation_trend_by_ind.pdf')


if __name__ == "__main__":
    main()
