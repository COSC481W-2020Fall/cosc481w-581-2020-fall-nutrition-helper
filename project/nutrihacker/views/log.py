from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from nutrihacker.models import DailyLog, MealLog, MealFood
from nutrihacker.forms import LogForm
from nutrihacker.functions import chop_zeros

# page that lists user's DailyLogs
class LogListView(LoginRequiredMixin, ListView):
	template_name = 'nutrihacker/log/log_list.html'
	model = DailyLog

	# override get_queryset to get only logged in user's DailyLogs
	def get_queryset(self):
		object_list = DailyLog.objects.filter(user=self.request.user).order_by('-date')
		return object_list

# page for creating a log, saves submitted data to database
class LogCreateView(LoginRequiredMixin, FormView):
	form_class = LogForm
	template_name = 'nutrihacker/log/log_create.html'
	daily_log_id = 0 # id of daily log to be redirected to
	
	# override get_success_url to correct daily log
	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.daily_log_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(LogCreateView, self).get_form_kwargs()
		if 'data' in kwargs:
			kwargs['extra'] = kwargs['data']['extra_field_count']
		
		return kwargs

	# override form_valid to create model instances from submitted data
	def form_valid(self, form):
		# get data from the form
		date = form.cleaned_data.get('date')
		time = form.cleaned_data.get('time')
		# get number of foods in form
		food_number = int(form.cleaned_data.get('extra_field_count')) + 1
		
		food = {}
		portions = {}

		# stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
		for i in range(1, food_number+1):
			food_field = 'food'+str(i)
			portions_field = 'portions'+str(i)

			# checks if fields exist
			if form.cleaned_data.get(food_field):
				food[food_field] = form.cleaned_data.get(food_field)
				portions[portions_field] = form.cleaned_data.get(portions_field)

		try: # searches for an existing daily log for this day and user
			daily_log = DailyLog.objects.get(user=self.request.user, date=date)
		except DailyLog.DoesNotExist: # if there is no matching daily log, a new one is created
			daily_log = DailyLog.create(self.request.user, date)
			daily_log.save()
		
		# update the daily log id to be passed to success url
		self.daily_log_id = daily_log.id
		
		# creates the meal log for this time
		meal_log = MealLog.create(time, daily_log)
		meal_log.save()

		# creates a meal food for each food for this meal log
		for i in range(1, food_number+1):
			# checks if fields exist
			if 'food'+str(i) in food:
				meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
				meal_food.save()

		return super(LogCreateView, self).form_valid(form)

# page that displays the details of one day's log
class LogDetailView(LoginRequiredMixin, DetailView):
	template_name = 'nutrihacker/log/log_detail.html'
	model = DailyLog

	def get_context_data(self, **kwargs):
		context = super(LogDetailView, self).get_context_data(**kwargs)
		
		# make sure user has permission by matching the user to the DailyLog
		try:
			dl = DailyLog.objects.get(user=self.request.user, id=self.kwargs['pk'])
		except DailyLog.DoesNotExist:
			raise PermissionDenied

		# get list of MealLogs for this DailyLog
		ml_list = MealLog.objects.filter(daily_log=dl).order_by('log_time')
		
		info_list = []

		# build a dictionary for each meal log
		for ml in ml_list:
			info = {}
			info['id'] = ml.id
			info['time'] = ml.log_time.strftime('%I:%M %p')
			info['food_list'] = []
			info['total'] = ml.get_total()
			
			# get list of meal foods for each meal log
			mf_list = MealFood.objects.filter(meal_log=ml)

			# build a dictionary for each food in each meal log
			for mf in mf_list:
				food = {}
				food['name'] = mf.food.name
				food['portions'] = chop_zeros(mf.portions)
				food['amount'] = chop_zeros(mf.portions * mf.food.servingSize)
				food = {**food, **mf.get_total()}

				info['food_list'].append(food)

			info_list.append(info)
		
		# add to context
		context['info_list'] = info_list
		context['daytotal'] = dl.get_total()
		
		return context

# delete DailyLog
class DailyLogDeleteView(LoginRequiredMixin, DeleteView):
	model = DailyLog
	success_url = reverse_lazy('nutrihacker:log_list')
	
	# override get_object to get id from form
	def get_object(self, queryset=None):
		# make sure user has permission by matching the user to the DailyLog
		try:
			dl = DailyLog.objects.get(user=self.request.user, id=self.request.POST.get('id'))
		except DailyLog.DoesNotExist:
			raise PermissionDenied

		return dl

