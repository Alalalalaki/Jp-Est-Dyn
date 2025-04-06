"""
This scrpit is to clean Official Subcontracting (BSMSA) data in csv or excel files
"""

import numpy as np
import pandas as pd
import z2h


input_path = "../Input/data_in_offical_documents/SubcontractData/"
output_path = "../Output/"


def clean_subcontract():

    subcontract_manu = pd.read_csv(
        input_path + 'ChushoHakusyo_2003_fig2-4-1_SME_subcontracting_ratio.csv',
        encoding='Shift_JIS', skiprows=3, skipfooter=5,
        names=['ind', 1966, 1971, 1976, 1981, 1987, 1998],)
    subcontract_manu = subcontract_manu.set_index('ind').stack().reset_index()
    subcontract_manu.columns = ['ind', 'year', 'subcontract_ratio']
    subcontract_manu.ind = subcontract_manu.ind.replace('製造業全体', 'ALL')
    subcontract_manu.subcontract_ratio = subcontract_manu.subcontract_ratio.apply(pd.to_numeric, errors='coerce')

    return subcontract_manu


def main():
    clean_subcontract().to_pickle(output_path + 'Offical_Subcontract.pkl')


if __name__ == "__main__":
    main()
