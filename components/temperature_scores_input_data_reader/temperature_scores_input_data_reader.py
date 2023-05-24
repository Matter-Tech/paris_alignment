import pandas as pd
import SBTi
from SBTi.data.excel import ExcelProvider


class TemperatureScoresInputDataReader:
    """This class reads the list of companies and the target data in the correct formats"""

    def __init__(self, companies_df, target_data_name):
        self.companies_df = companies_df
        self.target_data_name = target_data_name
        self.companies = None
        self.target_data = None

        self.read_companies()
        self.read_target_data()

    def read_companies(self):
        """reads the list of companies"""
        self.companies = SBTi.utils.dataframe_to_portfolio(self.companies_df)

    def read_target_data(self):
        """reads the target data"""
        self.target_data = ExcelProvider(path=self.target_data_name)
