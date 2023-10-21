from requests import Session
import requests
import pandas as pd
import datetime


challenge_id = 'test_competition'
base_url = 'https://dev-api.rebase.energy'

api_key = open("team_key.txt").read() #@param {type: "string"}

headers = {
    'Authorization': f"Bearer {api_key}"
}

# Create a session so that we can reuse the auth headers
session = Session()
session.headers = headers

# Spot price
def get_spot_price(day):
  url = f"{base_url}/challenges/data/spot_price"
  params = {'day': day}
  resp = session.get(url, params=params)
  return resp.json()



# Imbalance price
def get_imbalance_price(day):
  url = f"{base_url}/challenges/data/imbalance_price"
  params = {'day': day}
  resp = session.get(url, params=params)
  return resp.json()


# Wind production Hornsea Project 1
def get_wind_production(day):
  url = f"{base_url}/challenges/data/wind_total_production"
  params = {'day': day}
  resp = session.get(url, params=params)

  data = resp.json()
  df = pd.DataFrame(data)
  return df



# Solar production Sheffield Solar PES region 1
def get_solar_production():
  url = f"{base_url}/challenges/data/solar_total_production"
  params = {'from_date': '2023-09-15', 'to_date': '2023-09-18'}
  resp = session.get(url, params=params)
  return resp.json()


# Solar and wind forecast
def get_solar_wind_forecast(day):
  url = f"{base_url}/challenges/data/solar_and_wind_forecast"
  params = {'day': day}
  resp = session.get(url, params=params)
  data = resp.json()
  df = pd.DataFrame(data)
  return df


# Day ahead demand forecast
def get_day_ahead_demand_forecast():
  url = f"{base_url}/challenges/data/day_ahead_demand"
  resp = session.get(url)
  print(resp)
  return resp.json()


# Margin forecast
def get_margin_forecast():
  url = f"{base_url}/challenges/data/margin_forecast"
  resp = session.get(url)
  print(resp)
  return resp.json()



def query_weather_latest(model, lats, lons, variables, query_type):
  url = "https://dev-api.rebase.energy/weather/v2/query"

  body = {
      'model': model,
      'latitude': lats,
      'longitude': lons,
      'variables': variables,
      'type': query_type,
      'output-format': 'json',
      'forecast-horizon': 'latest'
  }

  resp = requests.post(url, json=body, headers={'Authorization': api_key})
  print(resp.status_code)

  return resp.json()


def query_weather_latest_points(model, lats, lons, variables):
  # Data here is returned a list
  data = query_weather_latest(model, lats, lons, variables, 'points')

  df = pd.DataFrame()
  for point in range(len(data)):
    new_df = pd.DataFrame(data[0])
    new_df["point"] = point
    new_df["latitude"] = lats[point]
    new_df["longitude"] = lons[point]
    df = pd.concat([df,new_df])

  return df



def query_weather_latest_grid(model, lats, lons, variables):
  # Data here is returned as a flattened
  data = query_weather_latest(model, lats, lons, variables, 'grid')
  df = pd.DataFrame(data)

  return df




# To query Hornsea project 1 DWD_ICON-EU grid
def get_hornsea_dwd():
  # As a 6x6 grid
  lats = [53.77, 53.84, 53.9, 53.97, 54.03, 54.1]
  lons = [1.702, 1.767, 1.832, 1.897, 1.962, 2.027]

  variables = 'WindSpeed, WindSpeed:100, WindDirection, WindDirection:100, Temperature, RelativeHumidity'
  return query_weather_latest_grid('DWD_ICON-EU', lats, lons, variables)


# To query Hornsea project 1 GFS grid
def get_hornsea_gfs():
  # As a 3x3 grid
  lats = [53.59, 53.84, 54.09]
  lons = [1.522, 1.772, 2.022]

  variables = 'WindSpeed, WindSpeed:100, WindDirection, WindDirection:100, Temperature, RelativeHumidity'
  return query_weather_latest_grid('NCEP_GFS', lats, lons, variables)


