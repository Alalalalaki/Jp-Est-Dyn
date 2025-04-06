"""
This scrpit is to download EEC data 1981-2006 from eStat.
"""

import os
import pandas as pd

from jpstat import estat


input_path = "../Input/Establishment_and_Enterprise_Census/eStat/"
input_path_est = "../Input/Establishment_and_Enterprise_Census/eStat/establishment/"
input_path_ent = "../Input/Establishment_and_Enterprise_Census/eStat/enterprise/"

for i in [input_path, input_path_est, input_path_ent]:
    if not os.path.exists(i):
        os.mkdir(i)


def read_estat_menu(name, path, ids, forcedownload=False):
    if not os.path.exists(path+name) or forcedownload:
        menu = pd.DataFrame()
        for i in ids:
            df, _ = estat.get_data(i)
            cols = ['period', 'TABLE_NAME', '提供統計名及び提供分類名', '総件数', 'ID']
            df = df[cols]
            menu = pd.concat([menu, df], ignore_index=True)
        menu.to_pickle(path+name)
    else:
        menu = pd.read_pickle(path+name)
    return menu


def extract_industry(df, colname='産業', mode="2-digit", list_=None):
    df = df.copy()
    c = df.filter(like=colname).squeeze()

    if mode == "2-digit":
        if len(c.unique()) < 22:
            return df
        else:
            df = df[c.str.contains(r'^[A-ZО]', regex=True)]
    elif mode == "3-digit":
        if len(c.unique()) < 97:
            return df
        else:
            df = df[c.str.contains(r'^\d{2}\s', regex=True)]
    elif mode == "custom":
        if len(list_) > 0:
            df = df[c.isin(list_)]
        else:
            raise ValueError('Mode "custom" require a given list of industries.')
    else:
        print(f'Mode {mode} is not valid.')
    return df


def extract_organization(df, colname='組織'):
    df = df.copy()
    c = df.filter(like=colname).squeeze()
    if len(c.shape) == 1:
        df = df[c.str.contains(r'^\s*会社$|^\s*個人$|^\s*法人$|民営|うち|総数', regex=True)]
    return df


def extract_number(df, colname='事業|男女'):
    df = df.copy()
    c = df.filter(regex=colname).squeeze()
    if len(c.shape) == 1:
        df = df[~c.str.contains(r'男|女|合名|合資|外国|有限|株式|相互|以外|でない', regex=True)]
    return df


def extract_setup(df, colname='成立'):
    df = df.copy()
    c = df.filter(like=colname).squeeze()
    if len(c.shape) == 1:
        df = df[~c.str.contains(r'うち|月', regex=True)]
    return df


def get_file_name(_id, tag, menu):
    menu = menu.query('ID == @_id')
    period = menu.period.values[0]
    year = str(period)[:4]
    info = menu.TABLE_NAME.str.extract(r'(^.+数)')[0].values[0]
    file_name = f'{year}_{tag}_{info}'
    return file_name, period


def save_file(id_, tag, df, input_path, menu, drop_col_name=None):
    df = df.copy()
    df = df.reset_index(drop=True)
    # drop certain column
    if drop_col_name:
        df = df.loc[:, ~df.columns.str.contains(drop_col_name)]
    # get name and save
    file_name, period = get_file_name(id_, tag, menu)
    df.assign(period=period).to_pickle(input_path + file_name + '.pkl')
    print(f'Save file {file_name} with shape: {df.shape}')