# delete MealLog
class MealLogDeleteView(LoginRequiredMixin, DeleteView):
	model = MealLog
	daily_log_id = 0 # id of daily log to be redirected to

	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.daily_log_id})

	# override get_object to get id from form
	def get_object(self, queryset=None):
		# make sure user has permission by matching the user to the MealLog
		try:
			ml = MealLog.objects.get(daily_log__user=self.request.user, id=self.request.POST.get('id'))
		except MealLog.DoesNotExist:
			raise PermissionDenied

		self.daily_log_id = ml.daily_log.id

		return ml

# page for user to edit log information, modifies database according to submitted data
class LogUpdateView(LoginRequiredMixin, FormView):
	form_class = LogForm
	template_name = 'nutrihacker/log/log_update.html'
	daily_log_id = 0 # id of DailyLog to be redirected to
	meal_log_id = 0 # id of MealLog
	
	# override get_success_url to correct daily log
	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.daily_log_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(LogUpdateView, self).get_form_kwargs()

		# checks whether form data was submitted
		if 'data' in kwargs: # if submitted, set 'extra' to 'extra_field_count' from form
			kwargs['extra'] = kwargs['data']['extra_field_count']
		else: # if not submitted, 'extra' is the number of MealFoods minus 1
			kwargs['extra'] = MealFood.objects.filter(meal_log__id=self.kwargs['pk']).count() - 1
		
		return kwargs

	# override get_context_data to provide ids of DailyLog and MealLog
	def get_context_data(self, **kwargs):
		context = super(LogUpdateView, self).get_context_data(**kwargs)
		
		ml = MealLog.objects.get(id=self.kwargs['pk'])
		
		context['dailylog_id'] = ml.daily_log.id
		context['meallog_id'] = ml.id
		
		return context

	# override get_initial to provide initial form values
	def get_initial(self):
		initial = super(LogUpdateView, self).get_initial()
		ml = MealLog.objects.get(id=self.kwargs['pk'])
		dl = ml.daily_log

		self.meal_log_id = ml.id
		self.daily_log_id = dl.id

		initial['date'] = dl.date
		initial['time'] = ml.log_time

		mf_list = MealFood.objects.filter(meal_log=ml)
		for i in range(mf_list.count()):
			initial['food'+str(i+1)] = mf_list[i].food
			initial['portions'+str(i+1)] = chop_zeros(mf_list[i].portions)
		
		return initial

	# override form_valid to modify model instances from submitted data
	def form_valid(self, form):
		# get data from the form
		date = form.cleaned_data.get('date')
		time = form.cleaned_data.get('time')
		# get number of foods in form
		food_number = int(form.cleaned_data.get('extra_field_count')) + 1
		
		food = {}
		portions = {}

		# stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
		for i in range(1, food_number+1):
			food_field = 'food'+str(i)
			portions_field = 'portions'+str(i)
			
			# checks if fields exist
			if form.cleaned_data.get(food_field):
				food[food_field] = form.cleaned_data.get(food_field)
				portions[portions_field] = form.cleaned_data.get(portions_field)

		try: # searches for an existing daily log for this day and user
			daily_log = DailyLog.objects.get(user=self.request.user, date=date)
		except DailyLog.DoesNotExist: # if there is no matching daily log, a new one is created
			daily_log = DailyLog.create(self.request.user, date)
			daily_log.save()
		
		# update the daily log id to be passed to success url
		self.daily_log_id = daily_log.id
		
		# gets the meal log for this time
		meal_log = MealLog.objects.get(id=self.meal_log_id)

		# change the daily_log field if different date
		if meal_log.daily_log is not daily_log:
			meal_log.daily_log = daily_log
			meal_log.save()

		# change the log_time field if different time
		if meal_log.log_time is not time:
			meal_log.log_time = time
			meal_log.save()

		# delete current list of foods
		MealFood.objects.filter(meal_log=meal_log).delete()

		# creates new meal foods for each food for this meal log
		for i in range(1, food_number+1):
			# checks if fields exist
			if 'food'+str(i) in food:
				meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
				meal_food.save()

		# checks if each food already exists
		# for i in range(1, food_number+1):
		#	  print('food', i)
		#	  if mf_list:
		#		  for mf in mf_list:
		#			  if mf.food == food['food'+str(i)]:
		#				  print('same')
		#				  if mf.portions is not portions['portions'+str(i)]:
		#					  mf.portions = portions['portions'+str(i)]
		#					  mf.save()
		#				  mf_list = mf_list.exclude(id=mf.id)
		#				  print('removed')
		#				  break
		#			  else:
		#				  print('new')
		#				  meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
		#				  meal_food.save()
		#				  newfood = True
		#				  break
		#	  else:
		#		  print('new')
		#		  meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
		#		  meal_food.save()

		return super(LogUpdateView, self).form_valid(form)