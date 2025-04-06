"""
This scrpit is to clean EEC input data both from eStat and by manual collecting
Update: after the udpate of pandas, must add "regex=True" in str.replace(), although have had, not sure the original code still work or not
"""

import os
import glob
import numpy as np
import pandas as pd

"""
Note

Age:
    1957: 0~3, 3~6, 6~12, 12+ (add: 0~6) (note: 0~3=36m, 3~6=36m) (no organization or employment)
    1969: 0~3, 4~6, 7~9, 10~15, 16~24, 25+
    1969: 0, 1, 2, 3, 4, 5, 6~8, 9~11, 12~14, 15~17, 18~24, 25+ (add: 0~5, 3~5, 6~8, 9~11, 12~17) (集計. no size data)
    1972: 0, 1, 2, 3, 4, 5, 6~8, 9~11, 12~14, 15~17, 18~20, 21~27, 28+  (also: 0~2, 3~5,) (add: 6~11, 15~20)
    1975: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9~11, 12~14, 15~17, 18~20, 21~23, 24~30, 31+ (also: 0~2, 3~5, 6~8) (add: 0~5, 3~20, 21~30, 15~17, 18~23)
    1978: 0~2, 3~5, 6~23, 24~33, 34+
    1981: 0, 1, 2, 3, 4, 5, 6~8, 9~16, 17~26, 27~36, 37+,  (add: 0~5, 2~16, 9~26, 27+)
    1986: 0, 1, 2, 3, 4, 5, 6, 7~11, 12~21, 22~31, 32+  (add: 0~5, 2~11, 7~21, )
    1989: 0, 1, 2, 3, 4, 5~9, 10~14, 15~24, 25~34, 35+ (no organization or size or employment)
    1991: 0, 1, 2, 3, 4, 5, 6, 7~16, 17~26, 27~36, 37+  (add: 0~5, 2~6, 27+)
    1996: 0, 1, 2, 3, 4, 5, 6, 7~11, 12~21, 22~31, 32~41, 42+  (add: 0~5, 2~11, 32+)
    2001: 0, 1, 2, 3, 4, 5, 6, 7~16, 17~26, 27~36, 37~46, 47+  (add: 0~5, 2~6, 27+)
    2004: 0, 1, 2, 3, 4, 5~9, 10~19, 20~29, 30~39, 40~49, 50+  (add: 0~5, 2~4, )
    2006: 0, 1, 2, 3, 4, 5, 6, 7~11, 12~21, 22~31, 32~41, 42~51, 52+  (add: 0~5, 4~6, 32+, )

Size:
    1957: 1, 2~4, 5~9, 10~29, 30~99, 100+
    1969: 1~4, 5~9, 10~29, 30~49, 50~99, 100~299, 300+, (報告, 集計age have no size data)
    1972: 1~4, 5~9, 10~19, 20~29, 30~49, 50~99, 100~199, 200~299, 300+,
    1975: ""
    1978: ""
    1981: "" + 1, 2, 3, 4
    1986: ""
    1989: no size data
    1991: ""
    1996: ""
    2001: "" + 派遣・下請従業者のみ
    2004: "" - 1, 2, 3, 4,
    2006: ""

"""

input_path_est = "../Input/Establishment_and_Enterprise_Census/eStat/establishment/"
input_path_ent = "../Input/Establishment_and_Enterprise_Census/eStat/enterprise/"
input_path_m = "../Input/Establishment_and_Enterprise_Census/manual/"
output_path = "../Output/"


