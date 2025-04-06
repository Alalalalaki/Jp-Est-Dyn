"""
Draw Wage Difference in Manufacturing based on Manufacturing data
"""

import pandas as pd
import matplotlib.pyplot as plt
from Figure_General import (input_path, get_colors, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig,)



def plot_wage_gap(df, var='wage_per_regem', base='1000+', wage_regem_combine_wage_em=False,
                  abnormal_years=[1971]):
    fig, ax = plt.subplots()
    if wage_regem_combine_wage_em:
        df = df.assign(wage_per_regem=df.wage_per_regem.fillna(df.wage_per_em))
    dt = df.query('industry == "ALL"').pivot('year', 'size', var)
    # start_year = min(dt.index.unique())
    cols = ['4~9', '10~19', '20~29', '30~49', '50~99', '100~199',
            '200~299', '300~499', '500~999', '1000+']  # '1~3',
    cols.remove(base)
    dt = dt.query('year not in @abnormal_years')
    print(f'Caution: Data in {abnormal_years} are somehow abnormal thus dropped.')
    (dt
        .apply(lambda x: x/dt[base])
        .assign(year=lambda x: x.index)
        .loc[:, cols[::-1]]
        .dropna(how='all', axis=1)
        .interpolate(limit=3, limit_area='inside')
     ).plot(ax=ax)

    return fig, ax

def set_wage_gap(ax, base):
    # ax.set_xlim(1947, 2017)
    ax.set_xlabel('')
    ax.set_ylabel(f'Average Real Wage ({base} = 1)')
    ax.legend(loc='best', frameon=False, bbox_to_anchor=(1, .8), handlelength=0.5,)  # title="Size"


def main():
    dfs = pd.read_pickle(input_path+'MC_size.pkl')

    set_style()

    # plot_wage_gap
    base = '10~19'
    fig, ax = plot_wage_gap(dfs, var='wage_per_em', base=base)
    set_wage_gap(ax, base=base)
    set_axes([ax])
    set_size(fig, fraction=0.7,)
    save_fig(fig, 'wage_gap_manu.pdf')


if __name__ == "__main__":
    main()
