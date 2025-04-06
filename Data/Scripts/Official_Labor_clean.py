"""
This scrpit is to clean Official Labor data in excel files
"""

import numpy as np
import pandas as pd
import z2h


input_path_L = "../Input/data_in_offical_documents/LaborData/"
output_path = "../Output/"


def labor_JIL_extractor(filename, colnames,):
    df = (pd.read_excel(input_path_L+filename, head=None, index=False, names=colnames)
          .assign(year=lambda x: x.year.astype(str).str.replace('\.0+', ''))
          )
    mask_year = df.year.str.contains('^\d{4}', na=False)
    df = (df.loc[mask_year]
          .assign(year=lambda x: x.year.astype(int))
          .set_index('year')
          .apply(pd.to_numeric, errors='coerce'))
    return df


def clean_labor_JIL():

    dfs = pd.DataFrame()
    # II-1
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図1_労働力人口.xls'
    colnames = ['year', '15+_population', 'labor_force']
    df = labor_JIL_extractor(filename, colnames)
    dfs = pd.concat([dfs, df], axis=1,)
    # II-2-1
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図2-1_就業者、雇用者(労働力人口、就業者、雇用者、常雇、正規の職員・従業員).xls'
    colnames = ['year', 'labor_force', 'employment', 'employee', 'regular_employee', 'formal_employee']
    df = labor_JIL_extractor(filename, colnames)
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, suffixes=('', '_'))
    # II-2-2
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図2-2_就業者、雇用者(就業者、従業上の地位).xls'
    colnames = ['year', 'employment', 'individual_proprietor', 'family_worker',
                'employee', 'regular_employee', 'temporary_employee', 'daily_employee']
    df = labor_JIL_extractor(filename, colnames)
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, suffixes=('', '_'))
    # II-3-1
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図3-1_労働力率、就業率.xls'
    colnames = ['year', 'labor_force_rate', 'employment_rate', ]
    df = labor_JIL_extractor(filename, colnames)
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, suffixes=('', '_'))

    dfs = (dfs.T.drop_duplicates().T
           .assign(unemployment=lambda x: x.labor_force - x.employment,
                   temporary_daily_employee=lambda x: x.temporary_employee + x.daily_employee,
                   individual_family_worker=lambda x: x.individual_proprietor + x.family_worker,
                   )
           #    .reset_index().melt('year', var_name='var')
           #    .assign(industry="ALL")
           )

    # II-4
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図4_産業別就業者数.xls'
    colnames = ['year', 'employment', 'employment_Sec1', 'employment_Sec2', 'employment_Sec3',
                'employment', 'employment_AFF', 'employment_Min', 'employment_Constr',
                'employment_Manu', 'employment_Sale', 'employment_FinReal', 'employment_Oth']
    df = labor_JIL_extractor(filename, colnames)
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, suffixes=('', '_'))
    # II-5
    filename = 'グラフでみる長期労働統計_II労働力、就業、雇用_図5_産業別雇用者数.xls'
    colnames = ['year', 'employee', 'employee_Sec1', 'employee_Sec2', 'employee_Sec3',
                'employee', 'employee_AFF', 'employee_Min', 'employee_Constr',
                'employee_Manu', 'employee_Sale', 'employee_FinReal', 'employee_Oth']
    df = labor_JIL_extractor(filename, colnames)
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, suffixes=('', '_'))
    dfs = (dfs.T.drop_duplicates().T
           .assign(employment_NALL=lambda x: x.employment_Sec2 + x.employment_Sec3,
                   employee_NALL=lambda x: x.employee_Sec2 + x.employee_Sec3,
                   nonemployee_NALL=lambda x: x.employment_NALL - x.employee_NALL
                   )
           )

    # IV-1, VI-1
    filename = "グラフでみる長期労働統計_Ⅳ賃金_図1_賃金.xls"
    wage = pd.read_excel(input_path_L+filename,
                         skiprows=7, usecols=[0, 2], names=['year', 'wage'], skipfooter=3,)
    filename = "グラフでみる長期労働統計_Ⅵ物価、家計_図1_物価.xls"
    inflation = (pd.read_excel(input_path_L+filename,
                               skiprows=3, usecols=[1, 4], names=['year', 'inflation'], skipfooter=2,)
                 .assign(year=lambda x: range(1947, 1947+len(x)))
                 )
    df = wage.merge(inflation).set_index('year')
    dfs = dfs.merge(df, how='outer', left_index=True, right_index=True, )

    return dfs


def main():
    clean_labor_JIL().to_pickle(output_path+'Offical_JIL_LaborSupply.pkl')


if __name__ == "__main__":
    main()
