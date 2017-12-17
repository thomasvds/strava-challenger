import json, urllib, requests, boto3

def lambda_handler(event, context):
  # DynamoDB configuration
  dynamodb         = boto3.resource('dynamodb')
  users_table      = dynamodb.Table('strava_users')
  activities_table = dynamodb.Table('strava_activities')

  # Retrieve all users from the users table
  users = users_table.scan()['Items']

  # Retrieve all activities for each user
  for u in users:
    # The access token is the Strava-generated, retrieved from Auth0, OmniAuth
    # token. The users fetching service is responsible for refreshing the latest
    # values from Auth0 on a regular basis
    access_token = u['access_token']
    url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {
      'Authorization': 'Bearer ' + access_token,
    }

    response = requests.get(url, headers=headers)
    activities = json.loads(response.content)
    
    print('Successfully fetched ' + str(len(activities)) + ' activities')

    for a in activities:
      # Keep only GPS-generated activities, relevant for the scoring
      if 'elev_low' in a:
        if a['manual'] == False:

          activity = {
            'id': a['id'],

            'name' : a['name'],
            'type' : a['type'],
            'manual' : a['manual'],

            'start_date_local' : a['start_date_local'],

            'moving_time' :json.dumps( a['moving_time']),
            'distance' : json.dumps(a['distance']),
            'max_speed' : json.dumps(a['max_speed']),
            'average_speed' : json.dumps(a['average_speed']),

            'elev_high' : json.dumps(a['elev_high']),
            'elev_low' : json.dumps(a['elev_low']),
            'total_elevation_gain' : json.dumps(a['total_elevation_gain']),
            
            'start_latlng' : json.dumps(a['start_latlng']),
            'end_latlng' : json.dumps(a['end_latlng']),
            'start_longitude' : json.dumps(a['start_longitude']),
            'start_latitude' : json.dumps(a['start_latitude']),

            # Dump everything to a string as the activity contains Floats, which
            # DynamoDB doesn't like...
            'raw_content': json.dumps(a),

            'user_id': u['id'],
            'user_details': json.dumps({
              'first_name': u['first_name'],
              'last_name': u['last_name'],
              'email': u['email'],
              'picture': u['picture'],
            }),
          }
          activities_table.put_item(Item=activity)