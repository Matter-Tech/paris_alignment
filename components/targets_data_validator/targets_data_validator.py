import logging
import numpy as np

class TargetsDataValidator:
    """
    This class does some checks on the formatted data and logs warning when things seem weird.
    We can add more checks when we think there is a need for it.
    """

    def __init__(self, data):
        self.data = data
        self.logger = logging.getLogger(__name__)

    def validate(self):
        self.numerical_shares_between_0_and_1()
        self.years_realistic()
        self.emissions_not_negative()

    def numerical_shares_between_0_and_1(self):
        num_share_columns = ["coverage_s1", "coverage_s2", "coverage_s3", "reduction_ambition", "achieved_reduction"]
        for col in num_share_columns:
            if False in self.data[col].dropna().apply(lambda x: 0 <= float(x) <= 1).unique().tolist():
                self.logger.warning(f"Not all values in column {col} are between 0 and 1")

    def years_realistic(self):
        year_columns = ["base_year", "end_year", "start_year"]
        for col in year_columns:
            if False in self.data[col].dropna().apply(lambda x: 1950 <= float(x) <= 2100 or x == np.nan).unique().tolist():
                self.logger.warning(f"Not all values in column {col} seem like a realistic year")

    def emissions_not_negative(self):
        emissions_columns = ["base_year_ghg_s1", "base_year_ghg_s2", "base_year_ghg_s3"]
        for col in emissions_columns:
            if False in self.data[col].dropna().apply(lambda x: float(x) >= 0 or x == np.nan).unique().tolist():
                self.logger.warning(f"There are negative values in column {col}")

    def scope_allowed(self):
        allowed_scopes = ["S1", "S2", "S3", "S1+S2", "S1+S2+S3"]
        if False in self.data["scope"].dropna().apply(lambda x: x.isin(allowed_scopes)):
            self.logger.warning("There are values in the scope column that are not allowed")

