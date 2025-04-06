"""
Draw Firm Entry rate based on Tax & Law data
"""

import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)


def plot_firm_entry_rate(df):
    fig, ax = plt.subplots()

    entry = df.eval('setup/ALL')*100
    entry.plot(ax=ax)
    exit_ = entry - df.ALL.pct_change()*100
    exit_.plot(ax=ax)

    return fig, ax


def set_firm_entry_rate(ax):
    ax.set_xlim(1939, 2008)
    ax.set_xlabel('')
    ax.set_ylabel('Entry Rate (%)')
    ax.legend(['Entry Rate', 'Exit Rate'], loc='best', frameon=False)


def main():
    dfh = pd.read_pickle(input_path+'Offical_TaxLaw_Corporation.pkl')

    set_style()

    # plot entry rate by org
    fig, ax = plot_firm_entry_rate(dfh)
    set_firm_entry_rate(ax)
    set_size(fig, fraction=0.7, row=1)
    save_fig(fig, 'entry_rate_firm.pdf')


if __name__ == "__main__":
    main()
