"""
This scrpit is to download EC data 2009-20016 from eStat.
"""

import os
import pandas as pd

from snippets import estat
from EEC_download import read_estat_menu, save_file, extract_industry, extract_number, extract_organization


input_path = "../Input/Economic_Census/"

if not os.path.exists(input_path):
    os.mkdir(input_path)


def download_age_data_for_establishment():

    # 基礎調査
    id_2009 = ["0003032602"]  # 産業(小分類),開設時期(14区分),本所・支所(3区分),経営組織(4区分)
    id_2009 = id_2009 + ["0003032603", "0003032604"]  # 産業(小分類),開設時期(14区分),本所・支所(3区分),従業者規模(10区分)
    id_2014 = ["0003117657"]
    id_2014 = id_2014 + ["0003117601", "0003117640"]  # 産業(小分類),開設時期(14区分),本所・支所(3区分),従業者規模(10区分)

    # 活動調査
    id_2012 = ["0003090089"]  # 産業(小分類),開設時期(12区分),単独・本所・支所(3区分),経営組織(4区分)別民営事業所数及び男女別従業者数
    id_2012 = id_2012 + ["0003090060"]  # 産業(小分類),開設時期(12区分),単独・本所・支所(3区分),従業者規模(10区分)別民営事業所数及び男女別従業者数
    id_2016 = ["0003218702"]  # 産業(小分類),開設時期(16区分),単独・本所・支所(3区分),経営組織(4区分)別民営事業所数及び男女別従業者数
    id_2016 = id_2016 + ["0003218703"]  # 産業(小分類),開設時期(16区分),単独・本所・支所(3区分),従業者規模(10区分)別民営事業所数及び男女別従業者数

    for i in (id_2009+id_2014+id_2012+id_2016):
        df = estat.DataRead(i)
        df = (df.pipe(extract_number, colname='項目')  # 表章項目,
              .pipe(extract_industry)
              .pipe(extract_organization)
              )
        df = df.drop_duplicates()
        if (df.duplicated(df.columns.values[:-1]).sum()) > 0:
            print(f"Caution: duplicated entry with different value : {i}")
        save_file(id_=i, tag='全国', df=df, input_path=input_path,
                  menu=EC_estat_menu, drop_col_name='全国')


def download_age_data_for_enterprise():

    # 基礎調査
    id_2009 = ['0003032606']  # 産業(中分類),開設時期(14区分),資本金階級(10区分),単独・本所(2区分)別民営事業所数及び男女別従業者数(外国の会社を除く会社の単独及び本所事業所)
    id_2014 = ['0003111151']  # 産業(中分類)、開設時期(13区分)、資本金階級(10区分)、単独・本所(2区分)別民営事業所数及び男女別従業者数(外国の会社を除く会社の単独及び本所事業所)
    id_2014 = id_2014 + ['0003111194']  # 産業(小分類)、開設時期(13区分)別民営事業所数、従業者数及び売上(収入)金額(外国の会社及び法人でない団体を除く) ?

    # 活動調査
    id_2012 = ["0003090100"]  # 産業(中分類),開設時期(12区分),資本金階級(10区分),単独・本所(2区分)別民営事業所数及び男女別従業者数(外国の会社を除く会社の単独及び本所事業所)
    id_2012 = id_2012 + ["0003090067"]  # 産業(小分類),開設時期(11区分)別民営事業所数,従業者数及び売上(収入)金額(外国の会社及び法人でない団体を除く)
    id_2012 = id_2012 + ["0003090121"]  # 産業(小分類),開設時期(11区分)別民営事業所数,事業従事者数及び付加価値額(外国の会社及び法人でない団体を除く)


def main():
    download_age_data_for_establishment()
    download_age_data_for_enterprise()


if __name__ == "__main__":
    EC_estat_menu = read_estat_menu(name="EC_estat_menu.pkl", path=input_path, ids=['00200552', '00200553'])
    main()
