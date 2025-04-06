"""
This scrpit is to clean MC data from downloaded excel files or by manual collecting data
"""

import os
import glob
import numpy as np
import pandas as pd

"""
Note:
    Size id and Industry id seem to changes over time, thus are not helpful except used as some verification.
"""


input_path_s = "../Input/Manufacturing_Census/SAN/"
input_path_sm = "../Input/Manufacturing_Census/SAN_manual/"
output_path = "../Output/"


def clean_avg_excel(df, file, year,):
    colname = ['ind_id', 'industry', 'size_id', 'size', ]
    if '30人' in file:
        value_cols = ['employment_per_est', 'revenue_per_est', 'output_per_est',
                      'va_per_est', 'inventory_per_est', 'investment_per_est',
                      'revenue_per_em', 'va_per_em', 'wage_per_regem']
        sizeall = '30+'
    elif '29人' in file:
        value_cols = ['employment_per_est', 'revenue_per_est', 'va_per_est',
                      'wage_per_em', 'revenue_per_em', 'va_per_em']
        if year <= 1980:
            sizeall = '1~29'
        else:
            sizeall = '4~29'
    else:
        raise ValueError('Neither 30人 nor 29人 in file name.')
    colname = colname + value_cols
    mask_col = ((df != 0) & (~df.isna()) & (df != year) & (~df.isin(["調査年", "年次"]))).any(axis=0)
    df = df.loc[:, mask_col]
    df.columns = colname
    mask_row = (~df.size_id.isna())
    df = df.loc[mask_row, :].assign(year=year).drop(['ind_id', 'size_id'], axis=1)
    df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    df = df.assign(size=lambda x: (x['size']
                                   .str.replace('～', '~')
                                   .str.replace('人|\s', '')
                                   .str.replace('計|合計', sizeall)
                                   .str.replace('以上', '+')),
                   industry=lambda x: (x.industry
                                       .str.replace('\s', '')
                                       .str.replace('合計|製造業計|従業者数', 'ALL'))
                   )
    return df


def clean_avg():

    # average data with size cohorts in excels files for 1979-2007
    folders = sorted(glob.glob(input_path_s+'*'), key=lambda x: x[-4:])
    years = [int(i[-4:]) for i in folders]
    dfs = pd.DataFrame()
    for f, y in zip(folders, years):
        if (y >= 1979) & (y < 2001):
            files = glob.glob(f+'/*人当*.xls')
            files = [f for f in files if '細分' not in f]
            for file in files:
                df = pd.read_excel(file, index=False, header=None, na_values=['x'])
                df = clean_avg_excel(df, file=file, year=y)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        if y >= 2001:
            files = glob.glob(f+'/*統計表*.xls')
            files = [f for f in files if '英語' not in f]
            dfexcel = pd.ExcelFile(files[0])
            sheets = dfexcel.sheet_names
            if '5120' in sheets:
                files = ['5120', '5220']
            elif '4120' in sheets:
                files = ['4120', '4220']
            else:
                raise ValueError('Neither 4120 or 5120 in sheets.')
            filemap = {'5120': '30人', '4120': '30人', '5220': '29人', '4220': '29人'}
            for file in files:
                df = dfexcel.parse(file, index=False, header=None, na_values=['x', 'X'])
                df = clean_avg_excel(df, file=filemap[file], year=y)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # average data with size cohorts in manual file
    file = input_path_sm + "1事業所当り及び従業者1人当り統計表.csv"
    df = pd.read_csv(file)
    df = df.assign(size=lambda x: x["size"].str.replace('1000~', '1000+'))
    df.columns = ['year', 'industry', 'size',
                  'employment_per_est', 'revenue_per_est', 'output_per_est',
                  'va_per_est', 'inventory_per_est', 'investment_per_est',
                  'revenue_per_em', 'va_per_em', 'wage_per_regem', 'wage_per_em']
    dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    return dfs


def clean_size_excel(df, year,):
    colname = ['ind_id', 'industry', 'size_id', 'size', ]
    value_cols = ['num', 'employment', 'regular_employment',
                  'wage', 'material', 'revenue', 'output', 'va']
    if year < 2002:
        colname = colname + value_cols
        mask_col = ((df != 0) & (~df.isna())).any(axis=0)
    elif year >= 2002:
        colname = colname + ['year'] + value_cols
        mask_col = df.isna().sum(axis=0) < (0.95 * len(df))
    df = df.loc[:, mask_col]
    df.columns = colname
    if year < 2002:
        mask_row = (~df.size_id.isna() & df['size'].str.contains('人|計'))
    elif year >= 2002:
        mask_row = (~df.size_id.isna()) & (df.year == year)
    if year < 2001:
        mask_row_industry = (df.ind_id.str[-2:] == '00')
    elif year >= 2001:
        mask_row_industry = ((pd.to_numeric(df.ind_id, errors='coerce') % 100) == 0)
    df = (df.loc[(mask_row & mask_row_industry), :]
            .assign(year=year)
            .drop(['ind_id', 'size_id'], axis=1)
          )
    df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    if year > 1980:
        sizeall = '4+'
    elif year > 1962:
        sizeall = '1+'
    df = df.assign(size=lambda x: (x['size']
                                   .str.replace('～', '~')
                                   .str.replace('人|\s', '')
                                   .str.replace('計|合計', sizeall)
                                   .str.replace('以上', '+')),
                   industry=lambda x: (x.industry
                                       .str.replace('\s', '')
                                       .str.replace('合計|製造業計|従業者数', 'ALL'))
                   )
    return df


