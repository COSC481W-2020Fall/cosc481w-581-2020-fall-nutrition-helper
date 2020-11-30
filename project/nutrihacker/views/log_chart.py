from datetime import datetime, timedelta, date
from calendar import monthrange

from django.http import JsonResponse

from nutrihacker.models import DailyLog

def fill_nutrients_ids(day_num, user, days, nutrients, ids):
	for i in range(day_num):
		try: # try to get DailyLog for that day belonging to user
			dl = DailyLog.objects.get(user=user, date=days[i])
			nutrients[i] = dl.get_total() # get the nutrient information
			ids[i] = dl.id
		except DailyLog.DoesNotExist: # if no matching DailyLog, assign False
			nutrients[i] = False

def get_past_seven(user, today):
	days = [None] * 7
	labels = [None] * 7
	nutrients = [None] * 7
	ids = [None] * 7

	days[6] = today
	# fill days array with past 7 days
	for i in range(5, -1, -1):
		days[i] = days[i+1] - timedelta(days=1)

	# create labels
	start_idx = today.weekday()
	for i in range(7):
		# get the day of the week from days array for each day, add it to date
		labels[i] = days[i].strftime('%a') + ' ' + str(days[i].month) + '/' + str(days[i].day)

	# fill nutrients and ids array
	fill_nutrients_ids(7, user, days, nutrients, ids)

	data = {
		'labels': labels,
		'nutrients': nutrients,
		'ids': ids
	}

	return JsonResponse(data)

def get_past_thirty(user, today):
	days = [None] * 30
	labels = [None] * 30
	nutrients = [None] * 30
	ids = [None] * 30

	days[29] = today
	# fill days array with past 30 days
	for i in range(28, -1, -1):
		days[i] = days[i+1] - timedelta(days=1)

	# fill labels array
	for i in range(30):
		labels[i] = days[i].day

	# add month label to first in array
	labels[0] = [labels[0], days[0].strftime('%b')]
	# add month label to first day of month
	for i in range(1, 30):
		if labels[i] == 1:
			labels[i] = [labels[i], days[i].strftime('%b')]
	
	# fill nutrients and ids array
	fill_nutrients_ids(30, user, days, nutrients, ids)

	data = {
		'labels': labels,
		'nutrients': nutrients,
		'ids': ids
	}
	
	return JsonResponse(data)

def get_week(user, today):
	days = [None] * 7
	labels = [None] * 7
	nutrients = [None] * 7
	ids = [None] * 7
	
	# determine the first day of the days
	if today.weekday() == 6: # if today is a Sunday
		days[0] = today
	else: # subtract the number of days from today to get Sunday
		days[0] = today - timedelta(days=today.weekday() + 1)

	# fill in the rest of the days
	for i in range(1, 7):
		days[i] = days[i-1] + timedelta(days=1)

	# create labels
	for i in range(7):
		labels[i] = days[i].strftime('%a') + ' ' + str(days[i].month) + '/' + str(days[i].day)

	# fill nutrients and ids array
	fill_nutrients_ids(7, user, days, nutrients, ids)

	data = {
		'labels': labels,
		'nutrients': nutrients,
		'ids': ids
	}

	return JsonResponse(data)

def get_month(user, today):
	month_days = monthrange(today.year, today.month)[1] # get number of days in current month
	
	days = [None] * month_days
	labels = list(range(1, month_days + 1)) # get list of days for month
	nutrients = [None] * month_days
	ids = [None] * month_days

	days[0] = today.replace(day=1) # set first day of month
	# fill in the rest of the days
	for i in range(1, month_days):
		days[i] = days[i-1] + timedelta(days=1)

	# fill nutrients and ids array
	fill_nutrients_ids(month_days, user, days, nutrients, ids)

	data = {
		'labels': labels,
		'nutrients': nutrients,
		'ids': ids,
		'title': today.strftime('%B')
	}
	
	return JsonResponse(data)

def get_year(user, today):
	current_year = today.year

	labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	nutrients = [None] * 12

	# fill nutrients array
	for i in range(12):
		month_days = monthrange(current_year, i+1)[1]
		month_average = {
			'servingSize':0,
			'calories':0,
			'totalFat':0,
			'cholesterol':0,
			'sodium':0,
			'totalCarb':0,
			'protein':0
		}
		
		days_logged = 0
		for j in range(month_days):
			day = date(current_year, i+1, j+1) # create date
			
			try: # try to get DailyLog for that day belonging to user
				dl = DailyLog.objects.get(user=user, date=day)
				daily_total = dl.get_total() # get the nutrient information
				
				# add the daily total to month average
				for key in daily_total:
					month_average[key] += daily_total[key]

				days_logged += 1 # update counter
			except DailyLog.DoesNotExist: # if no matching DailyLog, do nothing
				pass

		if days_logged != 0:
			for key in month_average:
				month_average[key] = month_average[key] / days_logged

			nutrients[i] = month_average
		else:
			nutrients[i] = False

	data = {
		'labels': labels,
		'nutrients': nutrients,
		'title': today.strftime('%Y')
	}

	return JsonResponse(data)

def get_log_data(request):
	user = request.GET.get('user', None)
	timerange = request.GET.get('timerange', None)
	today = datetime.now().date() #.replace(year=2021, month=3, day=1) # for testing
	
	if timerange == 'past7':
		return get_past_seven(user, today)
	if timerange == 'past30':
		return get_past_thirty(user, today)
	if timerange == 'week':
		return get_week(user, today)
	if timerange == 'month':
		return get_month(user, today)
	if timerange == 'year':
		return get_year(user, today)
