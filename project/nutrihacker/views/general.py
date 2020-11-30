from decimal import Decimal
from dal import autocomplete

from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q
from django.db.models.functions import Length

from nutrihacker.models import Food, Recipe, RecipeFood, Profile
from nutrihacker.functions import chop_zeros
from nutrihacker.forms import FilterRecipeForm

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
			qs = qs.filter(name__icontains=self.q).order_by(Length('name'))

		return qs

# autocomplete search for recipes
class RecipeAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Recipe.objects.none()

		qs = Recipe.objects.filter(Q(user=self.request.user) | Q(is_public=True))

		if self.q:
			qs = qs.filter(name__icontains=self.q).order_by(Length('name'))

		return qs

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
		
	
	# # overrides ListView get_queryset to find names containing search term and pass them to template recipefood_list = RecipeFood.objects.filter(food=food, is_public=True).values('
	# def get_queryset(self):
		# if self.request.user.is_authenticated:
			# user = self.request.user
		# else:
			# user = None
		
		# try:
			# food = Food.objects.get(id=self.kwargs['pk'])
		# except Food.DoesNotExist:
			# raise PermissionDenied
		
		# if (user == None):
			
			# recipe_list = Recipe.objects.filter(Q(recipefood__food=food), Q(is_public=True))
		# else:
			# recipe_list = Recipe.objects.filter(
					# Q(recipefood__food=food),
					# Q(user=user) | Q(is_public=True)
				# )
			
		# object_list = []
		# # build a list of each recipe
		# for recipe in recipe_list:
			# object_list.append(recipe)
		
		# return object_list

# displays the foods that match a search, passed to the template as a paginated list
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
		if query == None or query == '':
			return Food.objects.none()
		else: # If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
			object_list = Food.objects.filter(
				Q(name__icontains = query)
			).order_by(Length('name'))
			return object_list
		
# displays the recipes marked as public that match a search, passed to the template as a paginated list
class SearchRecipeView(ListView):
	paginate_by = 50
	model = Recipe
	template_name = 'nutrihacker/search-recipe.html'
	
	def get_context_data(self, **kwargs):
		context = super(SearchRecipeView, self).get_context_data(**kwargs)
				
		if self.request.method == 'GET':
			context['search'] = self.request.GET.get('term')
			default_filter = self.request.GET.get('filter')
			
			# set search filter form values to profile defaults if searched from the nav bar, otherwise create the form from the request
			if default_filter and self.request.user.is_authenticated:
				profile = Profile.objects.get(user=self.request.user)
				context['filter_form'] = FilterRecipeForm(initial = { 
					'allergy_filter' : profile.allergy_set.all(), 
					'diet_filter' : profile.dietpreference_set.all() 
					} )
			else:	
				context['filter_form'] = FilterRecipeForm(self.request.GET)
		else:
			context['filter_form'] = FilterRecipeForm()

		return context

	# overrides ListView get_queryset to find names containing search term and pass them to template
	def get_queryset(self):
		if self.request.user.is_authenticated:
			user = self.request.user
			profile = Profile.objects.get(user=user)
		else:
			user = None
			profile = None
		
		allergy_filter = None
		diet_filter = None
			
		if self.request.method == 'GET':
			query = self.request.GET.get('term')
			default_filter = self.request.GET.get('filter')
			filter_form = FilterRecipeForm(self.request.GET)
			if filter_form.is_valid():
				allergy_filter = filter_form.cleaned_data.get('allergy_filter')
				diet_filter = filter_form.cleaned_data.get('diet_filter')
		
		# show all recipes if there's no search query
		# (if you really want this to return here make sure you filter allergies and diets)
		if query == None:
			query = ''
		
		# if user searches from nav bar, allergy and diet filters default to their profile
		if (profile and default_filter == 'true'):
			allergy_filter = profile.allergy_set.all()
		if (profile and default_filter == 'true'):
			diet_filter = profile.dietpreference_set.all()
		
		# filter recipes by the search query 
		# only showing recipes that belong to the user or are public
		# order them by the length of the name
		object_list = Recipe.objects.filter(
			Q(name__icontains=query),
			Q(user=user) | Q(is_public=True),
		).order_by(Length('name'))
		
		# don't include recipes with filtered allergies
		if allergy_filter:
			object_list = object_list.exclude(allergies__in=allergy_filter)
		# only include recipes with filtered diets
		if diet_filter:
			object_list = object_list.filter(diets__in=diet_filter).distinct()
			
		return object_list
