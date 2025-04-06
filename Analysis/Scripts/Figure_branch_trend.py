

import pandas as pd
import matplotlib.pyplot as plt

from Figure_General import input_path, set_style, set_size, save_fig
from Data_General import clean_df, get_industry, get_industry_name


dfb = pd.read_pickle(input_path+'EEC_Establishment_branch.pkl').pipe(clean_df)

def plot_branch_trend(df = dfb):

    dt_num = df.query("industry == 'NALL' & organization == 'employer'").pivot(index="year", columns="control", values="num")
    dt_num = dt_num.eval("firm = head + sole").eval("est_per_firm = ALL/firm")

    dt_emp = df.query("industry == 'NALL' & organization == 'employer'").pivot(index="year", columns="control", values="employment")

    fig, axes = plt.subplots(2, 3)
    axes = axes.flatten()

    (dt_emp.ALL / dt_num.firm).plot(ax=axes[0], legend=False, title="Avg. Size per Firm")
    dt_num.est_per_firm.plot(ax=axes[1], legend=False, color="C1",title="Avg. Est. per Firm")
    (dt_num["head"] / dt_num.firm).plot(ax=axes[2], legend=False, color="C1", title="Share of Multi-Est. Firm")
    # ((dt_num["head"]+dt_num.branch) / dt_num["head"]).plot(ax=axes[2], legend=False, color="C1", title="Avg. Est. per Multi-Est. Firm")
    (dt_emp.sole / dt_num.sole).plot(ax=axes[3], legend=False, title="Avg. Size of Single-Est.")
    (dt_emp["head"] / dt_num["head"]).plot(ax=axes[4], legend=False, title="Avg. Size of Head-Est.")
    (dt_emp.branch / dt_num.branch).plot(ax=axes[5], legend=False, title="Avg. Size of Branch-Est.")

    for ax in axes:
        ax.set_xlim(1980, 2007)
        ax.set_xlabel('')
    axes[0].set_ylabel('Employee')
    axes[1].set_ylabel('Establishment')
    # axes[2].set_ylabel('Establishment')
    axes[2].set_ylabel('Percent')
    axes[3].set_ylabel('Employee')
    axes[4].set_ylabel('Employee')
    axes[5].set_ylabel('Employee')

    return fig, axes

def main():

    set_style(marker_cycle=True)

    fig, ax = plot_branch_trend()
    # set_size(fig, fraction=0.7, row=1)
    set_size(fig, fraction=1, row=1.2)
    save_fig(fig, 'branch_trend.pdf')



if __name__ == "__main__":
    main()
