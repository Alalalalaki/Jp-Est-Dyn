"""
This code generates the data moments
"""


import pandas as pd
import statsmodels.api as sm

import project_path
from Data_General import input_path, clean_df
from Figure_entry_rate import calculate_entry_exit_rate
from Figure_life_cycle_growth import output_life_growth


class Moments:
    def __init__(self, year=1969, avg_years="full",
                 ind="NALL", org="employer"):

        self._full_years = (1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006)
        assert year in self._full_years, f"year must be one in {self._full_years}"
        self.year = year
        if avg_years == "full":
            self.avg_years = self._full_years
        else:
            assert set(avg_years).issubset(set(self._full_years)
                                           ), f"avg_years must be either 'full', or a subset of {self._full_years}"
            self.avg_years = avg_years
        self.ind = ind
        self.org = org

        self.dfa = (pd.read_pickle(input_path+'EEC_Establishment_age.pkl')
                      .pipe(clean_df)
                      .query("organization==@org & industry==@ind"))
        self.dfl = pd.read_pickle(input_path+'Offical_JIL_LaborSupply.pkl')

        # common results
        self.entry_exit = calculate_entry_exit_rate(self.dfa, method="1", org=self.org, ind=self.ind)
        self.life_growth = self._get_life_growth()

        # labor growth rate
        self.LSgrowth = self._set_labor_growth()

        self.moment = self._set_moments_for_one_year(self.year)
        self.avgmoment = self._set_average_moments(self.avg_years)

    def _get_life_growth(self,):
        age = 1
        years = [1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006]
        life_growth = pd.DataFrame()
        for y in years:
            life_age, life_size = output_life_growth(self.dfa, cohort=[y, age], ind=self.ind, org=self.org)
            lg = (pd.Series(life_size, index=life_age)
                  .reindex(range(1, 40))
                  .interpolate(limit_area="inside")
                  .rename(y))
            life_growth = pd.concat([life_growth, lg], axis=1)
        return life_growth

    def get_avg_life_growth(self, age=(1, 10), years=None):
        """
        years == None: use self.avg_years
        years == "full": all use avaiable years
        years == (...): use specified years
        """
        if age[0] == age[1]:
            return 1
        if years == "full":
            df = self.life_growth.dropna(axis=1, subset=[age[1]]).loc[age, :]
        else:
            years = self.avg_years if years == None else years
            df = self.life_growth.loc[age, years]

        if df.isna().sum().sum() > 0:
            print(f"Caution: some size data is missing for the age {age} and the years {years} given.")
            # print(df)
            df = df.dropna(axis=1)

        life_growth_rate = df.pct_change().mean(axis=1)[age[1]]
        return life_growth_rate * 100

    def _set_labor_growth(self,):
        cols = ['employee_NALL', 'employment_NALL',
                'employment', 'labor_force'
                ]
        labor_supply = self.dfl[cols].dropna(how="all")
        labor_supply_hp = labor_supply.apply(
            lambda x: sm.tsa.filters.hpfilter(x.dropna(),
                                              6.25)[1]).rename(
            columns=lambda x: x + "_hp")
        labor_supply = pd.concat([labor_supply, labor_supply_hp], axis=1)
        labor_growth = (labor_supply.pct_change() * 100).dropna(how="all")
        return labor_growth

    def get_avg_labor_growth(self, org="employee_NALL", years=None):
        if years == None:
            s = self.avg_years[0]
            e = self.avg_years[-1]
            lg = self.LSgrowth.loc[s:e, org].mean()
        return lg

    def _set_moments_for_one_year(self, year):
        df = self.dfa.query("year == @year")
        entry_exit = self.entry_exit.query('year == @year')

        # entry & exit rate
        entry = entry_exit.entry_rate.values[0]
        exit_ = entry_exit.exit_rate.values[0]

        # average size + concentration/distribution
        avgsize = df.query('size=="ALL" & age=="ALL"').eval('employment / num').values[0]

        num_ALL = df.query('size=="ALL" & age=="ALL"').num.values[0]
        emp_ALL = df.query('size=="ALL" & age=="ALL"').employment.values[0]
        num_share_1_9 = df.query('size=="1~9" & age=="ALL"').num.values[0] / num_ALL * 100
        num_share_10_29 = df.query('size=="10~29" & age=="ALL"').num.values[0] / num_ALL * 100
        num_share_30_99 = df.query('size=="30~99" & age=="ALL"').num.values[0] / num_ALL * 100
        num_share_100_ = df.query('size=="100+" & age=="ALL"').num.values[0] / num_ALL * 100
        emp_share_1_9 = df.query('size=="1~9" & age=="ALL"').employment.values[0] / emp_ALL * 100
        emp_share_10_29 = df.query('size=="10~29" & age=="ALL"').employment.values[0] / emp_ALL * 100
        emp_share_30_99 = df.query('size=="30~99" & age=="ALL"').employment.values[0] / emp_ALL * 100
        emp_share_100_ = df.query('size=="100+" & age=="ALL"').employment.values[0] / emp_ALL * 100

        # average size + concentration/distribution for entrants
        entrant_age = "0~3" if year == 1969 else "1"
        entrant_avgsize = df.query('size=="ALL" & age==@entrant_age').eval('employment / num').values[0]

        entrant_num_ALL = df.query('size=="ALL" & age==@entrant_age').num.values[0]
        entrant_emp_ALL = df.query('size=="ALL" & age==@entrant_age').employment.values[0]
        entrant_num_share_1_9 = df.query('size=="1~9" & age==@entrant_age').num.values[0] / entrant_num_ALL * 100
        entrant_num_share_10_29 = df.query('size=="10~29" & age==@entrant_age').num.values[0] / entrant_num_ALL * 100
        entrant_num_share_30_99 = df.query('size=="30~99" & age==@entrant_age').num.values[0] / entrant_num_ALL * 100
        entrant_num_share_100_ = df.query('size=="100+" & age==@entrant_age').num.values[0] / entrant_num_ALL * 100
        entrant_emp_share_1_9 = df.query('size=="1~9" & age==@entrant_age').employment.values[0] / entrant_emp_ALL * 100
        entrant_emp_share_10_29 = df.query(
            'size=="10~29" & age==@entrant_age').employment.values[0] / entrant_emp_ALL * 100
        entrant_emp_share_30_99 = df.query(
            'size=="30~99" & age==@entrant_age').employment.values[0] / entrant_emp_ALL * 100
        entrant_emp_share_100_ = df.query(
            'size=="100+" & age==@entrant_age').employment.values[0] / entrant_emp_ALL * 100

        moments = {"entry_rate": entry,
                   "exit_rate": exit_,
                   "avgsize": avgsize,
                   "entrant_avgsize": entrant_avgsize,
                   "num_share_1_9": num_share_1_9,
                   "num_share_10_29": num_share_10_29,
                   "num_share_30_99": num_share_30_99,
                   "num_share_100_": num_share_100_,
                   "emp_share_1_9": emp_share_1_9,
                   "emp_share_10_29": emp_share_10_29,
                   "emp_share_30_99": emp_share_30_99,
                   "emp_share_100_": emp_share_100_,
                   "entrant_num_share_1_9": entrant_num_share_1_9,
                   "entrant_num_share_10_29": entrant_num_share_10_29,
                   "entrant_num_share_30_99": entrant_num_share_30_99,
                   "entrant_num_share_100_": entrant_num_share_100_,
                   "entrant_emp_share_1_9": entrant_emp_share_1_9,
                   "entrant_emp_share_10_29": entrant_emp_share_10_29,
                   "entrant_emp_share_30_99": entrant_emp_share_30_99,
                   "entrant_emp_share_100_": entrant_emp_share_100_,
                   }
        moments = pd.Series(moments).rename(year)
        return moments

    def _set_average_moments(self, years=(1969, 1972, 1975, 1981, 1986, 1991, 1996, 2001, 2006)):
        df = pd.DataFrame()
        for y in years:
            moment = self._set_moments_for_one_year(y)
            df = pd.concat([df, moment], axis=1)
        avgmoment = df.mean(axis=1)
        return avgmoment


def main():
    m = Moments(year=2006, avg_years="full")
    print(m.moment)
    print(m.avgmoment)

if __name__ == "__main__":
    main()
