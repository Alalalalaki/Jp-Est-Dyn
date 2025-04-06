"""
This scrpit is to clean EEC 3-digit industry data both from eStat and by manual collecting
The code is copied from EEC_clean with minor adjustment
"""

import os
import glob
import numpy as np
import pandas as pd

from EEC_clean import input_path_est, input_path_m, output_path, clean_estat, clean_manual, clean_age, clean_estat_1996, clean_variable, clean_control, add_size_cohort, add_age_cohort, add_AFF_NALL, add_combined_industry

"""
Note on Industry

Manufacturing: (base 2011)
  - 食料品製造業 (in 1981 食料品・たばこ製造業 i.e. combined to one industry)
  - 飲料・たばこ・飼料製造業 (in 1966 simply たばこ製造業; in 1981 not exit)
  - 繊維工業
  - 衣服・その他の繊維製品製造業
  - 木材・木製品製造業（家具を除く）
  - 家具・装備品製造業
  - パルプ・紙・紙加工品製造業
  - 出版・印刷・同関連産業
  - 化学工業
  - 石油製品・石炭製品製造業
  - プラスチック製品製造業(別掲を除く) (not in 1966 and 1981)
  - ゴム製品製造業
  - なめし革・同製品・毛皮製造業 (in 1966 皮革・同製品製造業)
  - 窯業・土石製品製造業
  - 鉄鋼業
  - 非鉄金属製造業
  - 金属製品製造業
  - 一般機械器具製造業 (in 1966 called 機械製造業(電気機械器具を除く))
  - 電気機械器具製造業
  - 輸送用機械器具製造業
  - 精密機械器具製造業
  - 武器製造業
  - その他の製造業

"""


def clean_industry_ind3(df):
    # deal with the ind name difference in different periods
    # here only tackle with manufacturing
    df = df.copy()
    ind = (df.industry
           .replace('食料品・たばこ製造業', '食料品製造業')  # not sure about do this
           .replace('繊維工業（衣服，その他の繊維製品を除く）', '繊維工業')
           .replace('繊維工業（衣服・その他繊維製品を除く）', '繊維工業')
           .replace('出版・印刷・同関連業', '出版・印刷・同関連産業')
           .replace('なめしかわ・同製品・毛皮製造業', 'なめし革・同製品・毛皮製造業')
           .replace('皮革・同製品製造業', 'なめし革・同製品・毛皮製造業')
           .replace('機械製造業', '一般機械器具製造業')
           .replace('計量器・測定器・測量機械・医療機械理化学機械・光学機械・時計製造業', '精密機械器具製造業')
           )
    df = df.assign(industry=ind)
    return df


def clean_eStat_data():

    files = sorted(glob.glob(input_path_est + '[0-9]*_産業_*.pkl'))
    _len = len(input_path_est)
    files_year = [i[_len:_len+4] for i in files]
    files_tail = [i[-8:-4] for i in files]

    dfs = pd.DataFrame()

    # 1981, 1986, 1991: two files each year
    var_keys = {"事業所数": 'num', "従業者数": 'employment'}
    for yr in ['1981', '1986', '1991']:
        for i, (y, v) in enumerate(zip(files_year, files_tail)):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_estat, var_keys[v])
                df = df.pipe(clean_industry_ind3)
                if y in ['1981', '1986']:
                    df = df.pipe(add_AFF_NALL)
                df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True)
                print(f'Cleaned {y}!')

    # 1996
    for i, y, in enumerate(files_year):
        if y == "1996":
            df = pd.read_pickle(files[i]).pipe(clean_estat_1996).pipe(clean_estat)
            df = df.pipe(clean_industry_ind3)
            df = df.pipe(add_size_cohort).pipe(add_age_cohort)
            dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
            print(f'Cleaned {y}!')

    # 2001, 2006
    for yr in ['2001', '2004', '2006']:
        for i, y, in enumerate(files_year):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_estat).pipe(clean_variable)
                df = df.pipe(clean_industry_ind3)
                if y in ['2004', '2006']:
                    df = df.pipe(add_combined_industry)
                df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
                print(f'Cleaned {y}!')

    dfs = dfs.drop_duplicates()
    return dfs


def clean_manual_data():
    files = sorted(glob.glob(input_path_m + '[0-9]*_産業_*.csv'))
    _len = len(input_path_m)
    files_year = [i[_len:_len+4] for i in files]

    dfs = pd.DataFrame()

    # 1966
    for f, y in zip(files, files_year):
        df = pd.read_csv(f)
        if y in ['1966']:
            df = df.query('経営組織 not in ["ALL","株式会社"]')  # the data including some unnecessary orgs
        df = df.pipe(clean_manual, int(y))
        df = df.pipe(clean_industry_ind3)
        if y in ['1966']:
            df = df.assign(age="ALL")
        else:
            df = df.pipe(clean_age, easy_mode=True)
        df = df.pipe(add_size_cohort).pipe(add_age_cohort)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        print(f'Cleaned {y}!')
    dfs = dfs.drop_duplicates()
    return dfs


def main():
    df_estat = clean_eStat_data()
    df_estat = (df_estat.set_index(['year', 'period', 'organization', 'industry',
                                    'size', 'establishment', 'age', 'var']).filter(["value"])
                .unstack().droplevel(0, axis=1).reset_index().rename_axis(None, axis=1)
                )
    df_manual = clean_manual_data()

    df = (pd.concat([df_estat, df_manual], ignore_index=True, sort=False)
          .assign(year=lambda x: x.year.astype(int)))
    df.to_pickle(output_path + 'EEC_Establishment_ind.pkl')


if __name__ == "__main__":
    main()
