import decimal

from dal import autocomplete
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView, FormMixin
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import Food, Recipe, RecipeFood, RecipePreset
from .models import DailyLog, MealLog, MealFood
from .models import Profile, Allergy, DietPreference

from .forms import AllergyChoiceForm, DietChoiceForm, AllergyDeleteForm, DietDeleteForm
from .forms import LogForm, RecipeForm

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

# Daily log page, saves submitted info to database
class LogView(LoginRequiredMixin, FormView):
    form_class = LogForm
    template_name = 'nutrihacker/log.html'
    daily_log_id = 0 # id of daily log to be redirected to
    
    # override get_success_url to correct daily log
    def get_success_url(self):
        return reverse_lazy('nutrihacker:displayLog', kwargs={'pk':self.daily_log_id})

    # override get_form_kwargs to get number of extra fields
    def get_form_kwargs(self):
        kwargs = super(LogView, self).get_form_kwargs()
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
            daily_log = DailyLog.objects.get(user__id=self.request.user.id, date=date)
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

        return super(LogView, self).form_valid(form)

class DisplayLogView(LoginRequiredMixin, DetailView):
    template_name = 'nutrihacker/displayLog.html'
    model = DailyLog

# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == value.to_integral():
		return value.quantize(decimal.Decimal(1))
	else:
		return value.normalize()

# displays the nutrition information of a food
class FactsView(DetailView):
	model = Food
	template_name = 'nutrihacker/nutrifacts.html'
	
	# overrides DetailView get_context_data
	def get_context_data(self, **kwargs):
		# get context
		context = super().get_context_data(**kwargs)
	
		# if there is a GET request
		if self.request.method == 'GET':
			# get the query value
			query = self.request.GET.get('portions')
			
			# if query empty
			if query == None:
				# set to 1
				query = decimal.Decimal(1)
			else:
				# convert query to python decimal
				query = decimal.Decimal(query)
		# no GET request
		else:
			# set query to 1
			query = decimal.Decimal(1)

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
	model = Food
	template_name = 'nutrihacker/search.html'
	
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
    model = RecipePreset
    template_name = 'nutrihacker/search-recipe.html'

    # overrides ListView get_queryset to find names containing search term and pass them to template
    def get_queryset(self):
        query = self.request.GET.get('term')
        if (query == None):
            return RecipePreset.objects.all()
        else:
            object_list = RecipePreset.objects.filter(
                Q(name__icontains=query)
            )
            return object_list


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'nutrihacker/profile.html', {"user":user})


class ProfileView(ListView):
	model = Profile
	template_name = 'nutrihacker/profile.html'


class UpdateProfile(UpdateView, LoginRequiredMixin):
    model = Profile
    pk_url_kwarg = 'profile_id'
    fields = '__all__'
    success_url= '../../profile/'
    login_url = '../../nutrihacker/login/'
    template_name = 'nutrihacker/update_profile.html'
    
    def get_object(self):
        return get_object_or_404(Profile, id=self.kwargs.get('profile_id'))


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


##-------------- Recipe Views --------------------------------------
class DetailRecipe(DetailView):
    model = Recipe
    fields = '__all__'
    template_name='nutrihacker/recipe/detail_recipe.html'
    
    def get_context_data(self, **kwargs):
        context = super(DetailRecipe, self).get_context_data(**kwargs)
        context['detail_list'] = Recipe.objects.all()
        return context

class ListRecipe(ListView):
    model = Recipe
    context_object_name = 'recipes'
    fields = '__all__'
    template_name='nutrihacker/recipe/list_recipe.html'

class CreateRecipe(CreateView):
    model = Recipe
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipe/create_recipe.html'

class UpdateRecipe(UpdateView):
    model = Recipe
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipe/update_recipe.html'

class DeleteRecipe(DeleteView):
    model = Recipe
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipe/delete_recipe.html'
    
    
    
    # Daily log page, login required
class RecipeView(LoginRequiredMixin, TemplateView):
    template_name = 'nutrihacker/recipe/create_recipe.html'

    # override get_context_data to include form html
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_form'] = RecipeForm()
        return context

# saves submitted info to database
class RecordRecipeView(FormView):
    form_class = RecipeForm
    success_url = reverse_lazy('nutrihacker:profile')
    
    
    #def get_success_url(self):
     #   return reverse_lazy('nutrihacker:displayLog',kwargs={'pk':self.dailylogID})
    
    # override get_form_kwargs to get number of extra fields
    def get_form_kwargs(self):
        kwargs = super(RecordRecipeView, self).get_form_kwargs()
        kwargs['extra'] = kwargs['data']['extra_field_count']
        
        return kwargs

    # override form_valid to create model instances from submitted info
    def form_valid(self, form):
        # get number of foods in form
        food_number = int(form.cleaned_data.get('extra_field_count')) + 1
        
        food = {}
        portions = {}

        # stores data from form into food and portions dicts (ex: 'food1': <Food: Egg>)
        for i in range(1, food_number+1):
            food['food'+str(i)] = form.cleaned_data.get('food'+str(i))
            portions['portions'+str(i)] = form.cleaned_data.get('portions'+str(i))

        
        recipe = Recipe.create(self.request.user)
        recipe.save()

        # creates a meal food for each food for this meal log
        for i in range(1, food_number+1):
            recipe_food = RecipeFood.create(recipe, food['food'+str(i)], portions['portions'+str(i)])
            recipe_food.save()

        return super(RecordRecipeView, self).form_valid(form)


##-------------- RecipeFood Views --------------------------------------
class DetailRecipeFood(DetailView):
    model = RecipeFood
    fields = '__all__'
    template_name='nutrihacker/recipefood/detail_recipefood.html'

class ListRecipeFood(ListView):
    model = RecipeFood
    context_object_name = 'recipefoods'
    fields = '__all__'
    template_name='nutrihacker/recipefood/list_recipefood.html'

class CreateRecipeFood(CreateView):
    model = RecipeFood
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipefood/create_recipefood.html'



class UpdateRecipeFood(UpdateView):
    model = RecipeFood
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipefood/update_recipefood.html'

class DeleteRecipeFood(DeleteView):
    model = RecipeFood
    fields = '__all__'
    success_url= "../"
    template_name = 'nutrihacker/recipefood/delete_recipefood.html'

@login_required
def add_to_recipe(request,food_id):
    food = get_object_or_404(Food, pk=food_id)
    portions = 1 #hard coded for now
    recipe,created = Recipe.objects.get_or_create(user=request.user, active=True)
    recipefood,created = RecipeFood.objects.get_or_create(food=food,recipe=recipe, portions=portions)
    recipe.add_to_recipe(book_id)
    recipefood.save()
    messages.success(request, "Recipe updated!")
    return redirect('recipe')
