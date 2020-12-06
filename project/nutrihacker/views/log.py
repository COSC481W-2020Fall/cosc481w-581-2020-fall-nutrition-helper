from datetime import datetime

from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from nutrihacker.models import DailyLog, MealLog, MealItem, Profile
from nutrihacker.forms import LogForm
from nutrihacker.functions import chop_zeros

# page that lists user's DailyLogs
class LogListView(LoginRequiredMixin, ListView):
	template_name = 'nutrihacker/log/log_list.html'
	model = DailyLog
	today = datetime.now()
	selected_month = False

	def get_context_data(self, **kwargs):
		context = super(LogListView, self).get_context_data(**kwargs)

		# get the calorie goal from user's profile
		cal_goal = Profile.objects.get(user=self.request.user).caloriegoal
		if not cal_goal:
			cal_goal = 'false' # assign false if no calorie goal

		context['calorie_goal'] = cal_goal
		context['current_month'] = self.today.strftime('%Y-%m')

		if self.selected_month:
			context['selected_month'] = self.selected_month[0] + '-' + self.selected_month[1]
		else:
			context['selected_month'] = context['current_month']

		return context

	# helper function to determind if date passed is valid
	def month_valid(self, value):
		if len(value) != 7:
			return False

		if value[4] != '-':
			return False
		
		try:
			y = int(value[:4])
			if y < 1920:
				return False
		except:
			return False

		try:
			m = int(value[-2:])
			if m > 12 and m < 1:
				return False
		except:
			return False

		return True

	# override get_queryset to get only logged in user's DailyLogs
	def get_queryset(self):
		if self.request.method == 'GET' and self.request.GET.get('month'):
			value = self.request.GET.get('month')

			if self.month_valid(value):
				yr = value[:4]
				mnth = value[-2:]
				self.selected_month = [yr, mnth]
			else:
				yr = self.today.year
				mnth = self.today.month
		else:
			yr = self.today.year
			mnth = self.today.month
		
		object_list = DailyLog.objects.filter(user=self.request.user,
											  date__year=yr,
											  date__month=mnth).order_by('-date')
		return object_list

# page for creating a log, saves submitted data to database
class LogCreateView(LoginRequiredMixin, FormView):
	form_class = LogForm
	template_name = 'nutrihacker/log/log_create.html'
	dailylog_id = 0 # id of daily log to be redirected to
	
	# override get_success_url to correct daily log
	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.dailylog_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(LogCreateView, self).get_form_kwargs()
		if 'data' in kwargs:
			kwargs['f_extra'] = kwargs['data']['extra_food_count']
			kwargs['r_extra'] = kwargs['data']['extra_recipe_count']
		
		return kwargs

	def get_initial(self):
		initial = super(LogCreateView, self).get_initial()

		if self.request.GET.get('date'):
			initial['date'] = self.request.GET.get('date')
		else:
			initial['date'] = datetime.now().date()
			initial['time'] = datetime.now().time().replace(second=0)

		return initial

	# override form_valid to create model instances from submitted data
	def form_valid(self, form):
		# get data from the form
		date = form.cleaned_data.get('date')
		time = form.cleaned_data.get('time')
		# get number of foods in form
		food_number = int(form.cleaned_data.get('extra_food_count')) + 1
		recipe_number = int(form.cleaned_data.get('extra_recipe_count')) + 1
		
		item = {}
		portions = {}

		# stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
		for i in range(1, max(food_number, recipe_number)+1):
			food_field = 'food'+str(i)
			recipe_field = 'recipe'+str(i)
			portions_field = '_portions'+str(i)

			# checks if fields exist
			if form.cleaned_data.get(food_field):
				item[food_field] = form.cleaned_data.get(food_field)
				portions['food'+portions_field] = form.cleaned_data.get('food'+portions_field)
			if form.cleaned_data.get(recipe_field):
				item[recipe_field] = form.cleaned_data.get(recipe_field)
				portions['recipe'+portions_field] = form.cleaned_data.get('recipe'+portions_field)

		try: # searches for an existing daily log for this day and user
			daily_log = DailyLog.objects.get(user=self.request.user, date=date)
		except DailyLog.DoesNotExist: # if there is no matching daily log, a new one is created
			daily_log = DailyLog.create(self.request.user, date)
			daily_log.save()
		
		# update the daily log id to be passed to success url
		self.dailylog_id = daily_log.id
		
		# creates the meal log for this time
		meal_log = MealLog.create(time, daily_log)
		meal_log.save()

		# creates a meal food for each food for this meal log
		for i in range(1, max(food_number, recipe_number)+1):
			# checks if fields exist
			if 'food'+str(i) in item:
				meal_item = MealItem.create(meal_log, item['food'+str(i)], None, portions['food_portions'+str(i)])
				meal_item.save()
			if 'recipe'+str(i) in item:
				meal_item = MealItem.create(meal_log, None, item['recipe'+str(i)], portions['recipe_portions'+str(i)])
				meal_item.save()

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
			info['item_list'] = []
			info['total'] = ml.get_total()
			
			# get list of meal foods for each meal log
			mi_list = MealItem.objects.filter(meal_log=ml)

			# build a dictionary for each food in each meal log
			for mi in mi_list:
				item = {}
				if mi.food:
					item['type'] = 'food'
					item['id'] = mi.food.id
					item['name'] = mi.food.name
				else:
					item['type'] = 'recipe'
					item['id'] = mi.recipe.id
					item['name'] = mi.recipe.name
				
				item['portions'] = chop_zeros(mi.portions)
				item = {**item, **mi.get_total()}

				info['item_list'].append(item)

			info_list.append(info)
		
		# add to context
		context['daytotal'] = dl.get_total()
		context['info_list'] = info_list
		
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
	dailylog_id = 0 # id of daily log to be redirected to

	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.dailylog_id})

	# override get_object to get id from form
	def get_object(self, queryset=None):
		# make sure user has permission by matching the user to the MealLog
		try:
			ml = MealLog.objects.get(daily_log__user=self.request.user, id=self.request.POST.get('id'))
		except MealLog.DoesNotExist:
			raise PermissionDenied

		self.dailylog_id = ml.daily_log.id

		return ml

