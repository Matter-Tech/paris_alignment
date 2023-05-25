import pandas as pd


class CVaRCreatorExistingTargets:
    """this class creates a Climate Value at Risk df for companies and timeframe combos with existing valid targets"""

    def __init__(self, sbti_df, carbon_prices, scores):
        self.sbti_df = sbti_df
        self.carbon_prices = carbon_prices
        self.scores = scores
        self.detailed_cvar_df = pd.DataFrame
        self.simple_cvar_df = pd.DataFrame

    def detailed_calculation(self):
        self.filter_sbti_df()
        self.existing_annual_reduction()
        self.carbon_price()
        for score in self.scores:
            self.calculate_total_price(score)

    def create_simple_output(self):
        df_simple_list = []
        for tf in ["SHORT", "MID", "LONG"]:
            df = self.detailed_cvar_df[self.detailed_cvar_df["time_frame"] == tf]
            df_simple = df[
                ["company_id"]+["total_price_of_additional_reduction_"+str(score) for score in self.scores]]
            df_simple = df_simple.rename(columns={"company_id": "ISIN"})
            df_simple = df_simple.rename(
                columns=dict(zip(["total_price_of_additional_reduction_"+str(score) for score in self.scores],
                                 [tf+" TERM "+str(score) for score in self.scores])))
            df_simple_list.append(df_simple)
        self.simple_cvar_df = df_simple_list[0].merge(
            df_simple_list[1], on="ISIN", how="outer").merge(
            df_simple_list[2], on="ISIN", how="outer")

    def filter_sbti_df(self):
        self.detailed_cvar_df = self.sbti_df[(self.sbti_df["scope"] == "S1S2") &
                                             (self.sbti_df["annual_reduction_rate"].notna()) &
                                             (self.sbti_df["temperature_score"].astype(float) != 3.2)]

        self.detailed_cvar_df = self.detailed_cvar_df[
            ["company_id", "time_frame", "scope", "target_type", "intensity_metric", "coverage_s1", "coverage_s2",
             "reduction_ambition", "base_year", "base_year_ghg_s1", "base_year_ghg_s2", "start_year", "end_year",
             "achieved_reduction", "company_name", "sr15", "annual_reduction_rate",	"slope", "variable", "param",
             "intercept", "r2",	"temperature_score"]]

    def existing_annual_reduction(self):
        self.detailed_cvar_df["existing_target_annual_emissions_reduction"] = \
            self.detailed_cvar_df["annual_reduction_rate"] * (
                self.detailed_cvar_df["base_year_ghg_s1"] + self.detailed_cvar_df["base_year_ghg_s2"])

    def carbon_price(self):
        self.detailed_cvar_df["start_year"] = self.detailed_cvar_df["start_year"].astype(int)
        self.detailed_cvar_df["end_year"] = self.detailed_cvar_df["end_year"].astype(int)
        self.detailed_cvar_df["years_list"] = self.detailed_cvar_df.apply(
            lambda x: list(range(x["start_year"], x["end_year"])), axis=1)
        self.detailed_cvar_df["carbon_prices_list"] = self.detailed_cvar_df["years_list"].apply(
            lambda x: [self.carbon_prices[year] for year in x])
        self.detailed_cvar_df["carbon_prices_sum"] = self.detailed_cvar_df["carbon_prices_list"].apply(lambda x: sum(x))

    def calculate_total_price(self, score):
        """start with 1.5C. We will add 2 and 4 later"""
        self.detailed_cvar_df["required_annual_reduction_rate_"+str(score)] = \
            (score - self.detailed_cvar_df["intercept"]) / (self.detailed_cvar_df["param"] * 100)
        self.detailed_cvar_df["required_annual_emissions_reduction_"+str(score)] = \
            self.detailed_cvar_df["required_annual_reduction_rate_"+str(score)] * (
                self.detailed_cvar_df["base_year_ghg_s1"] + self.detailed_cvar_df["base_year_ghg_s2"])
        self.detailed_cvar_df["required_additional_annual_emissions_reduction_"+str(score)] = \
            self.detailed_cvar_df["required_annual_emissions_reduction_"+str(score)] - \
            self.detailed_cvar_df["existing_target_annual_emissions_reduction"]
        self.detailed_cvar_df["total_price_of_additional_reduction_"+str(score)] = \
            self.detailed_cvar_df["required_additional_annual_emissions_reduction_"+str(score)] * \
            self.detailed_cvar_df["carbon_prices_sum"]
