import decimal

from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import Food, Recipe, RecipeFood
from .models import DailyLog, MealLog, MealFood
from .models import Profile, Allergy, DietPreference

from .forms import AllergyChoiceForm, DietChoiceForm, AllergyDeleteForm, DietDeleteForm
from .forms import LogForm, RecipeForm

class IndexView(TemplateView):
	template_name = 'nutrihacker/index.html'

class DescriptionView(TemplateView):
	template_name = 'nutrihacker/description.html'

# Daily log page, login required
class LogView(LoginRequiredMixin, TemplateView):
    template_name = 'nutrihacker/log.html'


    # override get_context_data to include form html
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log_form'] = LogForm()
        return context

# saves submitted info to database
class RecordLogView(FormView):
    form_class = LogForm
    dailylogID = 0
    success_url = reverse_lazy('nutrihacker:displayLog',kwargs={'pk':dailylogID})

    def get_success_url(self):
        return reverse_lazy('nutrihacker:displayLog',kwargs={'pk':self.dailylogID})

    # override get_form_kwargs to get number of extra fields
    def get_form_kwargs(self):
        kwargs = super(RecordLogView, self).get_form_kwargs()
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
        self.dailylogID = daily_log.id
        # creates the meal log for this time
        meal_log = MealLog.create(time, daily_log)
        meal_log.save()

        # creates a meal food for each food for this meal log
        for i in range(1, food_number+1):
            meal_food = MealFood.create(meal_log, food['food'+str(i)], portions['portions'+str(i)])
            meal_food.save()

        return super(RecordLogView, self).form_valid(form)

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
class SearchResultsView(ListView):
	model = Food
	template_name = 'nutrihacker/search.html'
	
	# overrides ListView get_queryset to find names containing search term and pass them to template
	def get_queryset(self):
		query = self.request.GET.get('term')
		# TODO: change the case of no query terms from returning all food items to returning an empty list
		if (query == None):
			return Food.objects.all()
		else: # If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
			object_list = Food.objects.filter(
				Q(name__icontains = query)
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

class AddAllergyView(LoginRequiredMixin, FormView):
    form_class = AllergyChoiceForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
        
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        allergy = form.cleaned_data.get('allergy_select')
        allergy.profiles.add(profile)
        return super(AddAllergyView, self).form_valid(form)
        
class AddDietPreferenceView(LoginRequiredMixin, FormView):
    form_class = DietChoiceForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
    
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        diet = form.cleaned_data.get('diet_select')
        diet.profiles.add(profile)
        return super(AddDietPreferenceView, self).form_valid(form)
        
class DeleteAllergyView(LoginRequiredMixin, FormView):
    form_class = AllergyDeleteForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
        
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        allergy_list = form.cleaned_data.get('allergy_checkbox')
        for allergy in allergy_list:
            allergy.profiles.remove(profile)
        return super(DeleteAllergyView, self).form_valid(form)
        
class DeleteDietPreferenceView(LoginRequiredMixin, FormView):
    form_class = DietDeleteForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
        
    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        diet_list = form.cleaned_data.get('diet_checkbox')
        for diet in diet_list:
            diet.profiles.remove(profile)
        return super(DeleteDietPreferenceView, self).form_valid(form)

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
    
    # override get_form_kwargs to get number of extra fields
    def get_form_kwargs(self):
        kwargs = super(RecordLogView, self).get_form_kwargs()
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
    amount = 1 #hard coded for now
    recipe,created = Recipe.objects.get_or_create(user=request.user, active=True)
    recipefood,created = RecipeFood.objects.get_or_create(food=food,recipe=recipe, amount=amount)
    recipe.add_to_recipe(book_id)
    recipefood.save()
    messages.success(request, "Recipe updated!")
    return redirect('recipe')
