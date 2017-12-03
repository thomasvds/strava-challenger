import json
from operator import itemgetter


def select_activity_type(activities, activity_type):
  filtered_list = list(filter(lambda d: d['type'] in [activity_type], activities))
  return filtered_list

def max_distance_activity(activities):
  ancestor = max(runs, key=itemgetter('distance'))
  return ancestor

def meters_to_kilometers(distance):
  kilometers = round(distance/1000, 2)
  return kilometers


activities = json.load(open('sample_activities.json'))
runs       = select_activity_type(activities, 'Run')

winning_activity = max_distance_activity(runs)
distance = meters_to_kilometers(winning_activity['distance'])

print( winning_activity ['name'] + ': ' + str(distance) + 'KM' )
