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
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
      'Authorization': 'Bearer ' + access_token,
    }
    try:
      response = requests.get(url, headers=headers)
      activities = json.loads(response.content)
      for a in activities:
        activity = {
          'id': a['id'],
          # Dump everything to a string as the activity contains Floats, which
          # DynamoDB doesn't like...
          'raw_content': json.dumps(a)
        }
        activities_table.put_item(Item=activity)
    except Exception as e:
      print(format(e))