def download_age_data_for_establishment():
    """
    Note:
    産業大分類ある場合は大分類データをdownload & save。
    ない場合は中分類か小分類をdownloadしたら大分類だけ残してsave。
    従業者数
    """
    # 81-91 data: 事業所数, 従業員数別ファイル
    id_1981 = ["0000040034", "0000040037"]  # 経営組織（４Ａ），産業大分類（１３），開設時期（１３），従業者規模（１４）
    id_1986 = ["0000040202", "0000040205"]  # 経営組織（１０），産業大分類（１３），開設時期（１３），従業者規模（１６Ａ）
    id_1991 = ["0000040675", "0000040678"]  # 産業大分類（１８），開設時期（１３），経営組織（１０Ｂ），従業者規模（１６Ａ）
    # 96-06 data: 事業所数, 従業員数別(男女別)同ファイル　(1996 2 part分け)
    id_1996 = ["0000040955", "0000040956"]  # 産業大分類（１８），開設時期（１４），従業者規模・経営組織（１７６）
    id_1996_control = ["0000040928"]  # 産業大分類(18), 開設時期(14), 本所・支所・経営組織(16)
    id_2001 = ["0000041429"]  # 産業小分類、開設時期（１３区分）、 従業者規模（１５区分－１）、経営組織（８区分）
    id_2001_control = ["0000041415"]  # 産業小分類、開設時期(13区分)、本所・支所の別(3区分)、経営組織(4区分-1)
    id_2006 = ["0003001012"]  # 産業小分類、開設時期（14区分）、従業者規模（15区分）、経営組織（9区分）// "0003001510" には従業者規模: 派遣・下請従業者のみ データ
    id_2006_control = ["0003000910", "0003000910"]  # 産業(小分類)、開設時期(14区分)、本所・支所(3区分)、従業者規模(10区分)・経営組織(5区分)

    # download 81-06 data
    df_1996 = pd.DataFrame()
    df_2006_control = pd.DataFrame()
    for i in (id_1981+id_1986+id_1991+id_1996+id_1996_control+id_2001+id_2001_control+id_2006+id_2006_control):
        df, _ = estat.get_data(i)
        df = df.drop_duplicates()  # in some data, there are duplicates after downloading for unknown reasons
        if (df.duplicated(df.columns.values[:-1]).sum()) > 0:
            print(f"Caution: duplicated entry with different value : {i}")
        df = df.pipe(extract_number).pipe(extract_organization).pipe(extract_industry)
        df.columns = df.columns.str.replace(r'\d', '', regex=True)
        if i in id_1996:
            df_1996 = pd.concat([df_1996, df], ignore_index=True)
            df = df_1996
        if i in id_2006_control:
            df_2006_control = pd.concat([df_2006_control, df], ignore_index=True)
            df = df_2006_control
        save_file(id_=i, tag='全国', df=df, input_path=input_path_est,
                  menu=EEC_estat_menu, drop_col_name='全国')  # drop 全国 column

    # 2004 data is somehow different from above and thus dolwnloaded seperately
    id_2004 = ["0000041721", "0000041722"]  # 産業中分類、開設時期（１２区分）、従業者規模（１０区分）; 産業小分類、開設時期(12区分)、本所・支所の別(3区分)、経営組織(8区分)
    id_2004_ee = ["0000041712"]  # 存続・新設・廃業、開設時期（２７区分）but no 従業者規模区分
    df, _ = estat.get_data(id_2004_ee[0])
    ind_1d = df.filter(regex='産業').squeeze().unique()
    df.columns = df.columns.str.replace(r'\d', '', regex=True)
    save_file(id_=id_2004_ee[0], tag='全国', df=df, input_path=input_path_est, menu=EEC_estat_menu, drop_col_name='全国')
    for i in id_2004:
        df, _ = estat.get_data(i)
        # in 2004 data there are duplicated entry with different value in 漁業 probably due to some industry classification issue. Here I leave the first large entry.
        df = df.drop_duplicates(df.columns.values[:-1])
        df = df.pipe(extract_number).pipe(extract_industry, mode='custom', list_=ind_1d).pipe(extract_organization)
        df.columns = df.columns.str.replace(r'\d', '', regex=True)
        save_file(id_=i, tag='全国', df=df, input_path=input_path_est, menu=EEC_estat_menu, drop_col_name='全国')


def download_age_data_for_establishment_ind3():
    # 81-96: similar data as above
    id_1981 = ["0000040035", "0000040038"]
    id_1986 = ["0000040203", "0000040206"]
    id_1991 = ["0000040676", "0000040679"]
    id_1996 = ["0000040957", "0000040958"]
    # 01-06: exactly the same data but now extract ind3
    id_2001 = ["0000041429"]
    id_2006 = ["0003001012"]

    # download code is similar to above
    df_1996 = pd.DataFrame()
    for i in (id_1981+id_1986+id_1991+id_1996+id_2001+id_2006):
        df, _ = estat.get_data(i)
        df = df.drop_duplicates()  # in some data, there are duplicates after downloading for unknown reasons
        if (df.duplicated(df.columns.values[:-1]).sum()) > 0:
            print(f"Caution: duplicated entry with different value : {i}")
        df = df.pipe(extract_number).pipe(extract_organization).pipe(extract_industry, mode="3-digit")
        df.columns = df.columns.str.replace(r'\d', '', regex=True)
        if i in id_1996:
            df_1996 = pd.concat([df_1996, df], ignore_index=True)
            df = df_1996
        save_file(id_=i, tag='産業', df=df, input_path=input_path_est,
                  menu=EEC_estat_menu, drop_col_name='全国')  # drop 全国 column