def assign_year(df):
    df = df.copy()
    df = df.assign(year=df.period // 100)
    return df


def clean_organization(df):
    df = df.copy()
    cols = df.columns.values
    # clean string and change column name
    org = df.filter(like="組織").squeeze()
    if isinstance(org, pd.DataFrame):
        if 'organization' not in cols:
            df = df.assign(organization='ALL')
        return df
    org = org.str.replace(r'\s|うち|\(.+\)', '', regex=True).replace('民営|総数', 'ALL', regex=True)
    org_name = org.name
    df = df.assign(organization=org).drop(org_name, axis=1)
    return df


def clean_industry(df):
    df = df.copy()
    # clean string and change column name
    ind = (df.filter(like="産業").squeeze()
           .str.replace(r'[A-ZО][ー〜~\-]*[A-Z]*|\(.+\)|[\d\s~]', '', regex=True).str.replace('、', ',')
           .replace('全産業', 'ALL')
           .replace('非農林漁業', 'NALL')
           .replace('非農林水産業', 'NALL')
           .replace('農林漁業', 'AFF')
           .replace('農林水産業', 'AFF')
           .replace('林業,狩猟業', '林業')
           .replace('林業・狩猟業', '林業')
           .replace('漁業,水産養殖業', '漁業')
           .replace('卸売業,小売業', '卸売・小売業')
           .replace('卸売業・小売業', '卸売・小売業')
           .replace('卸売・小売業,飲食店', '卸売・小売業')
           .replace('卸売業・小売業,飲食店', '卸売・小売業')
           .replace('卸売・小売業・飲食店', '卸売・小売業')
           .replace('電気・ガス・熱供給・水道業', '電気・ガス・水道・熱供給業')
           .replace('電気,ガス,水道,熱供給業', '電気・ガス・水道・熱供給業')
           .replace('電気,ガス,水道業', '電気・ガス・水道・熱供給業')
           .replace('運輸,通信業', '運輸・通信業')
           .replace('運輸通信業', '運輸・通信業')
           .replace('金融,保険業', '金融・保険業')
           .replace('金融保険業', '金融・保険業')
           .replace('飲食店,宿泊行', '飲食店,宿泊業')
           )
    ind_name = ind.name
    df = df.assign(industry=ind).drop(ind_name, axis=1)
    return df


def clean_size(df):
    df = df.copy()
    cols = df.columns.values
    # clean string and change column name
    size = df.filter(like="規模").squeeze()
    if isinstance(size, pd.DataFrame):
        if 'size' not in cols:
            df = df.assign(size='ALL')
        return df
    size = (size.str.replace(r'\s|\(|\)', '', regex=True)
            .str.replace(r'人', '')
            .str.replace('-', '~')
            .str.replace('以上', '+')
            .replace('総数', 'ALL')
            .replace('派遣･下請従業者のみ', '派遣・下請従業者のみ')
            )
    mask = size.str.contains('うち|派遣', na=False)
    df = df.loc[~mask]
    size_name = size.name
    df = df.assign(size=size).drop(size_name, axis=1)
    return df


def clean_age(df, easy_mode=False):
    df = df.copy()
    # clean string and change column name
    establishment = (df.filter(like="時期").squeeze()
                     .str.replace(r'\s', '', regex=True).replace('総数', 'ALL').replace('不詳', 'unknown')
                     )
    est_name = establishment.name

    # format establishment period and turn it to age
    mask_age = ~establishment.str.contains("unknown|ALL")
    establishment_age = establishment[mask_age]
    if easy_mode:
        yrs = establishment_age.str.split('~', expand=True).apply(pd.to_numeric, errors='ignore')
    else:
        # in 1986 data 昭和 is missed before year
        mask_era = ~establishment_age.str.contains("^平成|昭和")
        establishment_age[mask_era] = establishment_age[mask_era].map(lambda x: '昭和'+x)
        # split establishment period to begin and end years
        era = establishment_age.str[:2].map({'昭和': 1925, '平成': 1988})
        era_fix = establishment_age.str.contains('昭和.*平成').map({True: 63, False: 0})
        yrs = (
            establishment_age.str.extract(r'(\d+|元)[年~\-平成]+(\d+|元)*')
            .replace('元', '1')
            .apply(pd.to_numeric, errors='ignore')
            .apply(lambda x: x.add(era))
        )
        yrs[1] = yrs[1] + era_fix
    # convert year to age
    year = df.year
    ages = yrs.apply(lambda x: x.sub(year).mul(-1)).fillna('')
    # use -, ~, + to form year and age
    hyphen = (
        (~yrs[0].isna() & ~yrs[1].isna()).map({True: '~', False: ''}).fillna('')
    )
    yrs = yrs.fillna('')
    before = establishment_age.str.contains(r'以前|^~').map(
        {True: '~', False: ''}
    )
    plus = before.replace('~', '+')
    establishment_age = ((before + yrs[0].astype(str) + hyphen + yrs[1].astype(str))
                         .str.replace('\.0', '', regex=True)
                         )
    establishment[mask_age] = establishment_age
    age = establishment.copy()
    age[mask_age] = ((ages[1].astype(str) + hyphen + ages[0].astype(str) + plus)
                     .str.replace('\.0', '', regex=True).str.replace('-0', '0')
                     )
    df = df.assign(establishment=establishment,
                   age=age).drop(est_name, axis=1)
    return df


def clean_variable(df, key_word="数"):
    df = df.copy()
    # clean string and change column name
    var = df.filter(like=key_word).squeeze()
    var = var.str.replace(r'\(.+\)|\s|総数', '', regex=True).map({'事業所数': 'num', '従業者数': 'employment'})
    df = df.assign(var=var).drop(var.name, axis=1)
    return df


def clean_control(df, remove=True):
    """
    Clean data with column 本所・支所別.
    Can choose to remove this column and leave only sum.
    """
    df = df.copy()
    cols = df.columns.values
    if remove:
        if '本所・支所別' in cols:
            df = (df.rename(columns={'本所・支所別': 'temp'})
                  .query('temp == "総数" ')
                  .drop(columns='temp'))
    else:
        # leave control category, clean string and change column name
        control = df.filter(like="本所").squeeze()
        if isinstance(control, pd.DataFrame):
            if 'control' not in cols:
                df = df.assign(control='ALL')
            return df
        control = (control.str.replace(r'\s', '', regex=True)
                   .replace('総数', 'ALL')
                   .replace('単独事業所', 'sole')
                   .replace('支所・支社・支店', 'branch')
                   .replace('本所・本社・本店', 'head')
                   )
        control_name = control.name
        df = df.assign(control=control).drop(control_name, axis=1)

    return df


def clean_estat(df, var=None):
    df = (df.filter(regex='^[^男女]')
          .pipe(assign_year)
          .pipe(clean_organization)
          .pipe(clean_industry)
          .pipe(clean_size)
          .pipe(clean_age)
          .rename(columns={"Value":"value"})
          .assign(value=lambda x: pd.to_numeric(x.value.replace('***', np.nan), errors='ignore'))
          )
    if var:
        df = df.assign(var=var)
    return df


def clean_estat_branch(df, var=None):
    df = (df.filter(regex='^[^男女]').filter(regex='^[^時間軸]').filter(regex='^[^@]')
          .pipe(assign_year)
          .pipe(clean_organization)
          .pipe(clean_industry)
          .pipe(clean_control, False)
          .rename(columns={"Value":"value"})
          .assign(value=lambda x: pd.to_numeric(x.value.replace('***', np.nan), errors='coerce'))
          )
    if var:
        df = df.assign(var=var)
    return df


def clean_estat_1996(df,):
    df = df.copy()
    c_ = df.filter(like="規模").squeeze()
    if isinstance(c_, pd.Series):
        c_name = c_.name
        tags = c_.str.replace('法人 会社', '会社').str.split(' ', expand=True)
        df = (df.assign(規模=tags[0],
                        組織=tags[1],
                        var=tags[2].map({'事業所数': 'num', '従業者数': 'employment'}))
              .drop(c_name, axis=1)
              )
    c_ = df.filter(like="本所").squeeze()
    if isinstance(c_, pd.Series):
        c_name = c_.name
        tags = (c_.apply(lambda x: '総数 ' + x if x[:2] not in ['単独', '本所', '支所'] else x)
                .str.replace(r'\s+', ' ', regex=True)
                .str.split(' ', expand=True))
        df = (df.assign(本所支所=tags[0],
                        組織=tags[1],
                        var=tags[2].map({'事業所数': 'num', '従業者数': 'employment'}),
                        temp=tags[3]
                        )
              .query('temp != "男" & temp != "女" ')
              .drop([c_name, 'temp'], axis=1)
              )
    return df

def clean_estat_1996_branch(df, col_key="経営事業男女従"):
    df = df.copy()
    c_ = df.filter(like=col_key).squeeze()
    if isinstance(c_, pd.Series):
        c_name = c_.name
        tags = c_.str.replace('法人 会社', '会社').str.split(' ', expand=True)
        df = (df.assign(
                        組織=tags[0],
                        var=tags[1].map({'事業所数': 'num', '従業者数': 'employment'}),
                        )
              .drop(c_name, axis=1)
              )
    return df

def clean_estat_1999_branch(df, col_key="事業所従業者数"):
    df = df.copy()
    mask_pct = df["@unit"] == "%"
    df = df.loc[~mask_pct, :]
    c_ = df.filter(like=col_key).squeeze()
    if isinstance(c_, pd.Series):
        c_name = c_.name
        tags = c_.str.replace('法人 会社', '会社').str.split(' ', expand=True)
        df = (df.assign(var=tags[0].map({'事業所数': 'num', '従業者数': 'employment'}),
                        組織=tags[1],
                        )
              .drop(c_name, axis=1)
              )
    return df


def clean_manual(df, year):
    df = (df.assign(year=year)
          .pipe(clean_organization)
          .pipe(clean_industry)
          .pipe(clean_size)
          .rename(columns={'事業所数': 'num', '事業者数': 'num', '従業者数': 'employment'})
          .replace('', np.nan).replace('\s', np.nan)
          )
    return df


def add_combined(df, combined_col, combined_tags, new_tag_name, drop_old_tags=False):
    df = df.copy()
    temp_col = ['value', combined_col, 'employment', 'num']
    if combined_col == "age":
        temp_col.append("establishment")
    group_col = [i for i in df.columns.values if i not in temp_col]
    combined_rows = (df.query(f'{combined_col} in @combined_tags')
                     .groupby(group_col)
                     .sum()
                     .reset_index()
                     .drop([combined_col], axis=1) # somehow required under new version, not sure why
                     .assign(temp=new_tag_name)
                     .rename(columns={'temp': combined_col})
                     )
    if drop_old_tags:
        mask = df[combined_col].isin(combined_tags)
        df = df.loc[~mask, :]
    df = pd.concat([df, combined_rows], ignore_index=True, sort=False)
    return df


def add_AFF_NALL(df):
    df = df.copy()
    ind_tags = df.industry.unique()
    if ('NALL' in ind_tags):  # ('AFF' in ind_tags) or
        print('Industry NALL have been added')
        return df
    AFF_tags = ['農業', '林業', '漁業']
    temp_tags = AFF_tags + ['ALL', 'AFF']
    NALL_tags = [i for i in df.industry.unique() if i not in temp_tags]
    df = (df.pipe(add_combined, 'industry', NALL_tags, 'NALL')
            .pipe(add_combined, 'industry', AFF_tags, 'AFF')
          )
    return df


def add_combined_industry(df):
    """
    Adjust the industry categories for 2004 and 2006.
    Caution: not excatly consistent with previous categories, probably might just drop.
    """
    df = df.copy()
    ind_tags = df.industry.unique()

    tags = []
    tags.append({'運輸・通信業': ['運輸業', '情報通信業']})
    tags.append({'卸売・小売業': ['卸売・小売業', '飲食店,宿泊業']})
    tags.append({'サービス業': ['医療,福祉', '教育,学習支援業', '複合サービス事業', 'サービス業', ]})

    for t in tags:
        new_tag, combined_tags = [(k, t[k]) for k in t][0]
        if all(i in ind_tags for i in combined_tags):
            df = df.pipe(add_combined, 'industry', combined_tags, new_tag, drop_old_tags=True)

    return df


def add_age_cohort(df):
    df = df.copy()
    age_tags = df.age.unique()

    # add types that need all
    types = []
    types.append({'ALL': ['0~3', '3~6', '6~12', '12+']})
    types.append({'0~5': ["0", "1", "2", "3", "4", "5"]})
    types.append({'0~5': ["0~2", "3~5"]})
    types.append({'0~6': ['0~3', '3~6']})
    types.append({'1~5': ["1", "2", "3", "4", "5"]})
    types.append({'2~6': ['2', '3', '4', '5', '6']})
    types.append({'2~4': ['2', '3', '4']})
    types.append({'4~6': ['4', '5', '6']})
    types.append({'3~20': ['3~5', '6~8', '9~11', '12~14', '15~17', '18~20']})
    types.append({'21~30': ['21~23', '24~30']})
    types.append({'9~26': ['9~16', '17~26']})
    types.append({'2~11': ['2', '3', '4', '5', '6', '7~11']})
    types.append({'2~16': ['2', '3', '4', '5', '6~8', '9~16']})
    types.append({'7~21': ['7~11', '12~21']})
    types.append({'17+': ['17~26', '27~36', '37+']})
    types.append({'17+': ['17~26', '27~36', '37~46', '47+']})
    types.append({'27+': ['27~36', '37+']})
    types.append({'27+': ['27~36', '37~46', '47+']})
    types.append({'32+': ['32~41', '42+']})
    types.append({'32+': ['32~41', '42~51', '52+']})
    types.append({'6~11': ['6~8', '9~11']})
    # types.append({'6~11': ['6', '7', '8', '9~11']})
    types.append({'6~11': ['6', '7~11']})
    types.append({'12~24': ['12~14', '15~17', '18~24']})
    types.append({'12~20': ['12~14', '15~17', '18~20']})
    types.append({'22+': ['22~31', '32+', ]})
    types.append({'22+': ['22~31', '32~41', '41+']})
    types.append({'22+': ['22~31', '32~41', '42~51', '52+']})
    types.append({'37+': ['37~46', '47+']})
    types.append({'18+': ['18~24', '25+']})
    types.append({'18+': ['18~20', '21~27', '28+']})
    types.append({'18+': ['18~20', '21~23', '24~30', '31+']})
    types.append({'9~14': ['9~11', '12~14']})
    types.append({'12~17': ['12~14', '15~17']})
    types.append({'15~20': ['15~17', '18~20']})
    types.append({'18~23': ['18~20', '21~23']})

    for t in types:
        new_tag, combined_tags = [(k, t[k]) for k in t][0]
        if all(i in age_tags for i in combined_tags):
            df = df.pipe(add_combined, 'age', combined_tags, new_tag)

    return df


def add_size_cohort(df):
    df = df.copy()
    size_tags = df['size'].unique()

    # add types that need all
    types = []
    # for 1969
    types.append({'1~9': ['1~4', '5~9']})
    types.append({'10~29': ['10~19', '20~29']})
    types.append({'100~299': ["100~199", "200~299"]})
    # for 1957
    types.append({'1~9': ['1', '2~4', '5~9']})
    types.append({'30~99': ["30~49", "50~99"]})
    types.append({'100+': ["100~299", "300+"]})
    types.append({'100+': ["100~199", "200~299", "300+"]})

    for t in types:
        new_tag, combined_tags = [(k, t[k]) for k in t][0]
        if all(i in size_tags for i in combined_tags):
            df = df.pipe(add_combined, 'size', combined_tags, new_tag)

    return df


def clean_eStat_data():

    files = sorted(glob.glob(input_path_est + '[0-9]*_全国*.pkl'))
    files = [i for i in files if '廃' not in i]
    files = [i for i in files if ('2004' in i) or ('本所' not in i)]  # add 2004 control data for organization category
    _len = len(input_path_est)
    files_year = [i[_len:_len+4] for i in files]
    files_tail = [i[-8:-4] for i in files]
    # print(files)

    dfs = pd.DataFrame()

    # 1981, 1986, 1991: two files each year
    var_keys = {"事業所数": 'num', "従業者数": 'employment'}
    for yr in ['1981', '1986', '1991']:
        for i, (y, v) in enumerate(zip(files_year, files_tail)):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_estat, var_keys[v])
                if y in ['1981', '1986']:
                    df = df.pipe(add_AFF_NALL)
                df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True)
                print(f'Cleaned {y}!')

    # 1996
    for i, y, in enumerate(files_year):
        if y == "1996":
            df = pd.read_pickle(files[i]).pipe(clean_estat_1996).pipe(clean_estat)
            df = df.pipe(add_size_cohort).pipe(add_age_cohort)
            dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
            print(f'Cleaned {y}!')

    # 2001, 2004, 2006
    for yr in ['2001', '2004', '2006']:
        for i, y, in enumerate(files_year):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_estat).pipe(clean_variable).pipe(clean_control)
                if y in ['2004', '2006']:
                    df = df.pipe(add_combined_industry)
                df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
                print(f'Cleaned {y}!')

    dfs = dfs.drop_duplicates()
    return dfs


