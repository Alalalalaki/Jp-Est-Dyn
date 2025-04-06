"""
Draw Subcontracting rate based on BSMSA data
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)
from Figure_avgsize_trend import plot_avgsize_trend_by_age

dfs = pd.read_pickle(input_path+'Offical_Subcontract.pkl')


def plot_subcontract_manu_rate(df=dfs,):
    fig, ax = plt.subplots()
    df.query('ind == "ALL"').plot('year', 'subcontract_ratio', ax=ax, marker='o')
    ax2 = ax.twinx()
    plot_avgsize_trend_by_age(ages=["0~5"], ind="製造業", _ax=ax2)  # ind="NALL"

    return fig, ax, ax2


def set_subcontract_manu_rate(ax, ax2):
    # ax.set_ylim(40,70)
    ax.set_xlabel('')
    ax.set_ylabel('Subcontractor Ratio (%)')

    # ax2.set_ylim(10, 16)
    ax2.get_lines()[0].set(color=get_colors()[1],)
    ax2.set_ylabel('Avg. Est. Size (Employee)')

    ax.legend([ax.get_lines()[0], ax2.get_lines()[0]],
              ['Subcontractor Ratio', "Avg. Size of Age 0-5"],
              loc='best', frameon=False)


def main():

    set_style()

    # plot subcontract ratio manufacturing
    fig, ax, ax2 = plot_subcontract_manu_rate()
    set_subcontract_manu_rate(ax, ax2)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'subcontract_ratio_manu.pdf')


if __name__ == "__main__":
    main()
