"""
Draw Average Size Trend based on EEC data
"""

import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_greys, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df, get_industry, get_industry_name


dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)


def get_avgsize_by_age(df=dfa, org="employer", ind="NALL",
                       ages=['0~5', '6~11', '12~21', '17~26', '27+', '32+', 'ALL']):
    df_ = (
        df.query('organization == @org & industry == @ind & size == "ALL" ')
        .query('age in @ages')
        .filter(['year', 'age', 'num', 'employment'])
        .eval('average_size = employment / num ')
        .pivot(index='year', columns='age', values='average_size')
        .loc[:, ages]
        .interpolate(limit_area='inside')
    )
    return df_


def plot_avgsize_trend_by_age(ages, ind="NALL", _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    df_ = get_avgsize_by_age(ages=ages, ind=ind)
    df_.plot(ax=ax, legend=False, )
    if not _ax:
        return fig, ax


def set_avgsize_trend_by_age(ax, fig, labels):
    ax.set_xlim(1968, 2007)
    ax.set_xlabel('')
    ax.set_ylabel('Avg. Est. Size (Employee)')
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc='best', frameon=False,
              bbox_to_anchor=(1, .8), handlelength=0.5)


def plot_avgsize_trend_by_ind_by_age(ages):
    inds = get_industry()

    fig, axes = plt.subplots(2, 3, sharex=True, )
    axes = axes.flatten()
    for ind, ax in zip(inds, axes):
        df_ = get_avgsize_by_age(ind=ind, ages=ages)
        df_.plot(ax=ax, legend=False, title=get_industry_name(ind),
                 #  color=get_colors(order=[0, 0, 1, 1, 2, 2, 5]), style=['-', '--']*3+['-.']
                 )
        # .apply(lambda x: x.dropna().plot(ax=ax, legend=False, title=get_industry_name(ind)))
    return fig, axes


def set_avgsize_trend_by_ind_by_age(axes, fig, labels):
    for i, ax in enumerate(axes):
        ax.set_xlim(1968, 2007)
        ax.set_xlabel('')
        if i == 0:
            handles, _ = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='lower center', frameon=False, ncol=len(labels), bbox_to_anchor=(0.5, -0.05),)


def main():

    # the trend of '12~17' in early 1970s somehow weirdly rising,
    # not sure if data issues, probably should drop from list
    ages = ['0~5', '6~11', '12~17', '12~21', '17~26', '18+', '27+', ]
    labels = ['0-5', '6-11', '12-17', '12-21', '17-26', '18+', '27+', ]

    set_style(marker_cycle=True)

    fig, ax = plot_avgsize_trend_by_age(ages=ages)
    set_avgsize_trend_by_age(ax, fig, labels)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'avgsize_trend_by_age.pdf')

    # plot avgsize by ind
    fig, axes = plot_avgsize_trend_by_ind_by_age(ages)
    set_avgsize_trend_by_ind_by_age(axes, fig, labels)
    set_size(fig, fraction=1.2, row=1, w_pad=.5)
    save_fig(fig, 'avgsize_trend_by_ind_by_age.pdf')


if __name__ == "__main__":
    main()
