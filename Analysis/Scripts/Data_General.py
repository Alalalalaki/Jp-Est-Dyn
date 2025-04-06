"""
General tools to adjust data (mainly EEC data)
"""

import numpy as np
import pandas as pd

input_path = "../../Data/Output/"


def clean_df(df):
    org_maps = {'会社': 'employer', '個人': 'nonemployer'}
    df = df.assign(organization=lambda x: x.organization.replace(org_maps))
    return df


def interpolated_dfh(org="ALL", ind="NALL", size="ALL"):
    """interpolate EEC historical data to be used in calculation"""
    dfh = pd.read_pickle(input_path+'Offical_Historical_EEC.pkl')
    org_maps = {'employer': 'company', 'nonemployer': 'individual_proprietorship',
                '会社': 'company', '個人': 'individual_proprietorship', '法人': 'corporations',
                'ALL': 'ALL', 'corporations': 'corporations', }
    org = org_maps[org]
    dfh62 = dfh.query('table_id == "06-02" ')
    df = (dfh62.query('organization == @org & industry == @ind & size == @size')
               .dropna(axis=1, how='all')  # drop employee_status in come case
               .drop(['table_id'], axis=1)
          )
    years = list(range(min(df.year), max(df.year)+1))
    df_interpolated = (
        df.set_index('year')
        .reindex(years)
        .assign(num=lambda x: x.num.interpolate(),
                employment=lambda x: x.employment.interpolate()
                )
        .ffill() # fillna(method='ffill')
    )
    return df_interpolated


def age_zero_adjust(first=12):
    agezeromonth = {1957: first, 1969: 6, 1972: 8, 1975: 5.5, 1978: 6.5, 1981: 6, 1986: 6,
                    1989: 6, 1991: 6, 1994: 4.7, 1996: 9, 1999: 6, 2001: 9, 2004: 5, 2006: 9}
    return agezeromonth


def age_cohorts(original=True):
    cohorts = {1957: ['0~3', '3~6', '6~12', '12+'],
               1969: ['0', '1', '2', '3', '4', '5', '6~8', '9~11', '12~14', '15~17', '18~24', '25+'],
               1972: ['0', '1', '2', '3', '4', '5', '6~8', '9~11', '12~14', '15~17', '18~20', '21~27', '28+'],
               1975: ['0', '1', '2', '3', '4', '5', '6~8', '9~11', '12~14', '15~17', '18~20', '21~23', '24~30', '31+'],
               1978: ['0~2', '3~5', '6~23', '24~33', '34+'],
               1981: ['0', '1', '2', '3', '4', '5', '6~8', '9~16', '17~26', '27~36', '37+'],
               1986: ['0', '1', '2', '3', '4', '5', '6', '7~11', '12~21', '22~31', '32+'],  # no org or size or employment
               1989: ['0', '1', '2', '3', '4', '5~9', '10~14', '15~24', '25~34', '35+'],
               1991: ['0', '1', '2', '3', '4', '5', '6', '7~16', '17~26', '27~36', '37+'],
               1996: ['0', '1', '2', '3', '4', '5', '6', '7~11', '12~21', '22~31', '32~41', '42+'],
               2001: ['0', '1', '2', '3', '4', '5', '6', '7~16', '17~26', '27~36', '37~46', '47+'],
               2004: ['0', '1', '2', '3', '4', '5~9', '10~19', '20~29', '30~39', '40~49', '50+'],
               2006: ['0', '1', '2', '3', '4', '5', '6', '7~11', '12~21', '22~31', '32~41', '42~51', '52+'],
               }
    return cohorts


def get_age_mean(df):
    # get the mean of age interval
    # of course the mathematic mean here can be biased, esp. when interval is wide
    mask = df.age.str.contains('\+')
    df = df.loc[~mask]
    df = df.assign(
        age_mean=lambda x: (
            x.loc[~mask]
            .age.str.split('~', expand=True)
            .map(pd.to_numeric)
            .mean(axis=1)
        )
    )
    return df


def size_cohorts(cat='simple'):
    if cat == 'full':
        sizes = ['1~4', '5~9',  '10~19', '20~29', '30~49', '50~99', '100~199', '200~299', '300+']
    elif cat == 'normal':
        sizes = ['1~4', '5~9', '10~29', '30~49', '50~99', '100~299', '300+']
    elif cat == 'simple':
        sizes = ['1~9', '10~29', '30~99', '100+']
    else:
        raise ValueError
    return sizes


def get_industry():
    # default industries with default order for multiple plots
    # for industries left, '鉱業' and '電気・ガス・水道・熱供給業' are not very good example, '不動産業' can substitute for "金融・保険業"
    inds = ["製造業", "運輸・通信業", "卸売・小売業",
            "建設業", "金融・保険業", "サービス業", ]
    return inds


def get_industry_name(ind):
    maps = {"製造業": "Manufacturing",
            "サービス業": "Service",
            "建設業": "Construction",
            "金融・保険業": "Finance",
            "運輸・通信業": "Transport & Communication",
            "卸売・小売業": "Wholesale & Retail", }
    name = maps[ind]
    return name


def sme_entry_exit_data():
    # NALL data from "ChushoHakusyo_2011_fig3-1-2_EntryExitRate_census_appendix_ind"
    dt = pd.DataFrame({
    'year': [1969, 1972, 1975, 1978, 1981, 1986, 1989, 1991, 1994, 1996, 1999, 2001, 2004, 2006],
    'period': ['66～69', '69～72', '72～75', '75～78', '78～81', '81～86', '86～89', '89～91', '91～94', '94～96', '96～99', '99～01', '01～04', '04～06'],
    'entry_rate': [6.5, 7.0, 6.1, 6.2, 6.1, 4.7, 4.2, 4.1, 4.6, 3.7, 4.1, 6.7, 4.2, 6.4],
    'exit_rate': [3.2, 3.8, 4.1, 3.4, 3.8, 4.0, 3.6, 4.7, 4.7, 3.8, 5.9, 7.2, 6.4, 6.5]
})
    return dt
