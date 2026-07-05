import openmeteo_requests

import argparse
import pandas as pd
import requests_cache
from retry_requests import retry

def process_hourly(response):
    #rain, relative humididty, dew point
    hourly = response.Hourly()
    #hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(0).ValuesAsNumpy()
    #hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
    #hourly_dew_point_2m = hourly.Variables(3).ValuesAsNumpy()
    #hourly_soil_temperature_0_to_7cm = hourly.Variables(4).ValuesAsNumpy()
    #hourly_soil_temperature_7_to_28cm = hourly.Variables(5).ValuesAsNumpy()
    #hourly_soil_moisture_0_to_7cm = hourly.Variables(6).ValuesAsNumpy()
    #hourly_soil_moisture_7_to_28cm = hourly.Variables(7).ValuesAsNumpy()

    #get the longest duration of constant rain
    longest_run = 0
    recent_run = 0
    for rain in hourly_rain:
        if rain > 0:
            recent_run += 1
            longest_run = max(longest_run, recent_run)
        else:
            recent_run = 0

    '''hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m Celsius"] = hourly_temperature_2m
    hourly_data["temperature_2m Fahrenheit"] = hourly_temperature_2m * 9/5 + 32
    hourly_data["rain"] = hourly_rain
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["dew_point_2m"] = hourly_dew_point_2m
    hourly_data["soil_temperature_0_to_7cm Celsius"] = hourly_soil_temperature_0_to_7cm
    hourly_data["soil_temperature_0_to_7cm Fahrenheit"] = hourly_soil_temperature_0_to_7cm * 9/5 + 32
    hourly_data["soil_temperature_7_to_28cm Celsius"] = hourly_soil_temperature_7_to_28cm
    hourly_data["soil_temperature_7_to_28cm Fahrenheit"] = hourly_soil_temperature_7_to_28cm * 9/5 + 32
    hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
    hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm'''

    return longest_run

def process_daily(response):
    daily = response.Daily()
    #daily_precipitation_sum = daily.Variables(0).ValuesAsNumpy()
    #daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    #daily_temperature_2m_max = daily.Variables(2).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
    daily_dew_point_2m_mean = daily.Variables(1).ValuesAsNumpy()

    time_range_temperature_mean = daily_temperature_2m_mean.mean()
    time_range_dew_point_mean = daily_dew_point_2m_mean.mean()

    '''daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["temperature_2m_min Celsius"] = daily_temperature_2m_min
    daily_data["temperature_2m_max Celsius"] = daily_temperature_2m_max
    daily_data["temperature_2m_mean Celsius"] = daily_temperature_2m_mean
    daily_data["temperature_2m_min Fahrenheit"] = daily_temperature_2m_min * 9/5 + 32
    daily_data["temperature_2m_max Fahrenheit"] = daily_temperature_2m_max * 9/5 + 32
    daily_data["temperature_2m_mean Fahrenheit"] = daily_temperature_2m_mean * 9/5 + 32'''

    return time_range_temperature_mean, time_range_dew_point_mean


#grab input args
parser = argparse.ArgumentParser(description="Weather API script")#,
                                 #help="Enter the latitude, longitude, start date, and end date for the weather data you want to retrieve")
#parser.add_argument("latitude", type=float, help="Latitude of the location")
#parser.add_argument("longitude", type=float, help="Longitude of the location")
#parser.add_argument("start_date", type=str, help="Start date in the format YYYY-MM-DD")
#parser.add_argument("end_date", type=str, help="End date in the format YYYY-MM-DD")
parser.add_argument("zip_code", type=str, help="Zip code of the location")
args = parser.parse_args()
#latitude = args.latitude
#longitude = args.longitude
#start_date = args.start_date
#end_date = args.end_date
zip_code = args.zip_code

end_date = pd.to_datetime("today", utc = True)
start_date = end_date - pd.Timedelta(days = 14)
end_date = end_date.strftime("%Y-%m-%d")
start_date = start_date.strftime("%Y-%m-%d")

#get lat and long from zip using zipToLatLon.csv
zip_to_lat_long = pd.read_csv("zipToLatLon.csv", dtype={"postal code": str})
lat_long = zip_to_lat_long[zip_to_lat_long["postal code"] == zip_code][["latitude", "longitude"]].iloc[0]
latitude = lat_long["latitude"]
longitude = lat_long["longitude"]

#open meteo API settup with cache retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

#the order of variable in hourly or daily is important to assign them correctly
url = "https://archive-api.open-meteo.com/v1/archive"
params = {  #2m: value at 2 meters above ground. Rain: total predicipitation of preceding hour, millimieters.
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date,
    "end_date": end_date,
    "daily": [#"precipitation_sum",
              #"temperature_2m_max",
              #"temperature_2m_min",
              "temperature_2m_mean",
              "dew_point_2m_mean"
              ],
    "hourly": [#"temperature_2m",
               "rain"
               #"relative_humidity_2m",
               #"dew_point_2m",
               #"soil_temperature_0_to_7cm",
               #"soil_temperature_7_to_28cm",
               #"soil_moisture_0_to_7cm",
               #"soil_moisture_7_to_28cm"
               ]
}

responses = openmeteo.weather_api(url, params=params)
response = responses[0]
#print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
#print(f"Elevation: {response.Elevation()} m asl")
#print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
longest_rain_duration = process_hourly(response)
#hourly_dataframe = pd.DataFrame(data = hourly_data)
#print("\nHourly data\n", hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
average_temp, average_dew_point = process_daily(response)
#daily_dataframe = pd.DataFrame(data = daily_data)
#print("\nDaily data\n", daily_dataframe)

#print("Average Temperature:\t\t", average_temp)
#print("Average Dew Point:\t\t", average_dew_point)
#print("Longest Rain Duration, Hours:\t", longest_rain_duration)
print(average_temp)
print(average_dew_point)
print(longest_rain_duration)