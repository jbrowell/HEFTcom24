"Functions for loading and formatting Rebase Data"
import datetime

import pandas as pd

import utils as utils


def get_hornsea_data(api_connection):
    pull = utils.weather_df_to_xr(api_connection.get_hornsea_dwd())
    hornsea_features = (
        pull["WindSpeed:100"]
        .mean(dim=["latitude", "longitude"])
        .to_dataframe()
        .reset_index()
    )
    return hornsea_features


def get_solar_data(api_connection):
    pull = utils.weather_df_to_xr(api_connection.get_pes10_nwp("DWD_ICON-EU"))
    solar_features = (
        pull["SolarDownwardRadiation"].mean(dim="point").to_dataframe().reset_index()
    )
    return solar_features


def get_next_day_market_times(today_date=pd.to_datetime("today")):
    tomorrow_date = today_date + pd.Timedelta(1, unit="day")
    DA_Market = [
        pd.Timestamp(
            datetime.datetime(
                today_date.year, today_date.month, today_date.day, 23, 0, 0
            ),
            tz="Europe/London",
        ),
        pd.Timestamp(
            datetime.datetime(
                tomorrow_date.year, tomorrow_date.month, tomorrow_date.day, 22, 30, 0
            ),
            tz="Europe/London",
        ),
    ]

    DA_Market = pd.date_range(
        start=DA_Market[0], end=DA_Market[1], freq=pd.Timedelta(30, unit="minute")
    )

    return DA_Market
