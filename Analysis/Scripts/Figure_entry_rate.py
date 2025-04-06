"""
Draw Entry rate based on EEC data
"""

import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle, add_super_label_for_multi_axes,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df, age_zero_adjust, interpolated_dfh, get_industry, get_industry_name, sme_entry_exit_data

dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)


def calculate_entry_exit_rate(df=dfa, method='1', org='employer', ind='NALL', dropyear=[2004]):
    if method == '0~3':
        assert org == "ALL", "If use 0~3 method, must have org to be ALL."
        ages = ["0~3", "ALL"]
        years = [1957, 1969]
        entry = (df.query('organization == @org & industry == @ind & size == "ALL"')
                 .query('age in @ages')
                 .query('year in @years')
                 .pivot(index='year', columns='age', values='num')
                 .rename(columns={'0~3': 'entry'})
                 .assign(adjust=lambda x: x.index.map(age_zero_adjust(first=0)))
                 .assign(denominator_year=lambda x: x.index-1)
                 .merge(interpolated_dfh(org="ALL", ind=ind).assign(
                     net_growth_rate=lambda x: x.num.pct_change()*100
                 )[['num', 'net_growth_rate']],
            how='left', left_on='denominator_year', right_index=True)
            .eval('entry_rate = ( entry * 12 / (36+adjust) / num) *100 ')
            .eval('exit_rate = entry_rate - net_growth_rate')
            .reset_index()
        )
    elif method == '1':
        ages = ["1", "ALL"]
        years_out = [1957, 1978, 1989]+dropyear
        entry = (df.query('organization == @org & industry == @ind & size == "ALL"')
                 .query('age in @ages')
                 .query('year not in @years_out')
                 .pivot(index='year', columns='age', values='num')
                 .rename(columns={'1': 'entry', })
                 .assign(denominator_year=lambda x: x.index-1)
                 .merge(interpolated_dfh(org=org, ind=ind).assign(
                     net_growth_rate=lambda x: x.num.pct_change()*100
                 )[['num', 'net_growth_rate']],
            how='left', left_on='denominator_year', right_index=True)
            .eval('entry_rate = (entry / num) *100 ')
            .eval('exit_rate = entry_rate - net_growth_rate')
            .reset_index()
        )
    else:
        raise ValueError('Method must be either "0~3" or "1".')
    return entry