def get_pes10_nwp(model):
  # As a list of points
  lats = [52.4872562, 52.8776682, 52.1354277, 52.4880497, 51.9563696, 52.2499177, 52.6416477, 52.2700912, 52.1960768, 52.7082618, 52.4043468, 52.0679429, 52.024023, 52.7681276, 51.8750506, 52.5582373, 52.4478922, 52.5214863, 52.8776682, 52.0780721]
  lons = [0.4012455, 0.7906532, -0.2640343, -0.1267052, 0.6588173, 1.3894081, 1.3509559, 0.7082557, 0.1534462, 0.7302284, 1.0762977, 1.1751747, 0.2962684, 0.1699257, 0.9115028, 0.7137489, 0.1204872, 1.5706825, 1.1916542, -0.0113488]

  variables = 'SolarDownwardRadiation, CloudCover, Temperature'
  return query_weather_latest_points(model, lats, lons, variables)




def get_demand_nwp(model):
  # As list of points
  lats = [51.479, 51.453, 52.449, 53.175, 55.86, 53.875, 54.297]
  lons = [-0.451, -2.6, -1.926, -2.986, -4.264, -0.442, -1.533]

  variables = 'Temperature, WindSpeed, WindDirection, TotalPrecipitation, RelativeHumidity'
  return query_weather_latest_points(model, lats, lons, variables)


# Convert nwp data frame to xarray
def weather_df_to_xr(weather_data):
    
    weather_data["ref_datetime"] = pd.to_datetime(weather_data["ref_datetime"],utc=True)
    weather_data["valid_datetime"] = pd.to_datetime(weather_data["valid_datetime"],utc=True)

    
    if 'point' in weather_data.columns:
      weather_data = weather_data.set_index(["ref_datetime",
                                            "valid_datetime",
                                            "point"])
    else:
        weather_data = pd.melt(weather_data,id_vars=["ref_datetime","valid_datetime"])
    
        weather_data = pd.concat([weather_data,
                              weather_data["variable"].str.split("_",expand=True)],
                             axis=1).drop(['variable',1,3], axis=1)
    
        weather_data.rename(columns={0:"variable",2:"latitude",4:"longitude"},inplace=True)
    
        weather_data = weather_data.set_index(["ref_datetime",
                                            "valid_datetime",
                                            "longitude",
                                            "latitude"])
        weather_data = weather_data.pivot(columns="variable",values="value")
    
    weather_data = weather_data.to_xarray()
 
    weather_data['ref_datetime'] = pd.DatetimeIndex(weather_data['ref_datetime'].values,tz="UTC")
    weather_data['valid_datetime'] = pd.DatetimeIndex(weather_data['valid_datetime'].values,tz="UTC")

    return weather_data



def day_ahead_market_times(today_date=pd.to_datetime('today')):

    tomorrow_date = today_date + pd.Timedelta(1,unit="day")
    DA_Market = [pd.Timestamp(datetime.datetime(today_date.year,today_date.month,today_date.day,23,0,0),
                            tz="Europe/London"),
                pd.Timestamp(datetime.datetime(tomorrow_date.year,tomorrow_date.month,tomorrow_date.day,22,30,0),
                tz="Europe/London")]

    DA_Market = pd.date_range(start=DA_Market[0], end=DA_Market[1],
                    freq=pd.Timedelta(30,unit="minute"))
    
    return DA_Market


def prep_submission_in_json_format(submission_data):
    submission = []

    # Example of a submission
    for i in range(len(submission_data.index)):
        submission.append({
            'timestamp': submission_data["datetime"][i].isoformat(),
            'market_mid': submission_data["market_bid"][i],
            'probabilistic_forecast': {
                10: submission_data["q10"][i],
                20: submission_data["q20"][i],
                30: submission_data["q30"][i],
                40: submission_data["q40"][i],
                50: submission_data["q50"][i],
                60: submission_data["q60"][i],
                70: submission_data["q70"][i],
                80: submission_data["q80"][i],
                90: submission_data["q90"][i],
            }
        })


    data = {
        'submission': submission
    }
    
    return data

def submit(data,market_day=pd.to_datetime('today') + pd.Timedelta(1,unit="day")):

    url = f"{base_url}/challenges/{challenge_id}/submit"


    # You can only submit a prediction for next day, before 10:20 UK time today
    params = {
        'prediction_date': market_day.strftime('%Y-%m-%d')

    }

    headers = {
        'Authorization': f"Bearer {api_key}"
    }
    resp = session.post(url, params=params, headers=headers, json=data)

    print(resp)

    print(resp.text)

    # Open text file in write mode
    text_file = open(f"logs/sub_{pd.Timestamp('today').strftime('%Y%m%d-%H%M%S')}.txt", "w")
    text_file.write(resp.text)
    text_file.close()