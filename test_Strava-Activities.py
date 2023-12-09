import json
from Strava_Activities import retrieve_access_token, get_activities, format_activity, select_columns, add_gear_info, get_gear_info

with open(".creds") as f:
    creds = json.load(f)

client_id = creds['client_id']
client_secret = creds['client_secret']
refresh_token = creds['refresh_token']

token = retrieve_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
with open("test_activities.json") as f:
    activities = json.load(f)


def get_test_activity() -> list:
    with open("test_activities.json") as f:
        return json.load(f)


def test_format_activity():
    activities = get_test_activity()
    test_activity = activities[0]
    test_activity['distance'] = 10000
    test_activity['total_elevation_gain'] = 100

    formatted_activity = format_activity(test_activity)

    assert formatted_activity['distance_mi'] == round(test_activity['distance'] / 1609.344, 2)
    assert formatted_activity['total_elevation_gain_ft'] == round(test_activity['total_elevation_gain'] * 3.2808399, 0)


def test_select_columns():
    COL_NAMES = ['type', 'name']
    # activities = get_test_activity()

    filtered_activity = select_columns(format_activity(activities[0]), COL_NAMES)
    assert COL_NAMES[0] in filtered_activity.keys()
    for item in COL_NAMES:
        assert item in filtered_activity.keys()


def test_retrieve_access_token():
    # token = retrieve_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
    assert token
    print(token)


def test_get_activities():
    # token = retrieve_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
    assert token
    activities = get_activities(token, activities_number=50)
    assert type(activities) is list
    assert type(activities[0]) is dict


def test_add_gear_info():
    # token = retrieve_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
    # activities = get_test_activity()
    gear_activities = add_gear_info(activities, token)
    # print(json.dumps(gear_activities, indent=2))

    assert gear_activities[0]['gear_name'] == "Nike Invincible Yellow Invincibles"
    assert gear_activities[1]['gear_name'] ==  "Saucony Triumph 20 Runshield Triumph 20 Runshield"


def test_get_gear_info():
    print(token)
    gear_name = get_gear_info(token, activities[0]['gear_id'])
    print(gear_name)

    assert gear_name == "Nike Invincible Yellow Invincibles"
