from decimal import Decimal
from dal import autocomplete

from django.views.generic import TemplateView, ListView, DetailView

from django.db.models import Q, F, Count, Sum, ExpressionWrapper, IntegerField
from django.db.models.functions import Length, Lower

from nutrihacker.models import Food, Recipe, RecipeFood, Profile, DietPreference
from nutrihacker.functions import chop_zeros
from nutrihacker.forms import FilterRecipeForm, FilterFoodForm

class IndexView(TemplateView):
	template_name = 'nutrihacker/index.html'

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
		
		
		if self.request.user.is_authenticated:
			user = self.request.user
			profile = Profile.objects.get(user=user)
		else:
			user = None
			profile = None
		
		
		object_list = Recipe.objects.filter(Q(user=user) | Q(is_public = True))
		# stuff for the recipe list
		recipe_food_list = RecipeFood.objects.filter(food=self.kwargs['pk'])
		recipe_ids = recipe_food_list.distinct().values_list('recipe')
		object_list = object_list.filter(pk__in=recipe_ids)
		
		
		portions_list = RecipeFood.objects.none()
		for recipe in object_list:
		
			portions_list = portions_list | RecipeFood.objects.filter(food=self.kwargs['pk'], recipe=recipe)
		
		context['portions_list'] = portions_list
		
		context['object_list'] = object_list
		
		

		return context
		
	

