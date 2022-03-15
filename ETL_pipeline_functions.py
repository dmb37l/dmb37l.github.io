# importing libaries

import numpy as np
import pandas as pd
import requests, json, csv
from datetime import datetime, timedelta
import time
import re
import psycopg2
import os

# timestamp functions

def last_timestamp(activities_file):

    with open(activities_file, 'r') as f:
        lines = f.read().splitlines()
        first_line = lines[0].split(',')
        last_line = lines[-1].split(',')
        last_line_dict = dict(list(zip(first_line, last_line)))
        last_timestamp = last_line_dict['timestamp']
        f.close()

    return last_timestamp

def sql_timestamp_formatter(timestamp_iso_string):

    timestamp_datetime = datetime.strptime(timestamp_iso_string, "%Y-%m-%dT%H:%M:%SZ")
    timestamp_sql = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_sql

def timestamp_to_unix(timestamp_string):

    timestamp_datetime = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
    datetime_tuple = timestamp_datetime.timetuple()
    unix_timestamp = int(time.mktime(datetime_tuple))

    return unix_timestamp

# API credentials functions

def strava_token_exchange(credentials_file):
    
    strava_keys = "select client_id, client_secret, access_token, refresh_token from strava_api_credentials"
    db_database = os.environ['DB_USER'] #db_credentials['database']
    db_user = os.environ['DB_USER'] #db_credentials['user']
    db_password = os.environ['DB_PASS'] #db_credentials['password']
    print('DB: ' ,db_database)
    print('Pass: ' ,db_password)
    with psycopg2.connect(host="tyke.db.elephantsql.com", port="5432", database="ugdkavve", "user=ugdkavve", password=db_password) as conn:
        cur = conn.cursor()
        cur.execute(strava_keys)
        api_credentials = cur.fetchone()  
        client_id = api_credentials[0]
        client_secret = api_credentials[1]
        refresh_token = api_credentials[3]
        cur.close()
        #req = requests.post("https://www.strava.com/oauth/token?client_id=58267&grant_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read").json()
        req = requests.post("https://www.strava.com/oauth/token?client_id={}&client_secret={}&refresh_token={}&grant_type=refresh_token".format(client_id, client_secret, refresh_token)).json()
        # api_credentials['access_token'] = req['access_token']
        # api_credentials['refresh_token'] = req['refresh_token']
        commit(conn, update_strava_key("strava_api_credentials", req['access_token'])) 
        
        #access_token = req['access_token']

    return req['access_token']

def geocode_key_getter(credentials_file):

    with open(credentials_file, 'r') as r:
        key = json.load(r)['key']
        r.close() 

    return key

# Strava activities endpoint functions

def request_activities(strava_access_token, start_date = False, end_date = False, page = 1):
    
    print ('Access token: ', strava_access_token, 'Start_Date: ', start_date)
    
    url = "https://www.strava.com/api/v3/" + "athlete/activities"# + "?after=" + str(start_date)
    headers = {"Authorization": "Bearer {}".format(strava_access_token)}
    #headers = {"Authorization: Bearer {}".format(strava_access_token)}
    params = {}
    
    print ('Headers: ', headers)
    
    #params['access_token'] = strava_access_token
    
    if start_date:
        params['after'] = start_date
    
    if end_date:
        params['before'] = end_date
    
    params['page'] = page
    params['per_page'] = 200
    
    print ('Params: ', params)
    
    response = requests.get(url, headers = headers, params = params).json()
    #response = requests.get(url, headers = headers).json()
    
    #print ('Response: ', response)

    return response

