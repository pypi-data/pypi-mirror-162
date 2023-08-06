import os
import math
from datetime import timedelta


def execute(pickup_date, distance_in_miles):
	minimum_miles_per_day = int(os.getenv('MINIMUM_MILES_PER_DAY', 300))

	if distance_in_miles:
		if distance_in_miles <= minimum_miles_per_day:
			transit_days = math.floor(distance_in_miles / minimum_miles_per_day)
		else:
			transit_days = math.ceil(distance_in_miles / minimum_miles_per_day)
	else:
		transit_days = 0
	return pickup_date + timedelta(days=transit_days)
