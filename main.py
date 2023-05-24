import pandas as pd
import datetime

from components.targets_data_formatter.targets_data_formatter import TargetsDataFormatter
from components.targets_data_validator.targets_data_validator import TargetsDataValidator
from components.companies_data_formatter.companies_data_formatter import CompaniesDataFormatter
from components.temperature_scores_input_data_reader.temperature_scores_input_data_reader import \
    TemperatureScoresInputDataReader
from components.temperature_scores_data_creator.temperature_scores_data_creator import TemperatureScoresCreator
import SBTi
from SBTi.temperature_score import TemperatureScore
from SBTi.interfaces import ETimeFrames, EScope

# name of the intermediary file that is output by the formatters and needed as input in SBTi tool
targets_fundamental_file_name = "fundamental_and_targets_data.xlsx"

run_time_point = datetime.datetime.now().strftime('%Y_%m_%d___%H_%M_%S')

# copy latest matter_metrics file #TODO: add function to read the latest from matter_data repo
matter_metrics = pd.read_csv("matter_metrics.csv", sep=";")

# raw targets file
raw_targets_name = "GHG Emissions Target Data - 7 Diverse Companies Sample.csv"

# raw targets file with errors: use this file to check that the validator works correctly
raw_targets_name_with_errors = "with_errors_GHG Emissions Target Data - 7 Diverse Companies Sample.csv"


raw_targets_df = pd.read_csv("data/target_data_input/"+raw_targets_name, sep=";")

# format targets
targets_formatter = TargetsDataFormatter(raw_targets_df)
targets_formatter.format_data()
formatted_targets_df = targets_formatter.formatted_df

# validate formatted targets
targets_validator = TargetsDataValidator(formatted_targets_df)
targets_validator.validate()

# format companies dfs
companies_formatter = CompaniesDataFormatter(formatted_targets_df)
companies_formatter.format_data()
companies_df = companies_formatter.companies_df
fundamental_df = companies_formatter.fundamental_df

# create intermediary file
writer = pd.ExcelWriter(targets_fundamental_file_name, engine="xlsxwriter")
fundamental_df.to_excel(writer, sheet_name="fundamental_data", index=False)
formatted_targets_df.to_excel(writer, sheet_name="target_data", index=False)
writer.close()

# read all input data for SBTi tool
input_data = TemperatureScoresInputDataReader(companies_df=companies_df,
                                              target_data_name=targets_fundamental_file_name)

# temperature score model from SBTi tool
temperature_score_model = TemperatureScore(time_frames=list(ETimeFrames),
                                           scopes=list(EScope))

# calculate temperature scores using model and input data
scores = TemperatureScoresCreator(input_data=input_data,
                                  temperature_score_model=temperature_score_model,
                                  matter_metrics=matter_metrics)

output_df = scores.output_df
output_df.to_csv(f"output/temperature_scores___{run_time_point}.csv",sep=";", index=False,
                 encoding="utf-8", date_format='%d/%m/%Y')

# only needed for analysis, comment out if not needed
output_sbti_format = scores.output_sbti_format
output_sbti_format.to_excel(f"output/temperature_scores_sbti_format___{run_time_point}.xlsx", index=False)