def clean_activity(activity):

    clean_activity = {}
    clean_activity['id'] = activity['id']
    clean_activity['name'] = activity['name'].replace("'", "*")
    clean_activity['distance'] = activity['distance']
    clean_activity['moving_time'] = activity['moving_time']
    clean_activity['elapsed_time'] = activity['elapsed_time']
    clean_activity['total_elevation_gain'] = activity.get('total_elevation_gain', 0)
    clean_activity['type'] = activity['type']
    clean_activity['start_date_local'] = sql_timestamp_formatter(activity['start_date_local'])
    clean_activity['timezone'] = activity['timezone']
    clean_activity['location_country'] = activity['location_country']
    clean_activity['start_latitude'] = activity.get('start_latitude', 0)
    clean_activity['start_longitude'] = activity.get('start_longitude', 0)
    clean_activity['achievement_count'] = activity.get('achievement_count', 0)
    clean_activity['trainer'] = activity['trainer']
    clean_activity['commute'] = activity['commute']
    clean_activity['manual'] = activity['manual']
    clean_activity['private'] = activity['private']
    clean_activity['visibility'] = activity['visibility']
    clean_activity['gear_id'] = activity['gear_id']
    clean_activity['upload_id_str'] = activity.get('upload_id_str', 0)
    clean_activity['average_speed'] = activity.get('average_speed', 0)
    clean_activity['max_speed'] = activity.get('max_speed', 0)
    clean_activity['average_cadence'] = activity.get('average_cadence', 0)
    clean_activity['average_temp'] = activity.get('average_temp', 0)
    clean_activity['average_watts'] = activity.get('average_watts', 0)
    clean_activity['weighted_average_watts'] = activity.get('weighted_average_watts', 0)
    clean_activity['kilojoules'] = activity.get('kilojoules', 0)
    clean_activity['device_watts'] = activity.get('device_watts', 0)
    clean_activity['has_heartrate'] = activity['has_heartrate']
    clean_activity['average_heartrate'] = activity.get('average_heartrate', 0)
    clean_activity['max_heartrate'] = activity.get('max_heartrate', 0)
    clean_activity['heartrate_opt_out'] = activity['heartrate_opt_out']
    clean_activity['max_watts'] = activity.get('max_watts', 0)
    clean_activity['elev_high'] = activity.get('elev_high', 0)
    clean_activity['elev_low'] = activity.get('elev_low', 0)
    clean_activity['pr_count'] = activity.get('pr_count', 0)
    clean_activity['has_kudoed'] = activity['has_kudoed']
    #clean_activity['suffer_score'] = activity['suffer_score']

    
    if activity.get('suffer_score', None):
        clean_activity['suffer_score'] = activity['suffer_score']
    else:
        clean_activity['suffer_score'] = 0
    
    if activity.get('start_latitude', None):
        clean_activity['start_latitude'] = activity['start_latitude']
    else:
        clean_activity['start_latitude'] = 0
        
    if activity.get('start_longitude', None):
        clean_activity['start_longitude'] = activity['start_longitude']
    else:
        clean_activity['start_longitude'] = 0        
        
    if activity.get('gear_id', None):
        clean_activity['gear_id'] = activity['gear_id']
    else:
        clean_activity['gear_id'] = 0

    if activity.get('location_country', None):
        clean_activity['location_country'] = activity['location_country']
    else:
        clean_activity['location_country'] = 0  
    
    return clean_activity

def request_location(geocode_key, latlng):

    url = "https://maps.googleapis.com/maps/api/" + "geocode/json"
    response = requests.get("{}?latlng={},{}&key={}".format(url, latlng[0], latlng[1], geocode_key)).json()
    
    return response

def clean_location(location):

    address_components_nested = location['results'][0]['address_components']
    component_names = list(map(lambda x: x['short_name'], address_components_nested))
    component_types = list(map(lambda x: x['types'][0], address_components_nested))
    address_components = dict(list(zip(component_types, component_names))) 
    clean_location = address_components.get('postal_town', 'missing')

    return clean_location

