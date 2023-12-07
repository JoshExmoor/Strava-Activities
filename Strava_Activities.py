from email.policy import default
from pydoc import cli
import requests
import urllib3
import pandas as pd
import json
import datetime
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AUTH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
COL_NAMES = ['start_date_local', 'type', 'name', 'distance_mi', 'total_time', 'avg_pace', 'total_elevation_gain_ft', 'calories', 'average_heartrate', 'max_heartrate', 'URL']
METERS_TO_MILES = 1/1609.344
METERS_TO_FEET = 0.3048


def filter_activity(activity: dict):
    return {key: activity[key] for key in COL_NAMES}


def format_activity(activity: dict) -> dict:
    formatted_activity = activity
    formatted_activity["distance_mi"] = round(activity["distance"] * METERS_TO_MILES, 2)
    formatted_activity["total_elevation_gain_ft"] = round(activity["total_elevation_gain"] / METERS_TO_FEET, 0)
    formatted_activity["total_time"] = str(datetime.timedelta(seconds=activity["elapsed_time"]))
    formatted_activity["start_date_local"] = activity["start_date_local"].split("T")[0]
    formatted_activity["URL"] = "https://www.strava.com/activities/" + str(activity["id"])
    if activity["average_speed"]:
        formatted_activity["avg_pace"] = str(datetime.timedelta(seconds=((26.8224 / activity["average_speed"]) * 60)))

    return formatted_activity


def select_columns(item: dict, column_list: list) -> dict:
    new_dict = {}
    for column in column_list:
        try:
            new_dict[column] = item[column]
        except KeyError:
            new_dict[column] = None
    return new_dict


def retrieve_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    # You need to update this information from your Strava account before you can run the rest of this code
    # See tutorial video here for info on how: https://www.youtube.com/watch?v=sgscChKfGyg&list=PLO6KswO64zVvcRyk0G0MAzh5oKMLb6rTW

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }

    print("Requesting Token...\n")
    res = requests.post(AUTH_URL, data=payload, verify=False)
    access_token = res.json()['access_token']
    print("Access Token = {}\n".format(access_token))
    return access_token


def get_activities(access_token: str, output_csv: str, per_page: int = 200, activity_type: str = "Run", activities_number=100000):

    # Now we need to import a list of activities and some top level stats about them.
    # This will be 1 row per activity.

    # Initialize the dataframe
    #activities = pd.DataFrame(columns=col_names)
    activities = []

    header = {'Authorization': 'Bearer ' + access_token}

    page = 1

    while True:

        # get page of activities from Strava
        param = {'per_page': per_page, 'page': page}
        print(f"Retrieving Page {page}, found {len(activities)} activities")
        results = requests.get(ACTIVITIES_URL, headers=header, params=param).json()

        # if no results then exit loop
        if (not results):
            break

        activities += results

        # increment page
        page += 1


    #print(json.dumps(format_activity(activities[0]), indent=2))
    #print(json.dumps(select_columns(format_activity(activities[0]), col_names), indent=2))

    with open('raw_activities.json', 'w') as f:
        json.dump(activities, f, indent=2)

    output_activities = []

    for activity in activities:
        if activity["type"] != activity_type:
            continue
        #print(f"Activity: {activity['id']}")
        #print(json.dumps(activity, indent=2))
        formatted_activity = format_activity(activity)
        filtered_activity = select_columns(formatted_activity, COL_NAMES)
        output_activities.append(filtered_activity)

    #print(json.dumps(output_activities, indent=2))

    df = pd.DataFrame.from_dict(output_activities)
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Retrieve Strava Activities.')
    parser.add_argument('output_filename')
    parser.add_argument('-i', "--client_id", required=True )
    parser.add_argument("-c", "--client_secret", required=True)
    parser.add_argument("-r", "--refresh_token", required=True)
    parser.add_argument("-a", "--activities_number", required=False, default=100000)
    args = parser.parse_args()

    print(args)

    output_filename = args.output_filename
    client_id = args.client_id
    client_secret = args.client_secret
    refresh_token = args.refresh_token

    access_token = retrieve_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
    get_activities(access_token=access_token, output_csv=output_filename)