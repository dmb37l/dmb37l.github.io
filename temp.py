import numpy as np
import pandas as pd
import requests, json, csv
from datetime import datetime, timedelta
import time
import re
import psycopg2
import ETL_pipeline_functions

def temp():
    # storing credentials for Strava and Google Geocoding API's
   # strava_access_token = ETL_pipeline_functions.strava_token_exchange('.secret/strava_api_credentials.json')
    #geocode_key = ETL_pipeline_functions.geocode_key_getter('.secret/geocode_api_credentials.json')

    # storing most recent date from request log file
    timestamp = ETL_pipeline_functions.last_timestamp('data/request_log.csv')
    # converting date to unix format
    unix_time = ETL_pipeline_functions.timestamp_to_unix(timestamp)
    print ('UNIX_TIME:', unix_time)
    # making requests to activities endpoint for Strava API
    #activities = ETL_pipeline_functions.processed_activities(strava_access_token, geocode_key, unix_time)
    #activities = ETL_pipeline_functions.processed_activities(strava_access_token, unix_time)
    
    # storing current date
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # logging requests to a csv file
    with open('data/request_log.csv', 'a', newline = '') as a:
        csv_writer = csv.writer(a)
        csv_writer.writerow([date, n])
    
    return print("Temp complete")

temp()