# displays the foods that match a search, passed to the template as a paginated list
class SearchFoodView(ListView):
	paginate_by = 50
	model = Food
	template_name = 'nutrihacker/search.html'
	
	def get_context_data(self, **kwargs):
		context = super(SearchFoodView, self).get_context_data(**kwargs)
		if self.request.method == 'GET':
			context['search'] = self.request.GET.get('search')
			context['order_by'] = self.request.GET.get('order_by')
			order = self.request.GET.get('order')
			if order:
				context['order'] = order
			else:
				context['order'] = 'asc'
			filter_count = self.request.GET.get('filter_count')
			if (filter_count == None):
				filter_count = 1
			context['filter_form'] = FilterFoodForm(self.request.GET, extra=int(filter_count)-1)
			context['filter_count'] = filter_count
			
		else:
			context['filter_form'] = FilterRecipeForm()
			
		return context
	
	# overrides ListView get_queryset to find names containing search term and pass them to template
	def get_queryset(self):
		# check for GET request
		if self.request.method == 'GET':
			query = self.request.GET.get('search')
			order_by = self.request.GET.get('order_by')
			order = self.request.GET.get('order')
			filter_count = self.request.GET.get('filter_count')
			if filter_count and filter_count.isnumeric():
				filter_count = int(filter_count)
			else:
				filter_count = 0
			filter_form = FilterFoodForm(self.request.GET, extra=filter_count-1)
			nutrients = [ ]
			nutrient_mins = [ ]
			nutrient_maxs = [ ]
			if filter_form.is_valid():
				for i in range(1, filter_count+1):
					nutrients.append(filter_form.cleaned_data.get('nutrient'+str(i)))
					nutrient_mins.append(filter_form.cleaned_data.get('nutrient_min'+str(i)))
					nutrient_maxs.append(filter_form.cleaned_data.get('nutrient_max'+str(i)))
			else:
				filter_count = 0
		else:
			query = None
		
		# no query shows all foods (but still uses given filters)
		if query == None:
			query = ''
			
		# If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
		object_list = Food.objects.filter(
			Q(name__icontains = query)
		).order_by(Length('name'))
			
		# filter results on given filters
		for i in range(0, filter_count):
			nutrient_min = nutrient_mins[i]
			nutrient_max = nutrient_maxs[i]
			if nutrient_min:
				if nutrients[i] == 'calories':
					object_list = object_list.filter(calories__gte=nutrient_min)
				elif nutrients[i] == 'totalFat':
					object_list = object_list.filter(totalFat__gte=nutrient_min)
				elif nutrients[i] == 'cholesterol':
					object_list = object_list.filter(cholesterol__gte=nutrient_min)
				elif nutrients[i] == 'sodium':
					object_list = object_list.filter(sodium__gte=nutrient_min)
				elif nutrients[i] == 'totalCarb':
					object_list = object_list.filter(totalCarb__gte=nutrient_min)
				elif nutrients[i] == 'protein':
					object_list = object_list.filter(protein__gte=nutrient_min)
				elif nutrients[i] == 'servingSize':
					object_list = object_list.filter(servingSize__gte=nutrient_min)
			if nutrient_max:
				if nutrients[i] == 'calories':
					object_list = object_list.filter(calories__lte=nutrient_max)
				elif nutrients[i] == 'totalFat':
					object_list = object_list.filter(totalFat__lte=nutrient_max)
				elif nutrients[i] == 'cholesterol':
					object_list = object_list.filter(cholesterol__lte=nutrient_max)
				elif nutrients[i] == 'sodium':
					object_list = object_list.filter(sodium__lte=nutrient_max)
				elif nutrients[i] == 'totalCarb':
					object_list = object_list.filter(totalCarb__lte=nutrient_max)
				elif nutrients[i] == 'protein':
					object_list = object_list.filter(protein__lte=nutrient_max)
				elif nutrients[i] == 'servingSize':
					object_list = object_list.filter(servingSize__lte=nutrient_max)
				
		# allow for user to order the search results on a certain field
		if order_by:
			# calories doesn't like Lower() because it's an int field?
			if order_by == 'calories':
				if order == 'desc':
					order_by = '-calories'
				object_list = object_list.order_by(order_by)
			elif order_by in [field.name for field in Food._meta.get_fields()]:
				if order == 'desc':
					object_list = object_list.order_by(Lower(order_by).desc())
				else:
					object_list = object_list.order_by(Lower(order_by))
		
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
			context['order_by'] = self.request.GET.get('order_by')
			order = self.request.GET.get('order')
			if order:
				context['order'] = order
			else:
				context['order'] = 'asc'
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
			order_by = self.request.GET.get('order_by')
			order = self.request.GET.get('order')
			
			filter_form = FilterRecipeForm(self.request.GET)
			if filter_form.is_valid():
				allergy_filter = filter_form.cleaned_data.get('allergy_filter')
				diet_filter = filter_form.cleaned_data.get('diet_filter')
				food_filter = filter_form.cleaned_data.get('food_filter')
				calories_min = filter_form.cleaned_data.get('calories_min')
				calories_max = filter_form.cleaned_data.get('calories_max')
			else:
				calories_min = None
				calories_max = None
				allergy_filter = None
				diet_filter = None
				food_filter = None
		
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
		# only include recipes that are tagged with all of the diet filters
		if diet_filter:
			object_list = object_list.filter(diets__in=diet_filter).annotate(dietCount=Count('diets')).filter(dietCount=len(diet_filter))
		# only include recipes containing the filtered food
		if food_filter:
			recipe_food_list = RecipeFood.objects.filter(food=food_filter)
			recipe_ids = recipe_food_list.values_list('recipe')
			object_list = object_list.filter(pk__in=recipe_ids)
		# filter results on calories, annotate queryset with sum of recipefood's (calories * portions) / recipe servings produced
		if calories_min or calories_max:
			object_list = object_list.annotate(calories=ExpressionWrapper(Sum(F('foods__calories') * F('recipefood__portions')) / F('servingsProduced'),
				output_field=IntegerField()))
			if calories_min:
				object_list = object_list.filter(calories__gt=calories_min-1)
			if calories_max:
				object_list = object_list.filter(calories__lt=calories_max+1)
			
		# allow for user to order the search results on a certain field
		if order_by:
			if order_by in ['name', 'user', 'created_at']:
				if order == 'desc':
					object_list = object_list.order_by(Lower(order_by).desc())
				else:
					object_list = object_list.order_by(Lower(order_by))
			elif order_by == 'calories':
				if order == 'desc':
					order_by = '-calories'
				# calories hasn't been annotated yet
				if not calories_min and not calories_max:
					object_list = object_list.annotate(calories=ExpressionWrapper(Sum(F('foods__calories') * F('recipefood__portions')) 
						/ F('servingsProduced'), output_field=IntegerField()))
				object_list = object_list.order_by(order_by)
			
		return object_list