# page for user to edit log information, modifies database according to submitted data
class LogUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
	form_class = LogForm
	template_name = 'nutrihacker/log/log_update.html'
	dailylog_id = 0 # id of DailyLog to be redirected to
	meallog_id = 0 # id of MealLog

	# override test_func to make sure only user that created log can edit
	def test_func(self):
		self.meallog_id = self.kwargs['pk']
		dl = MealLog.objects.get(id=self.meallog_id).daily_log
		return dl.user == self.request.user
	
	# override get_success_url to correct daily log
	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.dailylog_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(LogUpdateView, self).get_form_kwargs()
		
		# checks whether form data was submitted
		if 'data' in kwargs: # if submitted, set 'f/r_extra' to 'extra_food/recipe_count' from form
			kwargs['f_extra'] = kwargs['data']['extra_food_count']
			kwargs['r_extra'] = kwargs['data']['extra_recipe_count']
		else: # if not submitted, 'f/r_extra' is the number of food/recipe MealItems minus 1
			m_item_list = MealItem.objects.filter(meal_log__id=self.meallog_id)
			# exclude the recipe MealItems
			food_count = m_item_list.exclude(food=None).count()
			# subtract the number of food MealItems from the total
			recipe_count = m_item_list.count() - food_count
			
			kwargs['f_extra'] = food_count - 1
			kwargs['r_extra'] = recipe_count - 1
		
		return kwargs

	# override get_context_data to provide ids of DailyLog and MealLog
	def get_context_data(self, **kwargs):
		context = super(LogUpdateView, self).get_context_data(**kwargs)
		
		ml = MealLog.objects.get(id=self.meallog_id)
		
		context['dailylog_id'] = ml.daily_log.id
		context['meallog_id'] = ml.id
		
		return context

	# override get_initial to provide initial form values
	def get_initial(self):
		initial = super(LogUpdateView, self).get_initial()
		
		ml = MealLog.objects.get(id=self.meallog_id)
		dl = ml.daily_log

		self.dailylog_id = dl.id

		initial['date'] = dl.date
		initial['time'] = ml.log_time

		mi_list = MealItem.objects.filter(meal_log=ml)

		food_count = 1
		recipe_count = 1
		for item in mi_list:
			if item.food:
				initial['food'+str(food_count)] = item.food
				initial['food_portions'+str(food_count)] = chop_zeros(item.portions)
				food_count += 1
			else:
				initial['recipe'+str(recipe_count)] = item.recipe
				initial['recipe_portions'+str(recipe_count)] = chop_zeros(item.portions)
				recipe_count += 1
		
		return initial

	# override form_valid to modify model instances from submitted data
	def form_valid(self, form):
		# get data from the form
		date = form.cleaned_data.get('date')
		time = form.cleaned_data.get('time')
		# get number of foods in form
		food_number = int(form.cleaned_data.get('extra_food_count')) + 1
		recipe_number = int(form.cleaned_data.get('extra_recipe_count')) + 1
		
		item = {}
		portions = {}

		# stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
		for i in range(1, max(food_number, recipe_number)+1):
			food_field = 'food'+str(i)
			recipe_field = 'recipe'+str(i)
			portions_field = '_portions'+str(i)

			# checks if fields exist
			if form.cleaned_data.get(food_field):
				item[food_field] = form.cleaned_data.get(food_field)
				portions['food'+portions_field] = form.cleaned_data.get('food'+portions_field)
			if form.cleaned_data.get(recipe_field):
				item[recipe_field] = form.cleaned_data.get(recipe_field)
				portions['recipe'+portions_field] = form.cleaned_data.get('recipe'+portions_field)

		try: # searches for an existing daily log for this day and user
			daily_log = DailyLog.objects.get(user=self.request.user, date=date)
		except DailyLog.DoesNotExist: # if there is no matching daily log, a new one is created
			daily_log = DailyLog.create(self.request.user, date)
			daily_log.save()
		
		# update the daily log id to be passed to success url
		self.dailylog_id = daily_log.id
		
		# gets the meal log for this time
		meal_log = MealLog.objects.get(id=self.meallog_id)

		# change the daily_log field if different date
		if meal_log.daily_log is not daily_log:
			meal_log.daily_log = daily_log
			meal_log.save()

		# change the log_time field if different time
		if meal_log.log_time is not time:
			meal_log.log_time = time
			meal_log.save()

		# delete current list of foods
		MealItem.objects.filter(meal_log=meal_log).delete()

		# creates new MealItem for each food for this MealLog
		for i in range(1, max(food_number, recipe_number)+1):
			# checks if fields exist
			if 'food'+str(i) in item:
				meal_item = MealItem.create(meal_log, item['food'+str(i)], None, portions['food_portions'+str(i)])
				meal_item.save()
			if 'recipe'+str(i) in item:
				meal_item = MealItem.create(meal_log, None, item['recipe'+str(i)], portions['recipe_portions'+str(i)])
				meal_item.save()

		return super(LogUpdateView, self).form_valid(form)