import SBTi
from SBTi.temperature_score import TemperatureScore
from SBTi.interfaces import ETimeFrames, EScope
import pandas as pd
import logging
root_logger = logging.getLogger()
root_logger.setLevel("INFO")
import datetime


class TemperatureScoresCreator:
    """This class creates a dataset in correct format from the input data with the SBTi temperature score model"""

    def __init__(self, input_data, temperature_score_model, matter_metrics):
        self.input_data = input_data
        self.target_data = input_data.target_data
        self.temperature_score_model = temperature_score_model
        self.matter_metrics = matter_metrics
        self.metric_id_mapper = dict(zip(self.matter_metrics.metric_name,
                                         self.matter_metrics.metric_id))
        self.output_sbti_format = None
        self.output_df = None

        self.create_output_df()

    def create_output_df(self):
        """creates the output df in correct format"""
        self.output_sbti_format = self.temperature_score_model.calculate(data_providers=[self.input_data.target_data],
                                                                    portfolio=self.input_data.companies)
        output = self.output_sbti_format[["company_id", "company_name", "time_frame", "scope", "temperature_score"]]
        output["time_frame"] = output["time_frame"].apply(lambda x: x.value)
        output["scope"] = output["scope"].apply(lambda x: x.value).apply(lambda x: str(x).replace("+", "_"))

        output["Metric"] = output["time_frame"].astype(str)+"_term_"+output["scope"].astype(str)+"_temperature_score"
        output["Metric"] = output["Metric"].apply(lambda x: x.upper())
        output["Unit"] = "DEGREE CELSIUS"
        output["MUCID"] = ""  # TODO: add mucid attaching function somewhere
        output["Identifier"] = "ISIN:"+output["company_id"]
        output["Metric ID"] = output["Metric"].map(self.metric_id_mapper)
        output["Value type"] = "Calculated"
        output["Source"] = "SBTi"
        output["Date start"] = "01/01/"+str(datetime.date.today().year)  # TODO: ???
        output["Date end"] = "31/12/"+str(datetime.date.today().year)  # TODO: ???
        output = output.rename(columns={"temperature_score": "Value",
                               "company_name": "Name"})

        self.output_df = output[["Metric", "Value", "Unit", "MUCID", "Identifier", "Name", "Metric ID", "Value type",
                                 "Source", "Date start", "Date end"]]
