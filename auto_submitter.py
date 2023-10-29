import comp_utils
import pandas as pd
import numpy as np
import xarray as xr
from statsmodels.iolib.smpickle import load_pickle


# Get latest weather forecasts
latest_dwd_Hornsea1 = comp_utils.weather_df_to_xr(comp_utils.get_hornsea_dwd())
latest_dwd_Hornsea1_features = latest_dwd_Hornsea1["WindSpeed:100"].mean(dim=["latitude","longitude"]).to_dataframe().reset_index()

latest_dwd_solar = comp_utils.weather_df_to_xr(comp_utils.get_pes10_nwp("DWD_ICON-EU"))
latest_dwd_solar_features = latest_dwd_solar["SolarDownwardRadiation"].mean(dim="point").to_dataframe().reset_index()

latest_forcast_table = latest_dwd_Hornsea1_features.merge(latest_dwd_solar_features,how="outer",on=["ref_datetime","valid_datetime"])
latest_forcast_table = latest_forcast_table.set_index("valid_datetime").resample("30T").interpolate("linear",limit=5).reset_index()
latest_forcast_table.rename(columns={"WindSpeed:100":"WindSpeed"},inplace=True)

# Produce quantile forecasts
for quantile in range(10,100,10):
    loaded_model = load_pickle(f"models/model_q{quantile}.pickle")
    latest_forcast_table[f"q{quantile}"] = loaded_model.predict(latest_forcast_table)

# Make submission
submission_data=pd.DataFrame({"datetime":comp_utils.day_ahead_market_times()})
submission_data = submission_data.merge(latest_forcast_table,how="left",left_on="datetime",right_on="valid_datetime")
submission_data["market_bid"] = submission_data["q50"]

submission_data = comp_utils.prep_submission_in_json_format(submission_data)
# print(submission_data)

comp_utils.submit(submission_data)