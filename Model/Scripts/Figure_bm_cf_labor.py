"""
This code plots the counterfactural result of labor growth change
"""

import pandas as pd
import matplotlib.pyplot as plt

import project_path
from Figure_General import set_style, set_axes, set_size, save_fig, get_colors
from Figure_entry_rate import plot_entry_rate
from Figure_labor_growth import plot_labor_growth_lc
from Figure_aggregate_trend import plot_avgsize_trend_by_org

from counterfactural_labor import calculate_transition_path


def plot_counterfactural_entry(model_stat, show_labor_trend=False):
    fig, ax = plt.subplots()
    model_stat.entry_rate.plot(ax=ax)
    plot_entry_rate(orgs=['employer'], pre_period=False, pre_period_interpolate=True, _ax=ax)
    if show_labor_trend:
        model_stat.iloc[:, -1].plot(color=get_colors()[2], style=[':'], ax=ax)
    return fig, ax


def set_counterfactural_entry(ax, labels=["Model", "Data", ]):
    # ax.get_lines()[1].set(markerfacecolor="None", linestyle="--")
    ax.get_lines()[2].set(color=get_colors()[1])
    ax.get_lines()[2].set(label='_nolegend_')
    ax.set_xlabel(None)
    ax.set_ylabel('Entry Rate (%)')
    ax.legend(labels, loc='best', frameon=False)


def plot_counterfactural_exit_avgsize(model_stat):
    fig, axes = plt.subplots(1, 2)

    model_stat.exit_rate.plot(ax=axes[0])
    plot_entry_rate(mode='exit_rate', orgs=['employer'],
                    pre_period=False, pre_period_interpolate=True, _ax=axes[0])

    model_stat.avgsize.plot(ax=axes[1])
    plot_avgsize_trend_by_org(orgs=["company"], pre_period_interpolate=True, _ax=axes[1])

    return fig, axes


def set_counterfactural_exit_avgsize(axes):
    for ax in axes:
        # ax.get_lines()[1].set(markerfacecolor="None", linestyle="--")
        ax.get_lines()[2].set(color=get_colors()[1])
        ax.set_xlabel(None)
        ax.legend(["Model", "Data"], loc='best', frameon=False)
    axes[0].set(ylabel='Exit Rate (%)', title="Exit Rate")
    axes[1].set(ylabel='Avg. Est. Size (Employee)', title="Average Size")


def main():

    labor_supply = "employee_NALL" # "labor_force"

    transition_path_stat_long, _ = calculate_transition_path(labor_supply=labor_supply)  # year_end=2018
    transition_path_stat = transition_path_stat_long.loc[:2006, :]

    set_style()

    # plot counterfactural result on entry rate
    fig, ax = plot_counterfactural_entry(transition_path_stat)  # 2001
    set_counterfactural_entry(ax)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_counterfactural_labor_entry.pdf')

    # plot counterfactural result on entry rate with labor growth trend
    fig, ax = plot_counterfactural_entry(transition_path_stat, show_labor_trend=True)  # 2001
    set_counterfactural_entry(ax, labels=["Model", "Data: Entry Rate", "Data: Labor Growth Rate"])
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_counterfactural_labor_entry_labor.pdf')

    # plot counterfactural result on entry rate
    fig, axes = plot_counterfactural_exit_avgsize(transition_path_stat)  # 2001
    set_counterfactural_exit_avgsize(axes)
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_counterfactural_labor_exit_avgsize.pdf')

    # use hp filtered lanpr grpwtj
    transition_path_stat_long, _ = calculate_transition_path(labor_supply=labor_supply+"_hp")  # year_end=2018
    transition_path_stat = transition_path_stat_long.loc[:2006, :]

    fig, ax = plot_counterfactural_entry(transition_path_stat)  # 2001
    set_counterfactural_entry(ax, labels=["Model (labor force with HP filter)", "Data", ])
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_counterfactural_labor_entry_hp.pdf')

    fig, ax = plot_counterfactural_entry(transition_path_stat, show_labor_trend=True)  # 2001
    set_counterfactural_entry(ax, labels=["Model", "Data: Entry Rate", "Data: Labor Growth Rate (HP filter)"])
    set_size(fig, fraction=0.7, row=1,)
    save_fig(fig, 'benchmark_counterfactural_labor_entry_labor_hp.pdf')


if __name__ == "__main__":
    main()
