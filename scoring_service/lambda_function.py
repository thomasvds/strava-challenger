import json

# TODO: include full user data to feed leaderboard
# TODO: include geodesic distances calculations
# TODO: include 'furthest_distance' to metrics

def aggregated_metrics_per_user(activities):
	aggregated_metrics = {}
	for activity in activities:
		# user_id = activity['user_id']
		user_id = activity['athlete']['id']
		if user_id in aggregated_metrics:
			aggregated_metrics[user_id]['total_distance'] += activity['distance']
			aggregated_metrics[user_id]['total_elevation_gain'] += activity['total_elevation_gain']
			aggregated_metrics[user_id]['total_moving_time'] += activity['moving_time']

			if activity['elev_high'] > aggregated_metrics[user_id]['max_elevation']:
				aggregated_metrics[user_id]['max_elevation'] = activity['elev_high']

			if activity['elev_low'] < aggregated_metrics[user_id]['min_elevation']:
				aggregated_metrics[user_id]['min_elevation'] = activity['elev_low']
			
		else:
			aggregated_metrics[user_id] = {
				'user': user_id, 
				'total_distance': activity['distance'],
				'total_elevation_gain': activity['total_elevation_gain'],
				'total_moving_time': activity['moving_time'],
				'max_elevation': activity['elev_high'],
				'min_elevation': activity['elev_low']
			}
	return [ m for m in aggregated_metrics.values() ]

def metric_leaderboard(aggregated_metrics_per_user, metric):
	if metric == 'min_elevation':
		reversed = False
	else:
		reversed = True
	return sorted(aggregated_metrics_per_user, key=lambda k: k[metric], reverse=reversed) 

activities = json.load(open('sample_activities.json'))
aggregated_metrics = aggregated_metrics_per_user(activities)

print json.dumps(metric_leaderboard(aggregated_metrics, 'min_elevation'))