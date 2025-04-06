"""
Draw Wage Growth Rate based on Labor data
"""

import pandas as pd
import matplotlib.pyplot as plt
from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig,)


def plot_wage_growth(df, ):
    fig, ax = plt.subplots()
    wage = (df[['wage', 'inflation', ]]
            .eval('real_wage = wage / inflation * 100')
            .assign(real_wage_growth=lambda x: x.real_wage.pct_change()*100)
            .reset_index()
            )
    wage.plot('year', 'real_wage_growth', ax=ax)
    return fig, ax


def set_wage_growth(ax):
    ax.set_xlim(1947, 2017)
    ax.set_xlabel('')
    ax.legend(['Real Wage Growth Rate', ], loc='best', frameon=False)

def main():
    dfl = pd.read_pickle(input_path+'Offical_JIL_LaborSupply.pkl')

    set_style()

    # plot_wage_growth
    fig, ax = plot_wage_growth(dfl,)
    set_wage_growth(ax)
    set_size(fig, fraction=0.7,)
    save_fig(fig, 'wage_growth.pdf')


if __name__ == "__main__":
    main()
