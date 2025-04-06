"""
This scrpit is to clean Official data in excel files
"""

import numpy as np
import pandas as pd
from util import z2h
from EEC_clean import clean_industry, clean_organization, clean_size, add_combined_industry

input_path_E = "../Input/data_in_offical_documents/EntryExitData/"
input_path_H = "../Input/data_in_offical_documents/HistoricalData/"
output_path = "../Output/"


def clean_SME_EEC():
    df = pd.read_excel(input_path_E+'ChushoHakusyo_2011_fig3-1-2_EntryExitRate_census_appendix.xls',
                       index=False, header=2, skipfooter=7)
    df.columns = ['year', 'period_census', 'num_begin', 'num_open', 'period_open',
                  'num_growth', 'num_growth_per_year', 'num_open_per_year', 'num_exit_per_year',
                  'open_rate', 'exit_rate']
    df = df[df.year.str.contains('\d{2}～\d{2}', na=False)]
    df = df.assign(
        year=(lambda x: x.year.str.replace('\s', '')
              .str.split('～', expand=True)
              .apply(lambda x: '19' + x)
              .assign(temp=lambda x: x[0] + '~' + x[1]).temp
              ),
        beginyear=lambda x: x.year.str[:4],
        endyear=lambda x: x.year.str[-4:],
        organization=(['企業']*9+['個人']*9+['会社']*9+['事業所']*14),
        industry='NALL',).apply(pd.to_numeric, errors='ignore')
    return df


def historical_EEC_extract(
        filename, usecols, colnames, varname, valuename, table_id, header=3, skipfooter=10, mode2006=False,
        dropyear=None, govindcode="M ",):
    df = (pd.read_excel(input_path_H+filename, index=False,
                        usecols=usecols, names=colnames,
                        header=header, skipfooter=skipfooter, )
          .replace('\n', '', regex=True)
          )
    if not mode2006:
        df = df.assign(industry=lambda x: x.industry.replace('^[^A-Z]', np.nan, regex=True).ffill(),
                       year=lambda x: x.year.astype(str))
        mask_ind = df.industry.str.contains(govindcode, na=False)  # drop 公務
        mask_year = df.year.str.contains('^\d+', na=False)
        if dropyear:
            mask_year = (mask_year & ~df.year.str.contains(dropyear, na=False))
        df = (df.loc[(~mask_ind & mask_year)]
              .melt(['industry', 'year'], var_name=varname, )
              .assign(var=valuename, table_id=table_id)
              )
    else:
        mask_ind1 = df.industry.str.contains('^[A-Z]', na=False)
        mask_ind2 = df.industry.str.contains('R\s|groups', na=False)  # drop 公務
        df = (df.loc[(mask_ind1 & ~mask_ind2)]
              .melt(['industry'], var_name=varname, )
              .assign(var=valuename, year="2006", table_id=table_id)
              )
    return df


