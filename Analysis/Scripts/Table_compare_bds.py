# Note: the code can be further simplified

import numpy as np
import pandas as pd

from Data_General import clean_df
from Figure_General import input_path
from Figure_exit_rate import exit_rate_from_two_year
from Figure_avgsize_trend import get_avgsize_by_age


def download_bds_data(year=2022, suffix="_sec"):
    base_url = f"https://www2.census.gov/programs-surveys/bds/tables/time-series/{year}/"
    dfe = pd.read_csv(base_url+f"bds{year}{suffix}.csv")

    return dfe

def clean(df, col_start=2):
    df.iloc[:,col_start:] = df.iloc[:,col_start:].replace("X", np.NaN).apply(lambda x: pd.to_numeric(x, errors='coerce'))
    return df

def np_sum(g):
    return np.sum(g.values)

def aggregate_category(df, selection, groupby=["year"]):

    selected_data = df[selection].copy()
    aggregated_data = selected_data.groupby(groupby).agg({
        'estabs': np_sum,
        'estabs_entry': np_sum,
        'estabs_exit': np_sum,
        'emp': np_sum,
        }).reset_index()
    # aggregated_data['estabs_t_minus_1'] = aggregated_data['estabs'] + aggregated_data['estabs_exit'] - aggregated_data['estabs_entry'] # This ways goes problematic when where is missing in estabs_exit or estabs_entry
    aggregated_data['estabs_t_minus_1'] = aggregated_data['estabs'].shift(1)
    aggregated_data['estabs_denominator'] = 0.5 * (aggregated_data['estabs'] + aggregated_data['estabs_t_minus_1'])
    aggregated_data['entry_rate'] = 100 * (aggregated_data['estabs_entry'] / aggregated_data['estabs_denominator'])
    aggregated_data['exit_rate'] = 100 * (aggregated_data['estabs_exit'] / aggregated_data['estabs_denominator'])
    aggregated_data['avg_estab_size'] = aggregated_data['emp'] / aggregated_data['estabs']

    return aggregated_data


def calculate_bds():

    # for non-primary sector
    dfe_s = download_bds_data()
    dfe_s_np = aggregate_category(dfe_s, dfe_s['sector'] != 11) # Exclude the primary sector (sector == 11)
    dfe_s_np["eage"] = "ALL"
    print(dfe_s_np)

    # for non-primary sector and each age group
    dfe_sa = download_bds_data(suffix="_sec_ea").pipe(clean, col_start=3)
    dfe_sa_np = aggregate_category(dfe_sa, dfe_sa['sector'] != 11, groupby=["year", "eage"])
    print(dfe_sa_np)
    dfe_sa_np_25 = aggregate_category(dfe_sa, (dfe_sa['sector'] != 11) & (dfe_sa['eage'].isin(["c) 2", "d) 3", "e) 4", "f) 5"])), groupby=["year"])
    dfe_sa_np_25["eage"] = "c+d+e+f) 2-5"
    dfe_sa_np_615 = aggregate_category(dfe_sa, (dfe_sa['sector'] != 11) & (dfe_sa['eage'].isin(["g) 6 to 10", "h) 11 to 15",])), groupby=["year"])
    dfe_sa_np_615["eage"] = "g+h) 6-15"
    dfe_sa_np_21plus = aggregate_category(dfe_sa, (dfe_sa['sector'] != 11) & (dfe_sa['eage'].isin(["j) 21 to 25", "k) 26+", "l) Left Censored"])), groupby=["year"])
    dfe_sa_np_21plus["eage"] = "j+k+l) 21+Censored"
    dfe_sa_np_26plus = aggregate_category(dfe_sa, (dfe_sa['sector'] != 11) & (dfe_sa['eage'].isin(["k) 26+", "l) Left Censored"])), groupby=["year"])
    dfe_sa_np_26plus["eage"] = "k+l) 26+Censored"
    print(dfe_sa_np_26plus)

    dfe = pd.concat([dfe_s_np, dfe_sa_np, dfe_sa_np_25, dfe_sa_np_615, dfe_sa_np_21plus, dfe_sa_np_26plus], ignore_index=True, axis=0)

    return dfe

def calculate_ec():

    dfa = pd.read_pickle(input_path+'EEC_Establishment_age.pkl').pipe(clean_df)

    age2001b = ['1', '2~6', '7~16', '17~26', '27+', ]
    age2006a = ['6', '7~11', '12~21', '22~31', '32+',]
    df_exit = exit_rate_from_two_year(2001, 2006, age2001b, age2006a, df=dfa,)
    print(df_exit)

    ages = ['1', '2~6', '7~11', '12~21', '22+', ]
    df_size = get_avgsize_by_age(ages=ages,)
    print(df_size)

    # return df


def main():
    dfe = calculate_bds()
    print(dfe[["year","eage","entry_rate","exit_rate","avg_estab_size"]].query("year == 2006"))

    calculate_ec()

if __name__ == "__main__":
    main()

