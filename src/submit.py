import os

import numpy as np
import pandas as pd
import xarray as xr
from dotenv import load_dotenv
from statsmodels.iolib.smpickle import load_pickle

import utils
from loaders import get_day_ahead_market_times, get_hornsea_data, get_solar_data
from rebase_api import RebaseAPI

if __name__ == "__main__":
    # INIT API KEY
    load_dotenv()
    api_key = os.getenv("api_key")
    rebase = RebaseAPI(api_key)

    # LOAD DATA
    solar = get_solar_data(rebase)
    hornsea = get_hornsea_data(rebase)

    current_forecasts = utils.format_forecast_table(hornsea, solar)

    # FORECASTING
    for quantile in range(10, 100, 10):
        # TODO: Want to stick with these naming conventions?
        # Maybe for multiple models want to specify in a params.yaml?
        model = load_pickle(f"models/model_q{quantile}.pickle")
        current_forecasts[f"q{quantile}"] = model.predict(current_forecasts)

    # SUBMITTING
    submission_data = pd.DataFrame({"datetime": get_day_ahead_market_times()})
    submission_data = submission_data.merge(
        current_forecasts, how="left", left_on="datetime", right_on="valid_datetime"
    )
    submission_data["market_bid"] = submission_data["q50"]

    submission_data = utils.prep_submission_in_json_format(submission_data)

    rebase.submit(submission_data)