def clean_size():

    # data in size cohorts in excels files for 1979-2007
    folders = sorted(glob.glob(input_path_s+'*'), key=lambda x: x[-4:])
    years = [int(i[-4:]) for i in folders]
    dfs = pd.DataFrame()
    for f, y in zip(folders, years):
        if (y >= 1979) & (y < 2001):
            files = glob.glob(f+'/*規模別統計表*.xls')
            files = [f for f in files if '(2)' not in f]
            for file in files:
                df = pd.read_excel(file, index=False, header=None, na_values=['x', '-', '－'])
                df = clean_size_excel(df, year=y)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        if y >= 2001:
            files = glob.glob(f+'/*統計表*.xls')
            files = [f for f in files if '英語' not in f]
            dfexcel = pd.ExcelFile(files[0])
            df = dfexcel.parse('2100', index=False, header=None, na_values=['x', 'X', '-', '－'])
            df = clean_size_excel(df, year=y)
            dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # data in size cohorts in manual file
    file = input_path_sm + "従業者規模別統計表.csv"
    df = pd.read_csv(file)
    cols = ['year', 'industry', 'size',
            'num', 'employment', 'regular_employment',
            'wage', 'material', 'revenue', 'output', 'va',
            'inventory', 'investment']
    df.columns = cols
    df = df.assign(size=lambda x: x["size"].str.replace('1000~', '1000+'))
    df.loc[df.year <= 1959, cols[6:]] = df.loc[df.year <= 1959, cols[6:]] / 1000  # adjust for unit
    dfs = pd.concat([dfs, df], ignore_index=True, sort=False)

    # adjust for 1981 regular employment
    dfs.loc[dfs.year == 1951, 'regular_employment'] = dfs.loc[dfs.year == 1951, 'regular_employment']/12

    return dfs


def clean_1_to_3_excel(df, year,):
    colname = ['ind_id', 'industry', ]
    value_cols = ['num', 'employment',
                  'wage', 'material', 'revenue', 'va']
    if str(year)[-1] in ['0', '3', '5', '8']:
        colname = colname + value_cols
    else:
        colname = colname + value_cols[:-1]
    mask_col = ((df != 0) & (~df.isna()) & (df != year) & (~df.isin(["調査年", "年次"]))).any(axis=0)
    df = df.loc[:, mask_col]
    df.columns = colname
    df = df.assign(ind_id=lambda x: x.ind_id.astype(str))
    mask_row_industry = (df.ind_id.str.contains('^0$|00$'))
    df = (df.loc[mask_row_industry, :]
            .assign(year=year)
            .assign(size='1~3')
            .drop(['ind_id', ], axis=1)
          )
    df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    df = df.assign(industry=lambda x: (x.industry
                                       .str.replace('\s', '')
                                       .str.replace('合計|製造業計|従業者数', 'ALL'))
                   )
    return df


def clean_1_to_3():
    # data 1-3 employment statistics in excels files for 1980-2007
    folders = sorted(glob.glob(input_path_s+'*'), key=lambda x: x[-4:])
    years = [int(i[-4:]) for i in folders]
    dfs = pd.DataFrame()
    for f, y in zip(folders, years):
        if (y >= 1981) & (y < 2001):
            files = glob.glob(f+'/*3人*.xls')
            files = sorted([f for f in files if '都道府県' not in f])
            if str(y)[-1] in ['0', '3', '5', '8']:
                file = files[0]
                df = pd.read_excel(file, index=False, header=None, na_values=['x', '-', '－'])
                df = clean_1_to_3_excel(df, year=y)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        if y >= 2001:
            files = glob.glob(f+'/*統計表*.xls')
            files = [f for f in files if '英語' not in f]
            if str(y)[-1] in ['0', '3', '5', '8']:
                dfexcel = pd.ExcelFile(files[0])
                sheets = dfexcel.sheet_names
                if '5100' in sheets:
                    file = '5100'
                elif '4100' in sheets:
                    file = '4100'
                else:
                    raise ValueError('Neither 4100 or 5100 in sheets.')
                df = dfexcel.parse(file, index=False, header=None, na_values=['x', 'X', '-', '－'])
                df = clean_1_to_3_excel(df, year=y)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
    return dfs


def main():
    # clean_avg().to_pickle(output_path+'MC_avg.pkl')
    # size.merge(avg_size, how='outer', on=['year', 'industry', 'size'])
    size = clean_size()
    statistics_1_to_3 = clean_1_to_3()
    size = pd.concat([size, statistics_1_to_3], ignore_index=True, sort=False)
    size = (size
            .eval('wage_per_em = wage / employment')
            #    .eval('wage_per_regem = wage / regular_employment')
            .eval('revenue_per_em = revenue / employment')
            .eval('output_per_em = output / employment')
            .eval('va_per_em = va / employment')
            .eval('employment_per_est = employment / num')
            .eval('revenue_per_est = revenue / num')
            .eval('output_per_est = output / num')
            .eval('va_per_est = va / num')
            .eval('inventory_per_est = inventory / num')
            .eval('investment_per_est = investment / num')
            .eval('regular_employment_share = regular_employment / employment')
            )
    size.to_pickle(output_path+'MC_size.pkl')


if __name__ == "__main__":
    main()
