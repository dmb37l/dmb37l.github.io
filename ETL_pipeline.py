import numpy as np
import pandas as pd
import requests, json, csv
from datetime import datetime, timedelta
import time
import re
import psycopg2
import sys
import os
import ETL_pipeline_functions

def ETL_pipeline(refresh_days=0): #, load='N'):
    try:
        arg = sys.argv[1]
        #load= sys.argv[2]
    except IndexError:
        arg = refresh_days
        #load = 'N'
        pass
    #**********    
    load = 'N' # you'll need to comment this line and add in the load param and uncomment the two references to load in the try except for a full load
    #**********
    
    # storing credentials for Strava and Google Geocoding API's
    strava_access_token = ETL_pipeline_functions.strava_token_exchange('')#('.secret/strava_api_credentials.json')
    #geocode_key = ETL_pipeline_functions.geocode_key_getter('.secret/geocode_api_credentials.json')

    # storing most recent date from request log file
    timestamp = ETL_pipeline_functions.last_timestamp('data/request_log.csv')
    print('TIMESTAMP', timestamp)
    print('date_time', pd.to_datetime(timestamp))
    print ('timedelta', timedelta(days=int(arg)))
    if load == 'N':
        timestamp = str(pd.to_datetime(timestamp)-timedelta(days=int(arg)))
        print('TIMESTAMP', timestamp)
        # converting date to unix format
        unix_time = ETL_pipeline_functions.timestamp_to_unix(timestamp)
        end_time = 2549285743
        print ('UNIX_TIME:', unix_time)
    else:
        end_timestamp = str(pd.to_datetime(timestamp)+timedelta(days=60))
        timestamp = str(pd.to_datetime(timestamp))
        print('TIMESTAMP', timestamp)
        # converting date to unix format
        unix_time = ETL_pipeline_functions.timestamp_to_unix(timestamp)
        end_time = ETL_pipeline_functions.timestamp_to_unix(end_timestamp)
    # making requests to activities endpoint for Strava API
    #activities = ETL_pipeline_functions.processed_activities(strava_access_token, geocode_key, unix_time)
    activities = ETL_pipeline_functions.processed_activities(strava_access_token, unix_time, end_time)

    # storing number of activities
    n = len(activities)

    # checking for activities
    if n:
        # storing ids for activities
        activity_ids = list(map(lambda activity: activity['id'], activities))

        # making requests to laps endpoint for Strava API
#        splits = ETL_pipeline_functions.processed_splits(strava_access_token, activity_ids)

        # making requests to zones endpoint for Strava API
 #       zones = ETL_pipeline_functions.processed_zones(strava_access_token, activity_ids)
        print('IDs' ,activity_ids)
        # making requests to activity_details endpoint for Strava API
        #actdets = ETL_pipeline_functions.processed_actdets(strava_access_token, activity_ids)
        
        # making requests to activity_details endpoint for segment efforts for Strava API
        segeffs = ETL_pipeline_functions.processed_segeffs(strava_access_token, activity_ids)
        
        # creating connection to postgresSQL database
        #db_cred_file = '.secret/db_credentials.json'
        #with open(db_cred_file, 'r') as r:
            #db_credentials = json.load(r)
        database = os.environ['DB_USER'] #db_credentials['database']
        user = os.environ['DB_USER'] #db_credentials['user']
        password = os.environ['DB_PASS'] #db_credentials['password']
         #   r.close()
        #with psycopg2.connect(host="localhost", database=database, user=user, password=password) as conn:
        with psycopg2.connect(host="tyke.db.elephantsql.com", port="5432", database=database, user=user, password=password) as conn:
            # delete all activities back to the start date
            ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.delete_to_start_date("activities", timestamp))
            # insert all records retrieved
            for activity in activities:
                ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.insert_statement("activities", activity))
            
            # delete all segment_efforts back to the start date
            ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.delete_to_start_date("segment_efforts", timestamp))
            # insert all the segment efforts
            for segeff in segeffs:
                ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.insert_statement("segment_efforts", segeff))
            
            #for zone in zones:
             #   ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.insert_statement("activity_zones", zone))

            #for split in splits:
             #   ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.insert_statement("activity_splits", split))

    # exception handling for no activities
    else:
        return print("no activities to append")
    
    # storing current date
    if load == 'N':
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        date = end_timestamp
    print('Date for file: ', date)
    # logging requests to a csv file
    #with open('data/request_log.csv', 'a', newline = '') as a:
    #    csv_writer = csv.writer(a)
    #   csv_writer.writerow([date, n])
    request_log = {}
    request_log['timestamp'] = date
    request_log['activities'] = n
    ETL_pipeline_functions.commit(conn, ETL_pipeline_functions.insert_statement("request_log", request_log))
    
    return print("ETL pipeline complete")

ETL_pipeline()

