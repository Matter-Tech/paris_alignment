import pandas as pd
import numpy as np


class TargetsDataFormatter:
    """This class formats the targets file provided by Datacie into the necessary format for the SBTi tool"""

    def __init__(self, source_df):
        self.source_df = source_df
        self.formatted_df = None

    def format_data(self):
        for col in self.source_df.columns:
            self.source_df[col] = self.source_df[col].apply(lambda x: x.lower() if type(x) == str else x)
        self.format_numerical_columns()
        self.create_one_to_one_columns()
        self.clean_scope()
        self.create_coverage()
        self.clean_intensity_metric()
        self.create_target_type()
        self.clean_base_year_emissions()
        self.divide_base_year_emissions()
        self.convert_achieved_reduction()
        columns_for_output = ["company_name", "company_id", "target_type", "intensity_metric", "scope", "coverage_s1",
                              "coverage_s2", "coverage_s3", "reduction_ambition", "base_year", "end_year", "start_year",
                              "base_year_ghg_s1", "base_year_ghg_s2", "base_year_ghg_s3", "achieved_reduction"]
        self.formatted_df = self.source_df[columns_for_output]

    def format_numerical_columns(self):
        """make all numerical columns floats"""
        num_cols = ["Baseline year", "Base year emissions value", "Start year", "Target year", "Reduction ambition",
                    "Achievement as of year", "Achievement value"]
        for col in num_cols:
            self.source_df[col] = np.where(self.source_df[col] == "unspecified", np.nan, self.source_df[col])
            self.source_df[col] = self.source_df[col].apply(
                lambda x: float(x.replace("%", "")) / 100 if type(x) == str and "%" in x else x).astype(float)

    def create_one_to_one_columns(self):
        """create columns for the output file that are exact copies of columns in the source file"""
        self.source_df["company_name"] = self.source_df["Company name"]
        # self.source_df["company_id"] = ""  we have manually inserted an id column
        self.source_df["reduction_ambition"] = self.source_df["Reduction ambition"]
        self.source_df["base_year"] = self.source_df["Baseline year"]
        self.source_df["end_year"] = self.source_df["Target year"]
        self.source_df["start_year"] = self.source_df["Start year"]

    def clean_scope(self):
        """
        Clean "scope of target" and remove those with subcategories
        """
        self.source_df["scope"] = self.source_df["Scope of target"].apply(eval).apply(
            lambda x: "+".join(x)).apply(lambda x: x.replace("cope ", "").upper())

        # FOR NOW remove rows with sub-scopes as we don't know the coverage but can assume that it's much less than the
        # minimum. The best thing would be to manually look up those companies' targets.
        self.source_df = self.source_df[~self.source_df["scope"].str.contains("-")]
        self.source_df = self.source_df.drop(columns=["Scope of target"])
        # print(self.source_df["scope"])

    def create_coverage(self):
        """
        Write coverage in the columns associated with the scopes.
        If nothing else specified, write 1 in relevant coverage column.
        """
        self.source_df["coverage_s1"] = np.where(self.source_df["scope"].str.contains("s1"), 1, np.nan)
        self.source_df["coverage_s2"] = np.where(self.source_df["scope"].str.contains("s2"), 1, np.nan)
        self.source_df["coverage_s3"] = np.where(self.source_df["scope"].str.contains("s3"), 1, np.nan)

    def clean_intensity_metric(self):
        """
        Clean "intensity metric"
        "Not Applicable" = blank
        "Per xxx" = "xxx"
        """
        self.source_df["intensity_metric"] = self.source_df["Intensity Metric"].apply(
            lambda x: x.replace("per ", "")if type(x) == str and "per " in x else x).apply(
            lambda x: np.nan if x == "not applicable" else x)
        self.source_df = self.source_df.drop(columns=["Intensity Metric"])

    def create_target_type(self):
        """
        Create "target_type" column
        If "intensity metric" blank, "Absolute"
        else, "Intensity"
        """
        self.source_df["target_type"] = np.where(self.source_df["intensity_metric"].notna(),
                                                 "intensity",
                                                 "absolute")

    def clean_base_year_emissions(self):
        """
        Base year emissions value
        Replace "Unspecified" by nans.
        Multiply base year emissions if not in tonnes (for now we have only seen kilos, will maybe need to add more
        unit conversions once we get full data
        """
        self.source_df["Base year emissions value"] = np.where(
            "kilograms of co2" in self.source_df["Base year emissions unit"],
            self.source_df["Base year emissions value"] / 1000,
            self.source_df["Base year emissions value"]
        )

    def divide_base_year_emissions(self):
        """
        divide emissions between the relevant scopes, into separate columns
        """
        self.source_df["base_year_ghg_s1"] = \
            np.where(
                self.source_df["scope"] == "s1",
                self.source_df["Base year emissions value"],
                np.where(
                    self.source_df["scope"] == "s1+s2",
                    self.source_df["Base year emissions value"] / 2,
                    np.where(
                        self.source_df["scope"] == "s1+s2+s3",
                        self.source_df["Base year emissions value"] / 3,
                        np.nan
                    )
                )
            )
        self.source_df["base_year_ghg_s2"] = \
            np.where(
                self.source_df["scope"] == "s2",
                self.source_df["Base year emissions value"],
                np.where(
                    self.source_df["scope"] == "s1+s2",
                    self.source_df["Base year emissions value"] / 2,
                    np.where(
                        self.source_df["scope"] == "s1+s2+s3",
                        self.source_df["Base year emissions value"] / 3,
                        np.nan
                    )
                )
            )
        self.source_df["base_year_ghg_s3"] = \
            np.where(
                self.source_df["scope"] == "s3",
                self.source_df["Base year emissions value"],
                np.where(
                    self.source_df["scope"] == "s1+s2+s3",
                    self.source_df["Base year emissions value"] / 3,
                    np.nan
                    )
                )

    def convert_achieved_reduction(self):
        """
        If achieved_reduction is in absolute terms, convert to %
        First convert reduction ambition to absolute terms, amb_abs = amb_pct * e
        Make sure that amb_abs amd ach_abs are in same unit!!
        Then get ach_pct = ach_abs / amb_abs
        If achieved_reduction is in percentage reduction from baseline year, get it in % of ambition:
        ach_pct = ach_pact_base / amb_pct
        """

        self.source_df["achieved_reduction"] = np.where(
                self.source_df["Achievement unit"] == "percentage reduction from baseline year",
                self.source_df["Achievement value"] / self.source_df["reduction_ambition"],
                np.where(
                    self.source_df["Achievement unit"] == self.source_df["Base year emissions unit"],
                    self.source_df["Achievement value"] /
                    (self.source_df["reduction_ambition"] *
                     self.source_df["Base year emissions value"]),
                    np.where(
                        self.source_df["Achievement unit"] == "percentage of the reduction ambition",
                        self.source_df["Achievement value"],
                        np.where(
                            self.source_df["Achievement value"].isna(),
                            self.source_df["Achievement value"],
                            -1
                        )
                    )
                )
        )
        # Only works if reduction ambition is in % in the data. It is in the sample but remember to check the real data
