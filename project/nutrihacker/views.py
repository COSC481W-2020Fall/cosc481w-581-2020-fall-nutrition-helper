from decimal import Decimal
from dal import autocomplete
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect	
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView, FormMixin
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Food, Recipe, RecipeFood
from .models import DailyLog, MealLog, MealFood
from .models import Profile, Allergy, DietPreference

from .forms import AllergyChoiceForm, DietChoiceForm, AllergyDeleteForm, DietDeleteForm
from .forms import LogForm, RecipeForm, UserForm, ProfileForm

class IndexView(TemplateView):
	template_name = 'nutrihacker/index.html'

class DescriptionView(TemplateView):
	template_name = 'nutrihacker/description.html'

# autocomplete search for foods
class FoodAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Food.objects.none()

		qs = Food.objects.all()

		if self.q:
			qs = qs.filter(name__icontains=self.q)

		return qs




# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == 0:
		return Decimal('0')
	elif value == value.to_integral():
		return value.quantize(Decimal(1))
	else:
		return value.normalize()

# displays the nutrition information of a food
class FactsView(DetailView):
	model = Food
	template_name = 'nutrihacker/nutrifacts.html'
	
	# overrides DetailView get_context_data
	def get_context_data(self, **kwargs):
		# get context
		context = super(FactsView, self).get_context_data(**kwargs)
	
		# if there is a GET request
		if self.request.method == 'GET':
			# get the query value
			query = self.request.GET.get('portions')
			
			# if query empty
			if query == None:
				# set to 1
				query = Decimal(1)
			else:
				# convert query to python decimal
				query = Decimal(query)
		# no GET request
		else:
			# set query to 1
			query = Decimal(1)

		# pass query as 'portions'
		context['portions'] = query
		
		# multiply nutrition data fields by query and chop trailing zeros
		context['food'].servingSize = chop_zeros(query * context['food'].servingSize)
		context['food'].calories = chop_zeros(query * context['food'].calories)
		context['food'].totalFat = chop_zeros(query * context['food'].totalFat)
		context['food'].cholesterol = chop_zeros(query * context['food'].cholesterol)
		context['food'].sodium = chop_zeros(query * context['food'].sodium)
		context['food'].totalCarb = chop_zeros(query * context['food'].totalCarb)
		context['food'].protein = chop_zeros(query * context['food'].protein)

		return context

# displays the food that match a search, passed to the template as a list
class SearchFoodView(ListView):
	paginate_by = 50
	model = Food
	template_name = 'nutrihacker/search.html'
	
	def get_context_data(self, **kwargs):
		context = super(SearchFoodView, self).get_context_data(**kwargs)
		if self.request.method == 'GET':
			context['search'] = self.request.GET.get('search')
		return context
	
	# overrides ListView get_queryset to find names containing search term and pass them to template
	def get_queryset(self):
		# check for GET request
		if self.request.method == 'GET':
			query = self.request.GET.get('search')
		else:
			query = None
		
		# no query terms returns an empty list
		if (query == None or query == ''):
			return Food.objects.none()
		else: # If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
			object_list = Food.objects.filter(
				Q(name__icontains = query)
			)
			return object_list
		

