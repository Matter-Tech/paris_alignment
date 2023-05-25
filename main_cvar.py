import pandas as pd
import datetime
from components.cvar_existing_targets.cvar_existing_targets import CVaRCreatorExistingTargets


run_time_point = datetime.datetime.now().strftime('%Y_%m_%d___%H_%M_%S')

temperature_scores = [1.5, 2, 4]

sbti_output_file_name = "temperature_scores_sbti_format___2023_05_25___14_05_35.xlsx"
carbon_prices_file_name = "yearly_carbon_prices_test.xlsx"

sbti_df = pd.read_excel("output_scores/"+sbti_output_file_name)

prices_df = pd.read_excel(carbon_prices_file_name)
prices_dict = dict(zip(prices_df["year"], prices_df["carbon_price"]))

cvar_calc = CVaRCreatorExistingTargets(sbti_df=sbti_df, carbon_prices=prices_dict, scores=temperature_scores)
cvar_calc.detailed_calculation()
cvar_calc.create_simple_output()
cvar_calc.detailed_cvar_df.to_excel("output_cvar/detailed_cvar_df___"+run_time_point+".xlsx", index=False)
cvar_calc.simple_cvar_df.to_excel("output_cvar/simple_cvar_df___"+run_time_point+".xlsx", index=False)