def download_age_data_for_firm():
    """
    Note:
    1981年に企業編データなし。
    企業社数データのみ、従業員数データなし。
    """

    # 1986
    id_1986 = ['0000040385']  # 企業類型(3),企業産業大分類(13),資本金階級(11),開設時期(9)
    id_1991 = ['0000040823']  # 企業産業大分類(18),開設時期(9),企業類型(3),資本金階級(11)
    id_1996 = ['0000041041']  # 企業産業大分類(18),開設時期(9),資本金階級(13)
    id_1996 = id_1996 + ['0000041046']  # 企業産業大分類(18),開設時期(14),親会社・子会社・関連会社の有無(15)
    id_2001 = ['0000041501']  # 企業産業中分類(2-1)、開設時期(13区分)、資本金階級(10区分)、資本金階級(10)
    id_2001 = id_2001 + ['0000041503']  # 企業産業中分類(2-1)、会社成立時期(7区分)、親会社・子会社等の有無(15区分)、資本金階級(10)
    id_2001 = id_2001 + ['0000041538']  # 会社成立時期(512区分)、企業産業中分類(2-3)、企業数(経営組織が会社の本所事業所)
    id_2006 = ['0003004282']  # 企業産業(中分類)、開設時期(14区分)、資本金階級(10区分)
    id_2006 = id_2006 + ['0003004286']  # 企業産業(中分類)、会社成立時期(9区分)、親会社・子会社等の有無別企業数
    id_2006 = id_2006 + ['0003004374']  # 会社成立時期(532区分)、企業産業(中分類)

    for i in (id_1986+id_1991+id_1996+id_2001+id_2006):
        df, _ = estat.get_data(i)
        df = df.pipe(extract_number).pipe(extract_industry).pipe(extract_setup)
        df = df.drop_duplicates()
        if (df.duplicated(df.columns.values[:-1]).sum()) > 0:
            print(f"Caution: duplicated entry with different value : {i}")
        df.columns = df.columns.str.replace(r'\d', '', regex=True)
        save_file(id_=i, tag='会社', df=df, input_path=input_path_ent,
                  menu=EEC_estat_menu, drop_col_name='全国')  # drop 全国 column

def download_branch_data_for_establishment():
    # 81-96: similar data as above
    id_1981 = ["0000040026", "0000040027"] # 産業大分類(13),本所・支所(4),経営組織(9A)
    id_1986 = ["0000040167", "0000040168"] # 産業大分類(13),本所・支所(4),経営組織(10) // 男女の別(3)
    id_1991 = ["0000040626", "0000040627"] # 産業大分類(15A),本所・支所(4),経営組織(10B) // 男女の別(3)
    id_1996 = ["0000040921"] # 産業大分類(15),本所・支所(4),経営組織(11)・事業所数,男女(3)・従業者数(民営)
    id_1999 = ["0000041242"] # 産業大分類(15)、本所・支所(4)、経営組織(11)、事業所数・従業者数(民営)
    id_2001 = ["0000041410"] # 産業大分類(20)、従業者規模(10区分)、本所・支所の別(3区分)、経営組織(8区分)、事業所数・男女別従業者数
    id_2004 = ["0000041718"] # 産業大分類(1-2)、本所・支所の別(3区分)、経営組織(8区分)、事業所数、従業者数(総数、男、女)
    id_2006 = ["0003000888"] # 産業(大分類)、本所・支所(3区分)、経営組織(9区分)別民営事業所数及び男女別従業者数

    # download code is similar to above
    for i in (id_1981+id_1986+id_1991+id_1996+id_1999+id_2001+id_2004+id_2006):
        df, _ = estat.get_data(i)
        df = df.drop_duplicates()
        df = df.pipe(extract_number).pipe(extract_organization).pipe(extract_industry)
        df.columns = df.columns.str.replace(r'\d', '', regex=True)
        save_file(id_=i, tag='本所', df=df, input_path=input_path_ent,
                  menu=EEC_estat_menu, drop_col_name='全国')  # drop 全国 column

def main():
    download_age_data_for_establishment()
    download_age_data_for_firm()
    download_age_data_for_establishment_ind3()

    download_branch_data_for_establishment()


if __name__ == "__main__":
    EEC_estat_menu = read_estat_menu(name="EEC_estat_menu.pkl", path=input_path, ids=['00200551'])
    main()
