from decimal import Decimal
from dal import autocomplete

from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q

from nutrihacker.models import Food, Recipe
from nutrihacker.functions import chop_zeros

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

# autocomplete search for recipes
class RecipeAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Recipe.objects.none()

		qs = Recipe.objects.all()

		if self.q:
			qs = qs.filter(name__icontains=self.q)

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
		if (query == None or query == ''):
			return Food.objects.none()
		else: # If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
			object_list = Food.objects.filter(
				Q(name__icontains = query)
			)
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