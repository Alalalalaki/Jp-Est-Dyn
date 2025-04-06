"""
Draw Aggregate Trend of Establishments based on EEC data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle, add_super_label_for_multi_axes,
                            set_style, set_axes, set_size, save_fig,)
from Data_General import get_industry, get_industry_name


dfh = pd.read_pickle(input_path+'Offical_Historical_EEC.pkl')


def calculate_num_employment_by_org(
        df=dfh, ind="NALL", orgs=["ALL", 'individual_proprietorship', 'company', 'corporations']):
    dfh62 = df.query('table_id == "06-02" ')

    num = (
        dfh62.query('organization in @orgs & industry == @ind & size == "ALL" ')
        .sort_values('year')
        .pivot('year', 'organization', 'num')
        .rename_axis(None, axis=1)
    )
    employ = (
        dfh62.query('organization in @orgs & industry == @ind & size == "ALL" ')
        .sort_values('year')
        .pivot('year', 'organization', 'employment')
        .rename_axis(None, axis=1)
    )
    avgsize = (employ/num)

    return num, employ, avgsize


def plot_avgsize_trend_by_org(orgs=["company", "corporations"], pre_period_interpolate=False, _ax=None):
    num, employ, avgsize = calculate_num_employment_by_org(orgs=orgs)
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    avgsize[orgs].plot(ax=ax, marker='o')

    if pre_period_interpolate:
        num, employ, avgsize = calculate_num_employment_by_org(orgs=["company", "corporations"])
        value_1957 = avgsize["company"][1957]
        pct = avgsize["corporations"].pct_change().loc[[1954, 1957]].values
        value_1954 = value_1957 / (1+pct[1])
        value_1951 = value_1954 / (1+pct[0])
        ax.plot([1954, 1957], [value_1954, value_1957],
                color=get_colors()[0], linestyle='--', marker='o', markerfacecolor='None')

    if not _ax:
        return fig, ax


def set_avgsize_trend_by_org(ax, year_ini=1956, labels=['Employer', 'Employer (All Corporations)']):
    # ax.get_lines()[1].set(markerfacecolor="None", linestyle="--")
    ax.set_xlim(year_ini, 2007)  # if also include corporations set year_init to 1950
    # ax.set_ylim(0.2,8.2)
    ax.set_xlabel('')
    ax.set_ylabel('Avg. Workers per Est.')
    ax.legend(labels, loc='best', frameon=False)


def plot_avgsize_trend_by_org_by_ind(inds, labels, row, col, orgs=["company"], normalize=False):

    fig, axes = plt.subplots(row, col, sharey=True)
    axes = axes.flatten()
    for ind, ax, l in zip(inds, axes, labels):
        _, _, avgsize = calculate_num_employment_by_org(ind=ind, orgs=orgs)
        if normalize:
            avgsize = avgsize.apply(lambda x: x/x.dropna().iloc[0])
        avgsize[orgs].plot(ax=ax, marker='o', title=l, legend=None)
    return fig, axes


def set_avgsize_trend_by_org_ind(axes, fig, year_ini=1956, label='Average Est. Size'):
    for i, ax in enumerate(axes):
        ax.set_xlim(year_ini, 2007)
        # ax.set_ylim(0.2,8.2)
        ax.set_xlabel('')
        # if i == 0:
        #     ax.legend("Employer", loc='best', frameon=False)

    add_super_label_for_multi_axes(fig, label)


def plot_avgsize_trend_counterfactural(orgs=["company"], start=1969):
    fig, ax = plot_avgsize_trend_by_org(orgs=orgs)

    inds = ['鉱業', '建設業', '製造業',
            '運輸・通信業',  '電気・ガス・水道・熱供給業',
            '卸売・小売業', '金融・保険業', '不動産業',
            'サービス業',
            ]
    total_num_base_year = calculate_num_employment_by_org(ind='NALL', orgs=orgs)[0].loc[start].values[0]
    weight_base = []
    avgsize_matrix = pd.DataFrame(columns=inds)
    for ind in inds:
        num, employ, avgsize = calculate_num_employment_by_org(ind=ind, orgs=orgs)
        weight_base.append(num.loc[start].values[0]/total_num_base_year)
        avgsize_matrix[ind] = avgsize.query("year >= @start")
    avgsize_matrix_weighted = np.array(weight_base).reshape(1, -1) * avgsize_matrix.values
    avgsize_counterfactural = pd.Series(avgsize_matrix_weighted.sum(axis=1), index=avgsize_matrix.index)
    avgsize_counterfactural.plot(ax=ax, color=get_colors([1]),
                                 linestyle='--', marker='o', markerfacecolor='None')

    return fig, ax


def plot_num_employment_trend_by_org(row, col,
                                     orgs=["ALL", 'individual_proprietorship', 'company', 'corporations']):
    num, employ, avgsize = calculate_num_employment_by_org(orgs=orgs)
    fig, axes = plt.subplots(row, col)
    titles = ['(a) Number', '(b) Employment', '(c) Average Size']
    for d, ax, t, in zip([num, employ, avgsize], axes, titles,):
        d.plot(color=get_colors(order=[0, 1, 1, 2]), linewidth=2, style=['-', '-', ':', '-'],
               ax=ax, legend=False, title=t)  #
    return fig, axes


def set_num_employment_trend_by_org(axes, fig):
    for (i, ax) in enumerate(axes):
        ax.set_xlim(1950, 2007)
        if i == 0:
            unit = int(1e6)
            yticks = range(unit, unit*8, unit)
            ax.set_yticks(yticks)
            ax.set_yticklabels([f'{y/1e6:.0f}' for y in yticks])
            ax.set_ylabel('Number (in millions)')
            ax.set_xlabel('')
        if i == 1:
            unit = int(1e7)
            yticks = range(unit, unit*7, unit)
            ax.set_yticks(yticks)
            ax.set_yticklabels([f'{y/1e6:.0f}' for y in yticks])
            ax.set_ylabel('Employment (in millions)')
            ax.set_xlabel('')
        if i == 2:
            unit = 5
            yticks = range(unit, unit*6, unit)
            ax.set_yticks(yticks)
            ax.set_xlabel('')
            # ax.set_yticklabels([f'{y/1e6:.0f}' for y in yticks])
            ax.set_ylabel("Employment")
            handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, ['Total (Private)', 'Company', 'Corporation', 'Sole Proprietorship'],
               loc='lower center', frameon=False, ncol=4, bbox_to_anchor=(0.5, 0), handlelength=1,)


def main():

    inds = get_industry()
    labels_ind = [get_industry_name(i) for i in inds]

    set_style()

    # # plot_avgsize_trend_by_org
    # fig, ax = plot_avgsize_trend_by_org(orgs=["company"])  # , "corporations"
    # replace above simple one trend to adding counterfactural
    fig, ax = plot_avgsize_trend_counterfactural(orgs=["company"], start=1963)
    set_avgsize_trend_by_org(ax, labels=['Employer (data)', 'Employer (fixed sector share)'])
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'avgsize_trend.pdf')

    # plot_avgsize_trend_by_org_by_ind
    # ["製造業", "サービス業", "建設業", "金融・保険業", "運輸・通信業", "卸売・小売業"]
    # ["Manufacturing", "Service", "Construction", "Finance", "Transport & Communication", "Wholesale & Retail"]
    # Caution: cannot add "corporations" as the growth for service sector in corporations is abnormally high due to a low level in early period
    fig, axes = plot_avgsize_trend_by_org_by_ind(
        orgs=["company", ],  # "corporations"
        inds=inds,
        labels=labels_ind,
        row=2, col=3,
        normalize=True)
    set_avgsize_trend_by_org_ind(axes, fig, label='Avg. Est. Size (Normalize 1957 = 1)')  # year_ini=1950,
    set_size(fig, fraction=1.1, row=1, w_pad=.5)
    save_fig(fig, 'avgsize_trend_by_ind_norm.pdf')
    # plot exactly the same but un-normalized
    fig, axes = plot_avgsize_trend_by_org_by_ind(
        orgs=["company", ],  # "corporations"
        inds=inds,
        labels=labels_ind,
        row=2, col=3,
        normalize=False)
    set_avgsize_trend_by_org_ind(axes, fig, label='Avg. Est. Size (Employees)')  # year_ini=1950,
    set_size(fig, fraction=1.1, row=1, w_pad=.5)
    save_fig(fig, 'avgsize_trend_by_ind.pdf')

    # plot_num_employment_trend_by_org
    row, col = 1, 3
    fig, axes = plot_num_employment_trend_by_org(row, col)
    set_num_employment_trend_by_org(axes, fig)
    set_size(fig, fraction=1.2, row=row, rect=[0, 0.05, 1, 1])
    save_fig(fig, 'num_employment_trend_by_org.pdf')


if __name__ == "__main__":
    main()
