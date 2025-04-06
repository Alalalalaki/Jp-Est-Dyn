"""
Table: Decompose Entry rate based on EEC data
"""

import pandas as pd

from Figure_General import input_path
from Data_General import clean_df, interpolated_dfh
from Figure_entry_rate import calculate_entry_exit_rate

output_path = "../Tables/"


def table_decompose_entry(df):

    # entry, exit and their gap
    entry = pd.DataFrame()
    orgs = ['ALL', 'employer', 'nonemployer', ]
    for org in orgs:
        e = calculate_entry_exit_rate(df, '1', org, 'NALL')
        e = e[['denominator_year', 'entry_rate', 'exit_rate']].eval('organization = @org')
        entry = pd.concat([entry, e])

    e = calculate_entry_exit_rate(df, '0~3', 'ALL', 'NALL').query('year == 1957')
    e = e[['denominator_year', 'entry_rate', 'exit_rate']].eval('organization = "ALL"')
    entry = pd.concat([entry, e]).rename(columns={
        'entry_rate': 'entry rate', 'exit_rate': 'exit rate'})
    years = [1952, 1954, 1956, 1959, 1962, 1965] + sorted(entry.denominator_year.unique())[1:]

    # growth of avg size and labor force
    orgs = ['ALL', 'employer', 'corporations', 'nonemployer', ]
    growth = pd.DataFrame()
    for org in orgs:
        g = (interpolated_dfh(org=org, ind="NALL", size="ALL").assign(
            net_growth=lambda x: x.num.pct_change()*100,
            employment_growth=lambda x: x.employment.pct_change()*100,
            avg_size=lambda x: x.employment/x.num,
            avg_size_growth=lambda x: x.avg_size.pct_change()*100,
        ))
        g = g[['net_growth', 'employment_growth', 'avg_size_growth']].eval('organization = @org')
        growth = pd.concat([growth, g])
    growth = growth.reset_index().query('year in @years').rename(columns={
        'net_growth': 'net growth', 'employment_growth': 'employment growth',
        'avg_size_growth': 'avg size growth'})

    # combine and arrange
    decom = pd.merge(entry, growth, how='outer', left_on=['denominator_year', 'organization'],
                     right_on=['year', 'organization']).drop('denominator_year', axis=1)
    decom = decom.set_index(['organization', 'year']).stack().swaplevel().unstack()
    decom = decom.applymap('{:.1f}'.format).replace('nan', '-')
    decom = pd.concat([decom.loc[['ALL', 'employer']],
                       decom.loc[['corporations']],
                       decom.loc[['nonemployer']]
                       ])
    decom.index = decom.index.set_levels(['Total (Private)', 'Corporation', 'Employer',  'Nonemployer'], level=0)
    return decom, years


def main():
    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)
    decom, years = table_decompose_entry(dfa)
    decom = decom.rename_axis([None, None]).rename_axis(None, axis=1)  # drop index and column name
    years = [i for i in years if i not in [1954]]  # a bit too long thus drop 1954
    decom.to_latex(output_path+'decompose_entry.tex',
                   columns=years,
                   col_space=1,
                   column_format='l'*2+'c'*len(years),
                   multirow=True
                   )


if __name__ == "__main__":
    main()
