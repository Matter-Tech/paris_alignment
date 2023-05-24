import pandas as pd
import numpy as np


class CompaniesDataFormatter:
    """This class formats somewhat empty dfs that are needed for the SBTi tool to work"""

    def __init__(self, targets_df):
        self.targets_df = targets_df
        self.unique_name_ids = []
        self.companies_df = pd.DataFrame
        self.fundamental_df = pd.DataFrame

    def format_data(self):
        self.create_name_id_tuple_list()
        self.create_companies_df()
        self.create_fundamental_df()

    def create_name_id_tuple_list(self):
        companies_targets_df = self.targets_df[["company_name", "company_id"]]
        companies_targets_df["name_id"] = list(
            zip(companies_targets_df["company_name"], companies_targets_df["company_id"]))
        self.unique_name_ids = companies_targets_df["name_id"].unique().tolist()

    def create_companies_df(self):
        self.companies_df = pd.DataFrame(self.unique_name_ids, columns=["company_name", "company_id"])
        self.companies_df["company_isin"] = self.companies_df["company_id"]
        self.companies_df["weights"] = 1 / len(self.unique_name_ids)
        self.companies_df["investment_value"] = 1
        self.companies_df["engagement_target"] = np.nan

    def create_fundamental_df(self):
        self.fundamental_df = pd.DataFrame(self.unique_name_ids, columns=["company_name", "company_id"])
        blank_columns = ["isic", "country",	"region", "industry_level_1", "industry_level_2", "industry_level_3",
                         "industry_level_4", "sector", "company_revenue", "company_market_cap",
                         "company_enterprise_value", "company_total_assets", "company_cash_equivalents"]

        for col in blank_columns:
            self.fundamental_df[col] = np.nan
        numerical_columns = ["ghg_s1s2", "ghg_s3"]
        for col in numerical_columns:
            self.fundamental_df[col] = 1  # this is fine as long as we are not creating a s1s2s3 temp score!
        # Otherwise, we need to find the real values