def get_run_type(activity):

    key_words_int = ['Intervals', 'Yasso', 'Track']
    key_words_wu = ['WU', 'test']

    for key_word in key_words_int:
        if key_word in activity['activity_name']:
            return 'I'
    for key_word in key_words_wu:
        if key_word in activity['activity_name']:
            return 'WU'
    if 'WD' in activity['activity_name']:
            return 'WD'

    elif activity['distance'] < 8:
        return 'S'
    elif activity['distance'] < 16:
        return 'M'
    else:
        return 'L'  

def get_position(activity):

    pos_pattern = re.compile('.*\(\d?:?\d{2}:\d{2}\s-\s(\d+)\w+\)')
    pos_pattern_match = re.findall(pos_pattern, activity['activity_name'])

    if pos_pattern_match:
        return int(pos_pattern_match[0])
    else:
        return 0

def get_event_type(activity):

    if ('PR' in activity['activity_name']) & (activity['run_type'] == 'S') :
        return 'PR'
    elif activity['position'] > 0:
        return 'R'
    else:
        return 'W'

def HHMMSS_to_seconds(time_HHMMSS):

    time_tuple = [0] * 3
    time_tuple_raw = [int(x) for x in time_HHMMSS.split(':')]
    time_tuple[-len(time_tuple_raw):] = time_tuple_raw
    time_seconds = (time_tuple[0] * 3600) + (time_tuple[1] * 60) + time_tuple[2]

    return time_seconds

def get_chip_time(activity):

    time_pattern = re.compile('.*\((\d?:?\d{2}:\d{2})\s-\s\d+\w+\)')
    time_pattern_match = re.findall(time_pattern, activity['activity_name'])

    if time_pattern_match:
        return HHMMSS_to_seconds(time_pattern_match[0])
    else:
        return activity['time']

def engineer_activity(activity):

    engineered_activity = activity.copy()

    engineered_activity['location'] = 'missing'
    ## binning activities based on distances
    engineered_activity['run_type'] = get_run_type(engineered_activity)
    ## extracting race positions from activity names
    engineered_activity['position'] = get_position(engineered_activity)
    ## extracting event types from activity names
    engineered_activity['event_type'] = get_event_type(engineered_activity)
    ## extracting race chip times from activity names
    engineered_activity['chip_time'] = get_chip_time(engineered_activity)

    # dropping redundant features
    engineered_activity.pop('latlng', None)
    engineered_activity.pop('activity_name', None)
    
    return engineered_activity

def processed_activities(strava_access_token, start_date = False, end_date = False):

    processed_activities = []
    for page in range (1,100):
        activities_response = request_activities(strava_access_token, start_date, end_date, page)
        if not activities_response:
            break
            
        if activities_response:
            clean_activities = [clean_activity(activity) for activity in activities_response]
            #engineered_activities = [engineer_activity(activity) for activity in clean_activities]

            for activity in clean_activities: #engineered_activities:
               # if activity['type'] == 'Ride':
                activity.pop('activity_type', None)
                processed_activities.append(activity)
                #else:
                #    continue
        #for activity in activities_response:
         #   processed_activities.append(activity)
            
    return processed_activities
    
# Strava segeffs endpoint functions

def request_segeffs(strava_access_token, activity_id):

    base_url = "https://www.strava.com/api/v3"
    end_point = "activities/{}&include_all_efforts=true".format(activity_id)
    url = base_url + "/" + end_point
    headers = {"Authorization": "Bearer {}".format(strava_access_token)}

    response = requests.get(url, headers = headers).json()
    
    #print ('Response: ', response)
    
    return response

