"""
Draw Labor Growth Rate of Establishments based on Labor data and Establishment data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Data_General import input_path
from Figure_General import (get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig,)

dfl = pd.read_pickle(input_path+'Offical_JIL_LaborSupply.pkl')
dfh62 = pd.read_pickle(input_path+'Offical_Historical_EEC.pkl').query('table_id == "06-02" ')


def plot_labor_growth_lc(
        df=dfl, orgs=['employee_NALL', 'employment_NALL', 'employment', 'labor_force'], year_end=None,
        color=get_colors(order=[0, 0, 1, 1]), style=['-', ':', '-', ':'],
        _ax=None):
    if _ax:
        ax = _ax
    else:
        fig, ax = plt.subplots()
    df = df[orgs]  # 'nonemployee_NALL', '15+_population'
    if year_end:
        df = df.loc[:year_end,:]
    df.apply(lambda x: x.pct_change()*100).plot(ax=ax, color=color, style=style)
    if not _ax:
        return fig, ax


def set_labor_growth_lc(ax,):
    ax.set_xlim(1950, 2018)
    ax.set_xlabel('')
    ax.set_ylabel('Growth Rate (%)')
    ax.legend(['Employee (Non-Primary)', 'Employment (Non-Primary)',
               'Employment (All-Sector)', 'Labor Force'],
              loc='best', frameon=False)  # 'Other Employment (Non-Primary Sector)'


def plot_labor_growth_ec(df=dfh62, ):
    orgs = ['company', 'corporations', 'individual_proprietorship', ]
    fig, ax = plt.subplots()
    employ = (
        df.query('organization in @orgs & industry == "NALL" & size == "ALL" ')
        .sort_values('year')
        .pivot('year', 'organization', 'employment')
        .reindex(range(1950, 2018), fill_value=None)
        .interpolate(limit_area="inside")
        .rename_axis(None, axis=1)
        .pct_change()
    ).plot(ax=ax, color=get_colors(order=[0, 0, 1]), style=['-', ':',  '-'])
    return fig, ax


def set_labor_growth_ec(ax,):
    ax.set_xlim(1950, 2018)
    ax.set_xlabel('')
    ax.legend(['Employer', 'Employer (Corproration)', 'Nonemployer', ], loc='best', frameon=False)


def plot_labor_growth_decomp_single(df=dfl,i="employee_NALL",j="15+_population",ax=None):
    if ax is None:
        fig, ax = plt.subplots()
        ax_ = None
    else:
        ax_ = 1
    sample = df[[i,j]]
    sample = (sample.apply(lambda x: x.pct_change()).dropna()
    .assign(participation_rate = lambda x: x[i]-x[j])
    .assign(decade = lambda x: pd.cut(x.index,
            bins=range(1950,2021,1),labels=range(1950,2020,1)))
    .groupby("decade").mean()
            )
    (sample
    .drop(i,axis=1)
    .plot.bar(stacked=True, ax=ax)
    )
    (sample[i].plot(color="black", ax=ax))
    if ax_ is None:
        return fig, ax

def plot_labor_growth_decomp(df=dfl):
    fig, axes = plt.subplots(2)
    for i,j,ax in zip(["labor_force", "employee_NALL"],["15+_population", "15+_population"],axes):
        plot_labor_growth_decomp_single(df,i,j,ax)
    return fig, axes

def set_labor_growth_decomp_single(ax, legend=['Employee (Non-Primary) Growth Rate', 'Population Growth Rate', 'Participation Rate + Transformation Rate']):
    ax.set_xlabel('')
    ax.set_ylabel('Growth Rate (%)')
    ax.set_xticks(range(0, 72, 10))
    ax.set_xticklabels(range(1950, 2021, 10))
    ax.legend(legend, loc='best', frameon=False)

def set_labor_growth_decomp(axes):
    for ax in axes:
        set_labor_growth_decomp_single(ax)
    axes[0].set_title('Labor Force Growth Rate Decomposition')
    axes[0].legend(['Labor Force Growth Rate', 'Population Growth Rate', 'Participation Rate'], loc='best', frameon=False)
    axes[1].set_title('Employee (Non-Primary) Growth Rate Decomposition')
    axes[1].legend(['Employee (Non-Primary) Growth Rate', 'Population Growth Rate', 'Participation Rate + Transformation Rate'], loc='best', frameon=False)


def main():

    set_style()

    # plot labor growth rate from Labor Census - 2 figure
    fig, ax = plot_labor_growth_lc()
    set_labor_growth_lc(ax,)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'labor_growth_lc.pdf')

    # plot labor growth rate from Establishment Census
    fig, ax = plot_labor_growth_ec()
    set_labor_growth_ec(ax,)
    set_size(fig, fraction=0.7,)
    save_fig(fig, 'labor_growth_ec.pdf')

    # plot labor growth rate decomposition
    fig, axes = plot_labor_growth_decomp()
    set_labor_growth_decomp(axes)
    set_size(fig, fraction=0.7, row=2)
    save_fig(fig, 'labor_growth_decomp.pdf')
    fig, ax = plot_labor_growth_decomp_single()
    set_labor_growth_decomp_single(ax)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'labor_growth_decomp_ee.pdf')

if __name__ == "__main__":
    main()