class SearchRecipeView(ListView):
    paginate_by = 50
    model = Recipe
    template_name = 'nutrihacker/search-recipe.html'
    
    def get_context_data(self, **kwargs):
        context = super(SearchRecipeView, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['search'] = self.request.GET.get('term')
        return context


    # overrides ListView get_queryset to find names containing search term and pass them to template
    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None
            
        if self.request.method == 'GET':
            query = self.request.GET.get('term')
        else:
            query = None
            
        if (query == None):
            return Recipe.objects.filter(is_public=True)
        else:
            object_list = Recipe.objects.filter(
                Q(name__icontains=query),
                Q(user=user) | Q(is_public=True)
            )
            return object_list


def get_user_profile(request, username):
	user = User.objects.get(username=username)
	return render(request, 'nutrihacker/profile.html', {"user":user})


class ProfileView(ListView):
	model = Profile
	template_name = 'nutrihacker/profile.html'

class UpdateProfile(LoginRequiredMixin, TemplateView):
	template_name = 'nutrihacker/update_profile.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile = get_object_or_404(Profile, user=self.request.user)
		context['user_form'] = UserForm(instance=self.request.user)
		context['profile_form'] = ProfileForm(instance=profile, initial={'height':profile.get_height(), 'weight':profile.get_weight()})
		return context
		
	def post(self, request):
		profile = get_object_or_404(Profile, user=self.request.user)
		user_form = UserForm(request.POST, instance=self.request.user)
		profile_form = ProfileForm(request.POST, instance=profile)
				
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			profile = profile_form.save(commit=False)
			profile.set_height(profile_form.cleaned_data.get('height'))
			profile.set_weight(profile_form.cleaned_data.get('weight'))
			profile.save()
			return HttpResponseRedirect(reverse('nutrihacker:profile'))
		
		context = {'user_form':user_form, 'profile_form':profile_form}
		return self.render_to_response(context)


# Page to add dietary preferences and allergies.
# Login is required to view
class DietAndAllergiesView(LoginRequiredMixin, TemplateView):
	model = Allergy
	template_name = 'nutrihacker/diet_and_allergies.html'
	 
	# passes add/delete allergy/diet preference forms to the template
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile = Profile.objects.get(user=self.request.user)
		context['allergy_choice_form'] = AllergyChoiceForm(current_profile=profile)
		context['diet_choice_form'] = DietChoiceForm(current_profile=profile)
		context['allergy_delete_form'] = AllergyDeleteForm(current_profile=profile)
		context['diet_delete_form'] = DietDeleteForm(current_profile=profile)
		return context

# adds allergy to user from the AllergyChoiceForm form, always redirects back to DietAndAllergiesView		 
def add_allergy(request):
	if request.method == 'POST':
		form = AllergyChoiceForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			allergy = form.cleaned_data.get('allergy_select')
			allergy.profiles.add(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# adds diet preference to user from the DietChoiceForm form, always redirects back to DietAndAllergiesView
def add_diet_preference(request):
	if request.method == 'POST':
		form = DietChoiceForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			diet = form.cleaned_data.get('diet_select')
			diet.profiles.add(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# deletes allergies from user from the AllergyDeleteForm form, always redirects back to DietAndAllergiesView  
def delete_allergy(request):
	if request.method == 'POST':
		form = AllergyDeleteForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			allergy_list = form.cleaned_data.get('allergy_checkbox')
			for allergy in allergy_list:
				allergy.profiles.remove(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# deletes diet preferences from user from the DietDeleteForm form, always redirects back to DietAndAllergiesView  
def delete_diet_preference(request):
	if request.method == 'POST':
		form = DietDeleteForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			diet_list = form.cleaned_data.get('diet_checkbox')
			for diet in diet_list:
				diet.profiles.remove(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))
	

class LoginView(auth_views.LoginView):
	template_name = "nutrihacker/login.html"

class LogoutView(auth_views.LogoutView):
	template_name = "nutrihacker/logout.html"

class PasswordChangeView(auth_views.PasswordChangeView):
	template_name = "nutrihacker/change_password.html"
	success_url = reverse_lazy('nutrihacker:index')
	
class RegisterAccountView(FormView):
	template_name = 'nutrihacker/register_account.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('nutrihacker:index')
	
	# called when valid form data has been POSTed
	# redirects to success_url
	def form_valid(self, form):
		form.save()
		username = form.cleaned_data.get('username')
		raw_password = form.cleaned_data.get('password1')
		user = authenticate(username=username, password=raw_password)
		login(self.request, user)
		return super().form_valid(form)


# ------------------------ Log Views ------------------------

class LogListView(LoginRequiredMixin, ListView):
	template_name = 'nutrihacker/log/log_list.html'
	model = DailyLog

	def get_queryset(self):
		object_list = DailyLog.objects.filter(user=self.request.user).order_by('-date')
		return object_list

# Daily log page, saves submitted info to database
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

	# override form_valid to create model instances from submitted info
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
			food['food'+str(i)] = form.cleaned_data.get('food'+str(i))
			portions['portions'+str(i)] = form.cleaned_data.get('portions'+str(i))

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
			meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
			meal_food.save()

		return super(LogCreateView, self).form_valid(form)

class LogDetailView(LoginRequiredMixin, DetailView):
	template_name = 'nutrihacker/log/log_detail.html'
	model = DailyLog

	def get_context_data(self, **kwargs):
		context = super(LogDetailView, self).get_context_data(**kwargs)
		
		# make sure user has permission by matching the user to the daily log
		try:
			dl = DailyLog.objects.get(user=self.request.user, id=self.kwargs['pk'])
		except DailyLog.DoesNotExist:
			raise PermissionDenied

		# get list of meal logs for this daily log
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

class DailyLogDeleteView(LoginRequiredMixin, DeleteView):
	model = DailyLog
	success_url = reverse_lazy('nutrihacker:log_list')
	
	# override get_object to get id from form
	def get_object(self, queryset=None):
		try:
			dl = DailyLog.objects.get(user=self.request.user, id=self.request.POST.get('id'))
		except DailyLog.DoesNotExist:
			raise PermissionDenied

		return dl

class MealLogDeleteView(LoginRequiredMixin, DeleteView):
	model = MealLog
	daily_log_id = 0 # id of daily log to be redirected to

	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.daily_log_id})

	# override get_object to get id from form
	def get_object(self, queryset=None):
		try:
			ml = MealLog.objects.get(daily_log__user=self.request.user, id=self.request.POST.get('id'))
		except MealLog.DoesNotExist:
			raise PermissionDenied

		self.daily_log_id = ml.daily_log.id

		return ml

class LogUpdateView(LoginRequiredMixin, FormView):
	form_class = LogForm
	template_name = 'nutrihacker/log/log_update.html'
	daily_log_id = 0 # id of daily log to be redirected to
	meal_log_id = 0
	
	# override get_success_url to correct daily log
	def get_success_url(self):
		return reverse_lazy('nutrihacker:log_detail', kwargs={'pk':self.daily_log_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(LogUpdateView, self).get_form_kwargs()

		if 'data' in kwargs:
			kwargs['extra'] = kwargs['data']['extra_field_count']
		else:
			kwargs['extra'] = MealFood.objects.filter(meal_log__id=self.kwargs['pk']).count() - 1
		
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(LogUpdateView, self).get_context_data(**kwargs)
		ml = MealLog.objects.get(id=self.kwargs['pk'])
		dl = ml.daily_log
		
		context['dailylog'] = dl
		context['meallog'] = ml
		
		return context

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

	# override form_valid to create model instances from submitted info
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
			food['food'+str(i)] = form.cleaned_data.get('food'+str(i))
			portions['portions'+str(i)] = form.cleaned_data.get('portions'+str(i))

		try: # searches for an existing daily log for this day and user
			daily_log = DailyLog.objects.get(user=self.request.user, date=date)
		except DailyLog.DoesNotExist: # if there is no matching daily log, a new one is created
			daily_log = DailyLog.create(self.request.user, date)
			daily_log.save()
		
		# update the daily log id to be passed to success url
		self.daily_log_id = daily_log.id
		
		# creates the meal log for this time
		meal_log = MealLog.objects.get(id=self.meal_log_id)

		if meal_log.daily_log is not daily_log:
			meal_log.daily_log = daily_log
			meal_log.save()

		if meal_log.log_time is not time:
			meal_log.log_time = time
			meal_log.save()

		# delete current list of foods
		MealFood.objects.filter(meal_log=meal_log).delete()

		# creates new meal foods for each food for this meal log
		for i in range(1, food_number+1):
			meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
			meal_food.save()

		# checks each food
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

class MealFoodDeleteView(LoginRequiredMixin, DeleteView):
	model = MealFood
	success_url = reverse_lazy('nutrihacker:log_list')

	# override get_object to get id from form
	def get_object(self, queryset=None):
		try:
			mf = MealFood.objects.get(meal_log__daily_log__user=self.request.user, id=self.request.POST.get('id'))
		except MealFood.DoesNotExist:
			raise PermissionDenied

		return mf


##-------------- Recipe Views --------------------------------------
class DetailRecipe(UserPassesTestMixin, DetailView):
	model = Recipe
	fields = '__all__'
	context_object_name = "recipe"
	template_name='nutrihacker/recipe/detail_recipe.html'
	
	# Limit viewing recipe to creator if recipe is not public
	def test_func(self):
		recipe = Recipe.objects.get(id=self.kwargs['pk'])
		return recipe.is_public or recipe.user == self.request.user
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(DetailRecipe, self).get_context_data(**kwargs)
		context['ingredients'] = RecipeFood.objects.filter(recipe=self.kwargs['pk'])
		instance = Recipe.objects.get(id=self.kwargs['pk'])
		nutrition = instance.get_total()
		context['nutrition'] = nutrition
		
		
		# if there is a GET request
		if self.request.method == 'GET':
			# get the query value
			query = self.request.GET.get('portions')
			
			# if query empty
			if query == None:
				# set to 1
				query = Decimal(1)
			else:
				# convert query to python decimal
				query = Decimal(query)
		# no GET request
		else:
			# set query to 1
			query = Decimal(1)

		# pass query as 'portions'
		context['portions'] = query
		
		# multiply nutrition data fields by query and chop trailing zeros
		context['nutrition']['calories'] = chop_zeros(query * context['nutrition']['calories'])
		context['nutrition']['totalFat'] = chop_zeros(query * context['nutrition']['totalFat'])
		context['nutrition']['cholesterol'] = chop_zeros(query * context['nutrition']['cholesterol'])
		context['nutrition']['sodium'] = chop_zeros(query * context['nutrition']['sodium'])
		context['nutrition']['totalCarb'] = chop_zeros(query * context['nutrition']['totalCarb'])
		context['nutrition']['protein'] = chop_zeros(query * context['nutrition']['protein'])
		
		return context

class DetailRecipeFood(DetailView):
	model = RecipeFood
	fields = '__all__'
	context_object_name = "recipe_food"
	template_name='nutrihacker/recipe/detail_recipe_food.html'
	
	def get_queryset(self, *args, **kwargs):
		return RecipeFood.objects.filter(recipe=self.kwargs['pk'])


class ListRecipe(ListView):
	model = Recipe
	#context_object_name = 'recipes'
	fields = '__all__'
	template_name='nutrihacker/recipe/list_recipe.html'
	
	def get_queryset(self):
		object_list = Recipe.objects.filter(user=self.request.user)
		return object_list

class UpdateRecipe(UserPassesTestMixin, UpdateView):
	model = Recipe
	#fields = '__all__'
	fields = ['name', 'instruction', 'servingsProduced']
	success_url= "../"
	template_name = 'nutrihacker/recipe/update_recipe.html'
	
	# Limit updating recipe to creator
	def test_func(self):
		recipe = Recipe.objects.get(id=self.kwargs['pk'])
		return recipe.user == self.request.user

class DeleteRecipe(UserPassesTestMixin, DeleteView):
	model = Recipe
	fields = '__all__'
	success_url= "../../"
	template_name = 'nutrihacker/recipe/delete_recipe.html'
	
	# Limit updating recipe to creator
	def test_func(self):
		recipe = Recipe.objects.get(id=self.kwargs['pk'])
		return recipe.user == self.request.user

# saves submitted info to database
class RecordRecipeView(FormView):
	form_class = RecipeForm
	template_name = 'nutrihacker/recipe/create_recipe.html'
	success_url = reverse_lazy('nutrihacker:list_recipe')
	
	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(RecordRecipeView, self).get_form_kwargs()
		if 'data' in kwargs:
			kwargs['extra'] = kwargs['data']['extra_field_count']
		
		return kwargs

	# override get_context_data to include form html
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['recipe_form'] = RecipeForm()
		return context

	# override form_valid to create model instances from submitted info
	def form_valid(self, form):
		name = form.cleaned_data.get('name')
		servingsProduced = form.cleaned_data.get('servingsProduced')
		instruction = form.cleaned_data.get('instruction')
		name = form.cleaned_data.get('name')
		diet = form.cleaned_data.get('diet')
		allergy = form.cleaned_data.get('allergy')
		is_public = form.cleaned_data.get('is_public')
		# get number of foods in form
		food_number = int(form.cleaned_data.get('extra_field_count')) + 1
		
		food = {}
		portions = {}

		# stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
		for i in range(1, food_number+1):
			food['food'+str(i)] = form.cleaned_data.get('food'+str(i))
			portions['portions'+str(i)] = form.cleaned_data.get('portions'+str(i))

		
		recipe = Recipe.create(self.request.user, name, servingsProduced, instruction, is_public)
		recipe.save()
		recipe.allergy = allergy
		recipe.diet = diet
		recipe.save()

		# creates a recipe food for each food for this recipe
		for i in range(1, food_number+1):
			recipe_food = RecipeFood.create(recipe, food['food'+str(i)], portions['portions'+str(i)])
			recipe_food.save()

		return super(RecordRecipeView, self).form_valid(form)