def plot_entry_rate(
        mode='entry_rate', orgs=['ALL', 'employer', 'nonemployer', ], colors=['C0', 'C1',],
        pre_period=True, pre_period_interpolate=False, sme=False, _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()

    # use age1 / total in a certain census year to calculate one year entry rate
    for org, c in zip(orgs, colors):
        entry = calculate_entry_exit_rate(method='1', org=org, ind='NALL', dropyear=[])
        entry.plot('year', mode, ax=ax, marker='o', color=c, )

    # for 1957, use age 0~3 with adjustment on age 0 months to calculate entry rate per year
    # underestimated due to mortality of young firms, which can be shown by 1969 data
    if pre_period:
        entry_pre = calculate_entry_exit_rate(method='0~3', org='ALL', ind='NALL')
        entry_pre.plot('year', mode, color=get_colors()[1], linestyle='--',
                       marker='o', markerfacecolor='None', ax=ax, legend=False)

    if pre_period_interpolate:
        assert "employer" in orgs, "pre_period_interploate only interploate for org==employer"
        entry = calculate_entry_exit_rate(method='1', org="employer", ind='NALL', dropyear=[])
        entry_pre = calculate_entry_exit_rate(method='0~3', org='ALL', ind='NALL')
        pct = entry_pre[mode].pct_change()[1]
        value_1969 = entry[mode][0]
        value_1957 = value_1969 / (1+pct)
        ax.plot([1957, 1969], [value_1957, value_1969],
                color=get_colors()[0], linestyle='--', marker='o', markerfacecolor='None')

    if sme:
        entry_sme = sme_entry_exit_data()
        entry_sme.plot('year', mode, color=get_colors()[2],
                       marker='o', markerfacecolor='None', ax=ax, legend=False)

    if not _ax:
        return fig, ax


def set_entry_rate(ax, labels, mode='Entry'):
    ax.set_xlim(1956, 2007)
    # ax.set_ylim(0.2,8.2)
    ax.set_xlabel('')
    ax.set_ylabel(f'{mode} Rate (%)')
    ax.legend(labels, loc='best', frameon=False)


def plot_entry_exit_rate(orgs=['ALL', 'employer', 'nonemployer', ]):
    # same code as above, except adding exit rate
    fig, axes = plt.subplots(2)

    # for 1957, use age 0~3 with adjustment on age 0 months to calculate entry rate per year
    # underestimated due to mortality of young firms, which can be shown by 1969 data
    entry = calculate_entry_exit_rate(method='0~3', org='ALL', ind='NALL')
    entry.plot('year', 'entry_rate', color=get_colors(), linestyle='--', marker='o', ax=axes[0],
               markerfacecolor='None')
    entry.plot('year', 'exit_rate', color=get_colors(), linestyle='--', marker='o', ax=axes[1],
               markerfacecolor='None', legend=False)

    # use age1 / total in a certain census year to calculate one year entry rate
    for org in orgs:
        entry = calculate_entry_exit_rate(method='1', org=org, ind='NALL', dropyear=[])
        entry.plot('year', 'entry_rate', ax=axes[0], marker='o')
        entry.plot('year', 'exit_rate', ax=axes[1], marker='o', legend=False)

    return fig, axes


def set_entry_exit_rate(axes):
    titles = ['(a) Entry Rate', '(b) Exit Rate']
    for i, ax in enumerate(axes):
        ax.set_xlim(1956, 2007)
        # ax.set_ylim(0.2,8.2)
        ax.set_xlabel('')
        if i == 0:
            ax.legend(['All Private', 'All Private', 'Employer', 'Nonemployer'], loc='best', frameon=False)
        ax.set_title(titles[i])


def plot_entry_rate_by_industry(mode='entry_rate', orgs=['ALL', 'employer', 'nonemployer', ]):
    # use exactly the same code to plot except put into a ind loop
    inds = get_industry()
    fig, axes = plt.subplots(2, 3, sharey=True)  # sharex=True
    axes = axes.flatten()
    for ind, ax in zip(inds, axes):
        for org in orgs:
            entry = calculate_entry_exit_rate(method='1', org=org, ind=ind, dropyear=[])
            entry.plot('year', mode, ax=ax, marker='o', legend=False, title=get_industry_name(ind))

        entry = calculate_entry_exit_rate(method='0~3', org='ALL', ind=ind)
        entry.plot('year', mode, color=get_colors([1]), linestyle='--', marker='o', ax=ax,
                   markerfacecolor='None',  legend=False)
    return fig, axes


def set_entry_rate_by_industry(axes, fig, labels, mode='Entry'):
    for i, ax in enumerate(axes):
        ax.set_xlim(1956, 2007)
        ax.set_xlabel('')
        if i == 0:
            ax.legend(labels, loc='best', frameon=False)

    add_super_label_for_multi_axes(fig, ylabel=f'{mode} Rate (%)')


def main():

    orgs = ['employer', 'ALL', ]
    labels = ['Employer (Age 1)', 'All Est. (Age 1)', 'All Est. (Age 0-3)']

    set_style()

    # # plot entry rate by org
    # fig, ax = plot_entry_rate(orgs=orgs)
    # set_entry_rate(ax, labels=labels)
    # set_size(fig, fraction=0.7, row=1,)
    # save_fig(fig, 'entry_rate_by_org.pdf')

    # # plot eixt rate by org
    # fig, ax = plot_entry_rate(mode='exit_rate', orgs=orgs)
    # set_entry_rate(ax, labels=labels, mode='Exit')
    # set_size(fig, fraction=0.7, row=1,)
    # save_fig(fig, 'exit_rate_by_org.pdf')

    # # # plot entry and eixt rate by org
    # # fig, axes = plot_entry_exit_rate(dfa)
    # # set_entry_exit_rate(axes)
    # # set_size(fig, fraction=0.7, row=2)
    # # save_fig(fig, 'entry_exit_rate_by_org.pdf')

    # # plot entry rate by ind
    # fig, axes = plot_entry_rate_by_industry(orgs=orgs)
    # set_entry_rate_by_industry(axes, fig, labels=labels)
    # set_size(fig, fraction=1.1, row=1, w_pad=.5)
    # save_fig(fig, 'entry_rate_by_org_by_ind.pdf')

    # # plot exit rate by ind
    # fig, axes = plot_entry_rate_by_industry(mode='exit_rate', orgs=orgs)
    # set_entry_rate_by_industry(axes, fig, labels=labels, mode='Exit')
    # set_size(fig, fraction=1.1, row=1, w_pad=.5)
    # save_fig(fig, 'exit_rate_by_org_by_ind.pdf')


    # with sme data as comparison
    orgs = ['ALL', ]; colors = ['C1', ]
    labels = ['All Est. (Age 1)', 'All Est. (Age 0-3)', 'All Est. (SME Calculation)']
    fig, ax = plot_entry_rate(orgs=orgs, colors=colors, sme=True)
    set_entry_rate(ax, labels=labels)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'entry_rate_sme.pdf')
    fig, ax = plot_entry_rate(mode='exit_rate', orgs=orgs, colors=colors, sme=True)
    set_entry_rate(ax, labels=labels,  mode='Exit')
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'exit_rate_sme.pdf')

if __name__ == "__main__":
    main()
