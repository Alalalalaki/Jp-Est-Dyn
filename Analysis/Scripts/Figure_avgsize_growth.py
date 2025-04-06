"""
Draw Average Size Growth over time for Some certain Cohorts based on EEC data
"""

import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import (input_path, get_colors, get_greys, get_linestyle, get_markerstyle,
                            set_style, set_axes, set_size, save_fig)
from Data_General import clean_df


def plot_avgsize_growth_by_entry(df):
    org = "employer"
    years_1969 = [1969, 1972, 1975, 1978]
    cohorts_1969 = [
        ['0~2', '3~5', '6~8', ''],
        ['3~5', '6~8', '9~11', ''],
        # ['6~8', '9~11', '12~14', ''],
        # ['9~11', '12~14', '15~17', ''],
        ['6~11', '9~14', '12~17', ''],
        ['12~17', '15~20', '18~23', ''],
        ['18~24', '21~27', '24~30', ''],
        ['25+', '28+', '31+', '34+'],
    ]
    cohorts_1969_young = [
        ['0~2', '3~5', '6~8', ''],
        ['', '0~2', '3~5', ''],
        ['', '', '0~2', '3~5'],
    ]
    years_1981 = [1981, 1986, 1991, 1996, 2001, 2006]
    cohorts_1981 = [
        ['',      '',      '2~6',   '7~11',  '',      ''],
        ['',      '',      '',      '',      '2~6',  '7~11'],
        ['',      '',      '',      '2~11',  '7~16',  '12~21'],
        ['',      '2~11',  '7~16',  '12~21', '17~26', '22~31'],
        ['',      '12~21', '17~26', '22~31', '27~36', '32~41'],
        ['17~26', '22~31', '27~36', '32~41', '37~46', '42~51'],
    ]
    cohorts_1981_young = [
        ['1',      '6',      '',      '',      '',  ''],
        ['',      '1',      '6',      '',      '',  ''],
        ['',      '',      '1',      '6',      '',  ''],
        ['',      '',      '',      '1',      '6',  ''],
        ['',      '',      '',      '',      '1',  '6'],
        # ['',      '',      '2~6',   '7~11',  '',      ''],
        # ['',      '',      '',      '',      '2~6',  '7~11'],
    ]
    fig, axes = plt.subplots(2, 2)
    axes = axes.flatten(order='F')
    for years, cohorts, ax in zip([years_1969, years_1969, years_1981, years_1981],
                                  [cohorts_1969, cohorts_1969_young, cohorts_1981, cohorts_1981_young],
                                  axes):
        for ages in cohorts:
            ages_first = [a for a in ages if a != ""][0]
            cohort = pd.DataFrame()
            for year, age in zip(years, ages):
                cohort = pd.concat(
                    (cohort, df.query('organization == @org & industry == "NALL" & size == "ALL" ')
                     .query('year == @year & age == @age ')
                     )
                )
            (cohort.eval('avg_size = employment / num')
                .assign(exit=lambda x: x.num.pct_change()*100)
             ).plot('year', 'avg_size', ax=ax, label=ages_first.replace('~', '-'),
                    marker='o', )  # markerfacecolor='none', title=year
    return fig, axes


def set_avgsize_growth_by_entry(axes, fig):
    for i, ax in enumerate(axes):
        ax.set_xlabel('')
        ax.legend(loc='best', frameon=False, handlelength=0.1)
        if i <= 1:
            ax.set_xticks([1969, 1972, 1975, 1978])
            ax.set_xlim(1968.5, 1978.5)
        else:
            ax.set_xticks([1981, 1986, 1991, 1996, 2001, 2006])
            ax.set_xlim(1980, 2007)
        if i % 2 == 1:
            ax.set_ylim(10, 18)
        # else:
        #     ax.set_ylim(12, 36)
    fig.text(0.25, 1, '1969-1978', horizontalalignment='center', fontsize=12)
    fig.text(0.75, 1, '1981-2006', horizontalalignment='center', fontsize=12)


def main():
    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

    set_style()

    # plot entry rate by org
    fig, axes = plot_avgsize_growth_by_entry(dfa)
    set_avgsize_growth_by_entry(axes, fig)
    set_axes(axes)
    set_size(fig, fraction=0.9, row=1.2)
    save_fig(fig, 'avgsize_growth_by_entry.pdf')


if __name__ == "__main__":
    main()
