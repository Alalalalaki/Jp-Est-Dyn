"""
This scrpit is to clean Official Tax & Law data in excel files
"""

import numpy as np
import pandas as pd
import z2h


input_path_T = "../Input/data_in_offical_documents/TaxLawData/"
input_path_H = "../Input/data_in_offical_documents/HistoricalData/"
output_path = "../Output/"


def clean_TaxLaw():

    # corporation = pd.read_csv(input_path_T+'会社標本調査30回記念号_法人数.csv')

    # use the number of company in historical data
    # Note that the original data is from TaxLawData, set log on Tax&Law
    hist_corp_files = ['06-10-a_産業別法人数.xls', '06-10-b_産業別法人数.xls']
    col1 = ['todrop', 'year', 'ALL', 'Agriculture', 'Fisheries', 'Mining', 'Manufacturing',
            'Commerce', 'Finance', 'Transport', 'Other']
    col2 = ['todrop', 'year', 'ALL', 'Manufacturing', 'Wholesale', 'Retail', 'Construction',
            'TransportCommunicationUtilities', 'Services', 'EatingDrinkingHotels',
            'AFF', 'Mining', 'Finance', 'RealEstate', 'Other']
    corporation = pd.DataFrame()
    for i, col in zip(hist_corp_files, [col1, col2]):
        corp = (pd.read_excel(input_path_H+i, skiprows=4, names=col, na_values=['...', '*'])
                .assign(year=lambda x: x.year.astype(str).str[:4])
                .drop('todrop', axis=1)
                )
        mask_year = corp.year.str.contains('^\d{4}', na=False)
        corp = corp.loc[mask_year].apply(pd.to_numeric, errors='coerce').set_index('year')
        corporation = pd.concat([corporation, corp], sort=False)

    # use the number of company in Tax Data (as historical data is up to 2003)
    corps = pd.ExcelFile(input_path_T+'国税庁_長期時系列データ_法人税.xlsx')
    col = ['year', 'Manufacturing', 'Wholesale', 'Retail', 'Construction',
           'TransportCommunicationUtilities', 'ICT', 'Health', 'Services', 'EatingDrinkingHotels',
           'AFF', 'Mining', 'Finance', 'RealEstate', 'Other', 'ALL', 'todrop']
    corp = corps.parse(sheet_name=3, skiprows=4, names=col, skipfooter=4, na_values=['-'])
    corp = (corp.dropna(how='all').drop('todrop', axis=1)
            .reset_index(drop=True)
            .assign(year=lambda x: x.index+1948)
            .set_index('year')
            .apply(pd.to_numeric, errors='coerce'))
    corporation = pd.concat([corporation, corp.loc[2004:]], sort=False)

    # use setup data in Law Registration data
    setup = pd.read_csv(input_path_T+'登記統計年報_会社登記.csv')
    setup = setup.query('head_branch == "Head"').groupby('year')['設立', '合併又は組織変更による設立'].apply(sum)
    setup = setup.sum(axis=1).to_frame('setup')

    df = pd.concat([corporation, setup], axis=1)
    return df


def main():
    clean_TaxLaw().to_pickle(output_path+'Offical_TaxLaw_Corporation.pkl')


if __name__ == "__main__":
    main()
