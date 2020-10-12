import decimal

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.db.models import Q
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages


from .models import Food
from .models import Profile
from .models import EatReport, Recipe, RecipeFood
from .models import Food, Profile, Allergy, DietPreference
from .forms import AllergyChoiceForm, DietChoiceForm

class IndexView(TemplateView):
	template_name = 'nutrihacker/index.html'

class DescriptionView(TemplateView):
	template_name = 'nutrihacker/description.html'
class FoodIntakeView(TemplateView):
	template_name = 'nutrihacker/Food_intake.html'
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
    
    
class UpdateProfile(UpdateView):
    model = Profile
    fields = ['gender', 'height', 'weight', 'birthdate', 'showmetric'] # Keep listing whatever fields 
    # the combined UserProfile and User exposes.
    slug_field = 'username'
    slug_url_kwarg = 'slug'
    context_object_name = 'profile'
    template_name = 'nutrihacker/profile.html'

# Page to add dietary preferences and allergies.
# Login is required to view    
class DietAndAllergiesView(LoginRequiredMixin, ListView):
    model = Allergy
    template_name = 'nutrihacker/diet_and_allergies.html'
    context_object_name = 'user_allergy_list'
    
    # gets allergies of current user, passed to the template
    def get_queryset(self):
        user = self.request.user
        return user.allergy_set.all()
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_preference_list'] = user.dietpreference_set.all()
        context['allergy_choice_form'] = AllergyChoiceForm()
        context['diet_choice_form'] = DietChoiceForm()
        return context

class AddAllergyView(FormView):
    form_class = AllergyChoiceForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
        
    def form_valid(self, form):
        allergy = form.cleaned_data.get('allergy_select')
        allergy.users.add(self.request.user)
        return super(AddAllergyView, self).form_valid(form)
        
class AddDietPreferenceView(FormView):
    form_class = DietChoiceForm
    success_url = reverse_lazy('nutrihacker:diet_and_allergies')
        
    def form_valid(self, form):
        diet = form.cleaned_data.get('diet_select')
        diet.users.add(self.request.user)
        return super(AddDietPreferenceView, self).form_valid(form)

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

class ListRecipe(ListView):
    model = Recipe
    context_object_name = 'recipes'
    fields = '__all__'
    template_name='nutrihacker/recipe/list_recipe.html'

class CreateRecipe(CreateView):
    model = Recipe
    fields = '__all__'
    template_name = 'nutrihacker/recipe/create_recipe.html'

class UpdateRecipe(UpdateView):
    model = Recipe
    fields = '__all__'
    template_name = 'nutrihacker/recipe/update_recipe.html'

class DeleteRecipe(DeleteView):
    model = Recipe
    fields = '__all__'
    template_name = 'nutrihacker/recipe/delete_recipe.html'


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
    template_name = 'nutrihacker/recipefood/create_recipefood.html'



class UpdateRecipeFood(UpdateView):
    model = RecipeFood
    fields = '__all__'
    template_name = 'nutrihacker/recipefood/update_recipefood.html'

class DeleteRecipeFood(DeleteView):
    model = RecipeFood
    fields = '__all__'
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