def clean_manual_data():
    files = sorted(glob.glob(input_path_m + '[0-9]*_全国*民営*.csv'))  # exclude 3-digit level
    _len = len(input_path_m)
    files_year = [i[_len:_len+4] for i in files]

    dfs = pd.DataFrame()

    # 1957, 1969, 1972, 1975, 1978, 1989
    for f, y in zip(files, files_year):
        df = pd.read_csv(f).pipe(clean_manual, int(y))
        if y == '1957':
            df = (df.assign(開設時期=lambda df: df.開設時期.str.replace(r'\d+月', '', regex=True),
                            industry=lambda df: df.industry.replace('ALL', 'NALL'))
                  .pipe(clean_age)
                  )
        else:
            df = df.pipe(clean_age, easy_mode=True)
        df = df.pipe(add_size_cohort).pipe(add_age_cohort)
        dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
        print(f'Cleaned {y}!')
    dfs = dfs.drop_duplicates()
    return dfs


def clean_eStat_data_branch():
    files = sorted(glob.glob(input_path_ent + '[0-9]*_本所*.pkl'))
    _len = len(input_path_ent)
    files_year = [i[_len:_len+4] for i in files]
    files_tail = [i[-8:-4] for i in files]

    dfs = pd.DataFrame()

    # 1981, 1986, 1991: two files each year
    var_keys = {"事業所数": 'num', "従業者数": 'employment'}
    for yr in ['1981', '1986', '1991']:
        for i, (y, v) in enumerate(zip(files_year, files_tail)):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_estat_branch, var_keys[v])
                if y in ['1981', '1986']:
                    df = df.pipe(add_AFF_NALL)
                # df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True)
                print(f'Cleaned {y}!')
                # print(df.columns)

    # 1996, 1999
    func_map = {"1996": clean_estat_1996_branch, "1999": clean_estat_1999_branch}
    for yr in ['1996', '1999']:
        for i, y, in enumerate(files_year):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(func_map[y])
                df = df.pipe(clean_estat_branch)
                # df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
                print(f'Cleaned {y}!')
                # print(df.columns)

    # 2001, 2004, 2006
    for yr in ['2001', '2004', '2006']:
        for i, y, in enumerate(files_year):
            if y == yr:
                df = pd.read_pickle(files[i]).pipe(clean_variable).pipe(clean_estat_branch)
                if y == '2004': # only this year in this set of datasets have size info
                    c_ = df.filter(like="従業者規模").squeeze()
                    df = df.loc[c_=="総数", :]
                    df = df.drop(columns=c_.name)
                if y in ['2004', '2006']:
                    df = df.pipe(add_combined_industry)
                # df = df.pipe(add_size_cohort).pipe(add_age_cohort)
                dfs = pd.concat([dfs, df], ignore_index=True, sort=False)
                print(f'Cleaned {y}!')
                # print(df.columns)

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
    df.to_pickle(output_path + 'EEC_Establishment_age.pkl')

    df_estat_branch = clean_eStat_data_branch()
    # print(df_estat_branch.columns)
    df_estat_branch = (df_estat_branch.set_index(['year', 'period', 'organization', 'industry',
                                    'control', 'var']).filter(["value"])
                .unstack().droplevel(0, axis=1).reset_index().rename_axis(None, axis=1)
                )
    df_estat_branch.to_pickle(output_path + 'EEC_Establishment_branch.pkl')


if __name__ == "__main__":
    main()
