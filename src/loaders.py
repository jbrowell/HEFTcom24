"Functions for loading and formatting Rebase Data"
import datetime
import importlib

import numpy as np
import pandas as pd
import xarray as xr

import utils as utils

creation_funcs = {}

#  ╭──────────────────────────────────────────────────────────╮
#  │ Data Loaders                                             │
#  ╰──────────────────────────────────────────────────────────╯


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


#  ╭──────────────────────────────────────────────────────────╮
#  │ Abstract Loaders                                         │
#  ╰──────────────────────────────────────────────────────────╯


def register(name: str, module):
    """Register modules such as datasets and models"""
    creation_funcs[name] = module


def load_module(name, config, inputs):
    module = importlib.import_module(config.module)  # type: ignore
    module.initialize()
    try:
        creation_func = creation_funcs[name]
        return creation_func(config, inputs)
    except KeyError:
        raise ValueError from None


#  ╭──────────────────────────────────────────────────────────╮
#  │ Tmp Loaders                                             │
#  ╰──────────────────────────────────────────────────────────╯


def get_local_data(data_dir):
    "Read from local, static datasets. Taken from `Getting Started` notebook"
    hornsea = xr.open_dataset(
        f"{data_dir}/dwd/dwd_icon_eu_hornsea_1_20200920_20231027.nc"
    )
    hornsea_features = (
        hornsea["WindSpeed:100"]
        .mean(dim=["latitude", "longitude"])
        .to_dataframe()
        .reset_index()
    )
    hornsea_features["ref_datetime"] = hornsea_features["ref_datetime"].dt.tz_localize(
        "UTC"
    )
    hornsea_features["valid_datetime"] = hornsea_features[
        "ref_datetime"
    ] + pd.TimedeltaIndex(hornsea_features["valid_datetime"], unit="hours")

    solar = xr.open_dataset(f"{data_dir}/dwd/dwd_icon_eu_pes10_20200920_20231027.nc")

    solar_features = (
        solar["SolarDownwardRadiation"].mean(dim="point").to_dataframe().reset_index()
    )
    solar_features["ref_datetime"] = solar_features["ref_datetime"].dt.tz_localize(
        "UTC"
    )
    solar_features["valid_datetime"] = solar_features[
        "ref_datetime"
    ] + pd.TimedeltaIndex(solar_features["valid_datetime"], unit="hours")

    energy_data = pd.read_csv(f"{data_dir}/Energy_Data_20200920_20231027.csv")
    energy_data["dtm"] = pd.to_datetime(energy_data["dtm"])
    energy_data["Wind_MWh_credit"] = (
        0.5 * energy_data["Wind_MW"] - energy_data["boa_MWh"]
    )
    energy_data["Solar_MWh_credit"] = 0.5 * energy_data["Solar_MW"]

    table = hornsea_features.merge(
        solar_features, how="outer", on=["ref_datetime", "valid_datetime"]
    )

    table = (
        table.set_index("valid_datetime")
        .groupby("ref_datetime")
        .resample("30T")
        .interpolate("linear")
    )
    table = table.drop(columns="ref_datetime", axis=1).reset_index()
    table = table.merge(
        energy_data, how="inner", left_on="valid_datetime", right_on="dtm"
    )
    table = table[
        table["valid_datetime"] - table["ref_datetime"] < np.timedelta64(50, "h")
    ]
    table.rename(columns={"WindSpeed:100": "WindSpeed"}, inplace=True)
    table = table[table["SolarDownwardRadiation"].notnull()]
    table = table[table["WindSpeed"].notnull()]
    table["total_generation_MWh"] = table["Wind_MWh_credit"] + table["Solar_MWh_credit"]
    return table
