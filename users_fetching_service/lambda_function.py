import os, json, urllib, requests, boto3
from datetime import datetime

def lambda_handler(event, context):
  # Auth0 configuration - the client id and secrets are stored in the AWS
  # Lambda environment variables using their lowercase representation
  AUDIENCE      = 'https://eightytwentylab.eu.auth0.com/api/v2/'
  DOMAIN        = 'eightytwentylab.eu.auth0.com'
  CLIENT_ID     = os.environ['client_id']
  CLIENT_SECRET = os.environ['client_secret']
  GRANT_TYPE    = 'client_credentials'
  base_url      = 'https://{domain}'.format(domain=DOMAIN)

  # DynamoDB configuration
  dynamodb = boto3.resource('dynamodb')
  table    = dynamodb.Table('strava_users')

  # Get an access token from Auth0
  url     = base_url + '/oauth/token'
  headers = {
    'Content-Type': 'application/json'
  }
  payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'audience': AUDIENCE,
    'grant_type': GRANT_TYPE
  }
  response     = requests.post(url, data=json.dumps(payload), headers=headers)
  oauth        = json.loads(response.content)
  access_token = oauth['access_token']

  # Use the token to retrieve all users
  url     = base_url + '/api/v2/users'
  headers = {
    'Authorization': 'Bearer ' + access_token,
    'Content-Type': 'application/json'
  }

  try:
    response = requests.get(url, headers=headers)
    users = json.loads(response.content)

    # Loop through existing Auth0 users
    for u in users:
      # Only select the Strava logged users
      if u['identities'][0]['connection']=='Strava':
        # Build a simplified representation of the user
        user = {
          # Simplify Auth0's representation of Strava user id, retrieving the
          # real user id provided initially by Strava
          'id': int(u['identities'][0]['user_id'].replace('Strava|', '')),
          'first_name': u['firstname'],
          'last_name': u['lastname'],
          'email': u['email'],
          'picture': u['picture'],
          'access_token': u['identities'][0]['access_token'],
          'updated_at': str(datetime.now())
        }
        # Insert the user in the DynamoDB table. Note that since email has
        # been defined as the primary key, the existing uses only get refreshed
        # which is pretty useful for our purpose
        table.put_item(Item=user)
    print('Succesful users refresh at' + str(datetime.now()))
  except Exception as e:
    print(format(e))
