"""
This scrpit is to clean EC input data either from eStat.
The code is similar to clean_eStat_data in EEC_clean for 2001, 2004, 2006
"""

import os
import glob
import numpy as np
import pandas as pd

from EEC_clean import clean_estat, clean_variable, clean_control, add_combined_industry, add_size_cohort, add_age_cohort

"""
Note

Age:
    2009: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10~14, 15~24, 25+
Size:
    2009:

"""

input_path = "../Input/Economic_Census/"
output_path = "../Output/"


def drop_col(df, key_word="地域"):
    c_ = df.filter(like=key_word).squeeze()
    if not isinstance(c_, pd.DataFrame):
        df = df.drop(c_.name, axis=1)
    return df

def clean_industry_(df, y):
    ind = df.filter(like="産業").squeeze()
    if y == "2012":
        mask_2012 = ind.str.contains("内格付不能")
        df = df[~mask_2012]
    if y == "2016":
        mask_2016 = ind.str.contains("[A-Z][1-9]")
        df = df[~mask_2016]
    return df


def clean_eStat_data():
    files = sorted(glob.glob(input_path + '[0-9]*.pkl'))
    files = [i for i in files if '経営組織' in i]

    _len = len(input_path)
    files_year = [i[_len:_len+4] for i in files]

    dfs = pd.DataFrame()

    for i, y, in enumerate(files_year):
        df = (pd.read_pickle(files[i])
              .pipe(drop_col)
              .pipe(clean_industry_, y)
              .pipe(clean_estat)
              .pipe(clean_variable, key_word="表章項目")
              .pipe(clean_control, remove=False)
              .pipe(add_combined_industry)
              )
        # df = df.pipe(add_size_cohort).pipe(add_age_cohort)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        print(f'Cleaned {y}!')

    dfs = (dfs
           .drop_duplicates()
           .set_index(['year', 'period', 'organization', 'industry',
                       'size', 'establishment', 'age', 'control', 'var'])
           .unstack().droplevel(0, axis=1).reset_index().rename_axis(None, axis=1)
           )
    return dfs


def main():
    df = clean_eStat_data()
    df.to_pickle(output_path + 'EC_Establishment_age.pkl')


if __name__ == "__main__":
    main()