def historical_EEC():

    dfs = pd.DataFrame()

    # 6-2-a
    filename = '06-02-a_産業大分類，経営組織別事業所数及び従業者数.xls'
    table_id = "06-02"
    cols = ['industry', 'year', 'TALL', 'ALL', 'individual_proprietorship', 'corporations']
    col_num = [0, 1, 2, 3, 4, 5]
    col_employment = [0, 1, 7, 8, 9, 10]
    for n, c in zip(['num', 'employment'], [col_num, col_employment]):
        df = historical_EEC_extract(filename, usecols=c, colnames=cols, table_id=table_id,
                                    varname='organization', valuename=n)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
    # 6-2-b
    filename = '06-02-b_産業大分類，経営組織別事業所数及び従業者数.xls'
    cols.remove('year')
    col_num = [0, 2, 3, 4, 5]
    col_employment = [0, 7, 8, 9, 10]
    for n, c in zip(['num', 'employment'], [col_num, col_employment]):
        df = historical_EEC_extract(filename, usecols=c, colnames=cols, table_id=table_id,
                                    varname='organization', valuename=n,
                                    mode2006=True, skipfooter=3)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # 6-3-a
    filename = '06-03-a_産業大分類，従業者規模別事業所数及び従業者数.xls'
    table_id = "06-03"
    cols = ['industry', 'year', 'ALL', '1~4', '5~9', '10~29', '30~49',
            '50~99', '100~299', '300+', 'dispatched_or_subcontracted']
    col_num = list(range(11))
    col_employment = [0, 1] + list(range(11, 20))
    for n, c in zip(['num', 'employment'], [col_num, col_employment]):
        df = historical_EEC_extract(filename, usecols=c, colnames=cols, table_id=table_id,
                                    varname='size', valuename=n)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
    # 6-3-b
    filename = '06-03-b_産業大分類，従業者規模別事業所数及び従業者数.xls'
    cols = ['industry', 'year', 'ALL', '1~4', '5~9', '10~19', '20~29', '30~49',
            '50~99', '100~199', '200~299', '300+', 'dispatched_or_subcontracted']
    col_num = list(range(13))
    col_employment = [0, 1] + list(range(13, 24))
    for n, c in zip(['num', 'employment'], [col_num, col_employment]):
        df = historical_EEC_extract(filename, usecols=c, colnames=cols, table_id=table_id,
                                    varname='size', valuename=n,
                                    dropyear="2001", govindcode="R ", skipfooter=3)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # 6-5-a
    filename = '06-05-a_産業大分類，従業上の地位別従業者数.xls'
    table_id = "06-05"
    cols = ['industry', 'year', 'ALL', 'individual_proprietors', 'unpaid_family_workers',
            'salaried_directors', 'employees', 'regular_employees', 'temporary_or_daily_employees']
    col_employment = [0, 1] + list(range(4, 11))
    df = historical_EEC_extract(filename, usecols=col_employment, colnames=cols, table_id=table_id,
                                varname='employee_status', valuename='employment')
    dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
    # 6-5-b
    filename = '06-05-b_産業大分類，従業上の地位別従業者数－民営.xls'
    cols.remove('year')
    col_employment = [0] + list(range(3, 10))
    df = historical_EEC_extract(filename, usecols=col_employment, colnames=cols, table_id=table_id,
                                varname='employee_status', valuename='employment',
                                mode2006=True, skipfooter=3)
    dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # # 6-9 (information is not enough)
    # filename = '06-09_経営組織別会社企業数.xls'
    # table_id = "06-09"

    return dfs


def clean_historical_EEC():
    df = historical_EEC()
    df = (df.applymap(z2h.str_z2h)
            .rename(columns={'industry': '産業', 'size': '規模', 'organization': '組織'})
            .pipe(clean_industry).pipe(clean_organization).pipe(clean_size)
            .assign(
                year=lambda x: x.year.astype(int),
                organization=lambda x: x.organization.fillna('ALL'),
                size=lambda x: x['size'].fillna('ALL'),
                employee_status=lambda x: x.employee_status.fillna('ALL'),
                value=lambda x: pd.to_numeric(x.value.replace('...', np.nan).replace('*', np.nan).replace('-', np.nan),
                                              errors='ignore'))
            .drop_duplicates()
            .set_index(['table_id', 'year', 'organization', 'industry', 'size', 'employee_status', 'var'])
            .unstack().droplevel(0, axis=1).reset_index().rename_axis(None, axis=1)
          )
    df_plus = pd.read_csv(input_path_H+'06-02_plus_company.csv').assign(employee_status="ALL")
    df = pd.concat([df, df_plus], ignore_index=True, sort=False)
    df = pd.concat([df.query('year != 2006'),
                    df.query('year == 2006').pipe(add_combined_industry)],
                   ignore_index=True,)
    return df


def main():
    clean_SME_EEC().to_pickle(output_path+'Offical_SME_EEC_EERate.pkl')
    clean_historical_EEC().to_pickle(output_path+'Offical_Historical_EEC.pkl')


if __name__ == "__main__":
    main()