def clean_segeffs(segeffs, activity_id):
    
    cleaned_segeffs = []
    
    for seg_eff in segeffs.get('segment_efforts'):
        cleaned_segeff = {}
        cleaned_segeff['effort_id'] = seg_eff['id']
        cleaned_segeff['segment_id'] = seg_eff['segment']['id']
        cleaned_segeff['segment_name'] = seg_eff['name'].replace("'", "*")
        cleaned_segeff['activity_id'] = seg_eff['activity']['id']
        cleaned_segeff['athlete_id'] = seg_eff['athlete']['id']
        cleaned_segeff['distance'] = seg_eff['distance']
        cleaned_segeff['moving_time'] = seg_eff['moving_time']
        cleaned_segeff['elapsed_time'] = seg_eff['elapsed_time']       
        cleaned_segeff['start_date_local'] = sql_timestamp_formatter(seg_eff['start_date_local'])
        cleaned_segeff['start_index'] = seg_eff['start_index']
        cleaned_segeff['end_index'] = seg_eff['end_index']
        cleaned_segeff['average_cadence'] = seg_eff.get('average_cadence', 0)
        cleaned_segeff['average_watts'] = seg_eff.get('average_watts', 0)
        cleaned_segeff['device_watts'] = seg_eff.get('device_watts', 0)
        cleaned_segeff['average_heartrate'] = seg_eff.get('average_heartrate', 0)
        cleaned_segeff['max_heartrate'] = seg_eff.get('max_heartrate', 0)
        cleaned_segeff['average_grade'] = seg_eff['segment']['average_grade']
        cleaned_segeff['maximum_grade'] = seg_eff['segment']['maximum_grade']
        cleaned_segeff['elevation_high'] = seg_eff['segment']['elevation_high']
        cleaned_segeff['elevation_low'] = seg_eff['segment']['elevation_low']
        cleaned_segeff['climb_category'] = seg_eff['segment']['climb_category']
        cleaned_segeff['city'] = seg_eff['segment']['city']
        cleaned_segeff['state'] = seg_eff['segment']['state']
        cleaned_segeff['country'] = seg_eff['segment']['country']

        if cleaned_segeff.get('segment''country', None):
            cleaned_segeff['country'] = seg_eff['country']
        else:
            cleaned_segeff['country'] = 0
        if cleaned_segeff.get('segment''state', None):
            cleaned_segeff['state'] = seg_eff['state']
        else:
            cleaned_segeff['state'] = 0   
        if cleaned_segeff.get('segment''city', None):
            cleaned_segeff['city'] = seg_eff['city']
        else:
            cleaned_segeff['city'] = 0            
        
        cleaned_segeffs.append(cleaned_segeff)
        #print('Eff_id: ' , cleaned_segeff['effort_id'], 'SEG_NAME: ', cleaned_segeff['segment_name'], 'Activity_Id:', cleaned_segeff['activity_id'])
    
    return cleaned_segeffs


def processed_segeffs(strava_access_token, activity_ids):

    processed_segeffs = []
    for activity_id in activity_ids:
        segeffs_response = request_segeffs(strava_access_token, activity_id)
        cleaned_segeffs = clean_segeffs(segeffs_response, activity_id)
        processed_segeffs += cleaned_segeffs
        #print ('Segeffs:', cleaned_segeffs)
    
    return processed_segeffs

# Strava actdets endpoint functions

def request_actdets(strava_access_token, activity_id):

    base_url = "https://www.strava.com/api/v3"
    end_point = "activities/{}&include_all_efforts=true".format(activity_id)
    url = base_url + "/" + end_point
    headers = {"Authorization": "Bearer {}".format(strava_access_token)}

    response = requests.get(url, headers = headers).json()
    
    #print ('Response: ', response)
    
    return response

def clean_actdets(actdets, activity_id):
    
    cleaned_actdets = []
    for actdet in actdets:
        cleaned_actdet = {}
        cleaned_actdet['activity_id'] = activity_id
        cleaned_actdet['actdet_name'] = actdets['name']
        cleaned_actdet['distance'] = actdets['distance'] / 1000
        cleaned_actdet['time'] = actdets['elapsed_time']
        cleaned_actdet['elevation_gain'] = actdets.get('total_elevation_gain', 0)
        cleaned_actdet['average_speed'] = actdets.get('average_speed', 0) * 3.6
        cleaned_actdet['max_speed'] = actdets.get('max_speed', 0) * 3.6
        cleaned_actdet['average_hr'] = actdets.get('average_heartrate', 0)
        cleaned_actdet['max_hr'] = actdets.get('max_heartrate', 0)
        cleaned_actdet['average_cadence'] = actdets.get('average_cadence', 0) 
        cleaned_actdets.append(cleaned_actdet)
        
        #print ('Cleaned_actdets: ', cleaned_actdets)
       
    return cleaned_actdets

def processed_actdets(strava_access_token, activity_ids):

    processed_actdets = []

    for activity_id in activity_ids:
        actdets_response = request_actdets(strava_access_token, activity_id)
        cleaned_actdets = clean_actdets(strava_access_token, actdets_response, activity_id)
        processed_actdets += cleaned_actdets
    
   # print ('Actdets ', processed_actdets)
    
    return processed_actdets
   
# Strava zones endpoint functions

def request_zones(strava_access_token, activity_id):

    base_url = "https://www.strava.com/api/v3"
    end_point = "activities/{}/zones".format(activity_id)
    url = base_url + "/" + end_point
    headers = {"Authorization": "Bearer {}".format(strava_access_token)}

    response = requests.get(url, headers = headers).json()

    return response

def clean_zones(activity_zones, activity_id):

    distribution_types = list(map(lambda x: x['type'], activity_zones))
    distribution_buckets_nested = list(map(lambda x: x['distribution_buckets'], activity_zones))
    distribution_buckets = [list(map(lambda y: y['time'], x)) for x in distribution_buckets_nested]
    distributions = list(zip(distribution_types, distribution_buckets))

    cleaned_zones = []

    for distribution in distributions:
        for i in range(len(distribution[1])):
            cleaned_zone = {}
            cleaned_zone['activity_id'] = activity_id
            cleaned_zone['zone_type'] =  distribution[0]
            cleaned_zone['zone_index'] = i + 1
            cleaned_zone['time'] = distribution[1][i]
            cleaned_zones.append(cleaned_zone)

    return cleaned_zones

def processed_zones(strava_access_token, activity_ids):

    processed_zones = []

    for activity_id in activity_ids:
        zones_response = request_zones(strava_access_token, activity_id)
        cleaned_zones = clean_zones(zones_response, activity_id)
        processed_zones += cleaned_zones
    
    return processed_zones

# appending requests to csv file

def append_requests(requests, file_name):

    with open(file_name, 'r') as r:
        lines = r.read().splitlines()
        headers = lines[0].split(',')
        r.close()

    with open(file_name, 'a', newline = '') as a:
        csv_writer = csv.DictWriter(a, fieldnames = headers)
        csv_writer.writerows(requests)
        a.close()

    return print("{} appended".format(file_name))

# executing sql statements

def commit(conn, sql_statement):
    cur = conn.cursor()
    cur.execute(sql_statement)
    conn.commit()
    cur.close()
    return print("statement committed")

def fetch(conn, sql_statement):
    cur = conn.cursor()
    cur.execute(sql_statement)
    output = cur.fetchall()
    cur.close()
    return output

def insert_statement(table_name, record):
    columns = ', '.join(list(record.keys()))
    values = str(tuple(record.values()))
    statement = """INSERT INTO {} ({}) VALUES {};""".format(table_name, columns, values)
    return statement
    
def delete_to_start_date(table_name, start_time):
    #columns = ', '.join(list(record.keys()))
    #values = str(tuple(record.values()))
    statement = """DELETE FROM {} WHERE start_date_local >  to_timestamp('{}','YYYY-MM-DD HH24:MI:SS');""".format(table_name, start_time)
    return statement

def update_strava_key(table_name, access_token):
    #columns = ', '.join(list(record.keys()))
    #values = str(tuple(record.values()))
    statement = """UPDATE {} set access_token = '{}';""".format(table_name, access_token)
    return statement