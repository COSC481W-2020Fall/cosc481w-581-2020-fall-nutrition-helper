from decimal import Decimal

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from nutrihacker.models import Food, Recipe, RecipeFood
from nutrihacker.models import Allergy, DietPreference

from nutrihacker.forms import RecipeForm

from nutrihacker.functions import chop_zeros

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




class ListRecipe(ListView):
	model = Recipe
	#context_object_name = 'recipes'
	fields = '__all__'
	template_name='nutrihacker/recipe/list_recipe.html'
	
	def get_queryset(self):
		object_list = Recipe.objects.filter(user=self.request.user)
		return object_list
		



# page for user to edit recipe information, modifies database according to submitted data
class UpdateRecipe(UserPassesTestMixin, FormView):
	form_class = RecipeForm

	template_name = 'nutrihacker/recipe/update_recipe.html'
	recipe_id = 0 # id of recipe to be redirected to
	
	# Limit updating recipe to creator
	def test_func(self):
		recipe = Recipe.objects.get(id=self.kwargs['pk'])
		return recipe.user == self.request.user

	# override get_success_url to correct recipe
	def get_success_url(self):
		return reverse_lazy('nutrihacker:detail_recipe', kwargs={'pk':self.recipe_id})

	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(UpdateRecipe, self).get_form_kwargs()

		# checks whether form data was submitted
		if 'data' in kwargs: # if submitted, set 'extra' to 'extra_field_count' from form
			kwargs['extra'] = kwargs['data']['extra_field_count']
		else: # if not submitted, 'extra' is the number of RecipeFoods minus 1
			kwargs['extra'] = RecipeFood.objects.filter(recipe__id=self.kwargs['pk']).count() - 1
		
		return kwargs

	# override get_context_data to provide ids of Recipe
	def get_context_data(self, **kwargs):
		context = super(UpdateRecipe, self).get_context_data(**kwargs)
		
		ml = Recipe.objects.get(id=self.kwargs['pk'])
		
		context['recipe_id'] = ml.id
		
		return context

	# override get_initial to provide initial form values
	def get_initial(self):
		initial = super(UpdateRecipe, self).get_initial()
		ml = Recipe.objects.get(id=self.kwargs['pk'])

		self.recipe_id = ml.id

		initial['name'] = ml.name
		initial['servingsProduced'] = ml.servingsProduced
		initial['allergies'] = ml.allergies.all()
		initial['diets'] = ml.diets.all()
		initial['instruction'] = ml.instruction
		initial['is_public'] = ml.is_public

		mf_list = RecipeFood.objects.filter(recipe=ml)
		for i in range(mf_list.count()):
			initial['food'+str(i+1)] = mf_list[i].food
			initial['portions'+str(i+1)] = chop_zeros(mf_list[i].portions)
		
		return initial

	# override form_valid to modify model instances from submitted data
	def form_valid(self, form):
		# get data from the form
		name = form.cleaned_data.get('name')
		servingsProduced = form.cleaned_data.get('servingsProduced')
		allergies = form.cleaned_data.get('allergies')
		diets = form.cleaned_data.get('diets')
		instruction = form.cleaned_data.get('instruction')
		is_public = form.cleaned_data.get('is_public')
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
		
		
		
		# gets the recipe for this id
		recipe = Recipe.objects.get(id=self.recipe_id)

		#changing fields that are changed
		if recipe.name is not name:
			recipe.name = name
			recipe.save()
			
		if recipe.servingsProduced is not servingsProduced:
			recipe.servingsProduced = servingsProduced
			recipe.save()
			
		if recipe.allergies is not allergies:
			recipe.allergies.set(allergies)
			recipe.save()
		
		if recipe.diets is not diets:
			recipe.diets.set(diets)
			recipe.save()
		
		if recipe.instruction is not instruction:
			recipe.instruction = instruction
			recipe.save()
		
		if recipe.is_public is not is_public:
			recipe.is_public = is_public
			recipe.save()
		
		
			
		# update the daily log id to be passed to success url
		self.recipe_id = recipe.id

		# delete current list of foods
		RecipeFood.objects.filter(recipe=recipe).delete()

		# creates new meal foods for each food for this meal log
		for i in range(1, food_number+1):
			# checks if fields exist
			if 'food'+str(i) in food:
				recipe_food = RecipeFood.create(recipe, food['food'+str(i)], portions['portions'+str(i)])
				recipe_food.save()


		return super(UpdateRecipe, self).form_valid(form)


class DeleteRecipe(UserPassesTestMixin, DeleteView):
	model = Recipe
	fields = '__all__'
	success_url = reverse_lazy('nutrihacker:list_recipe')
	template_name = 'nutrihacker/recipe/delete_recipe.html'
	
	# Limit updating recipe to creator
	def test_func(self):
		recipe = Recipe.objects.get(id=self.kwargs['pk'])
		return recipe.user == self.request.user
	
	# override get_object to get id from form
	def get_object(self, queryset=None):
		# make sure user has permission by matching the user to the Recipe
		try:
			dl = Recipe.objects.get(user=self.request.user, id=self.request.POST.get('id'))
		except Recipe.DoesNotExist:
			raise PermissionDenied

		return dl

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
		diets = form.cleaned_data.get('diets')
		allergies = form.cleaned_data.get('allergies')
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
		recipe.allergies.set(allergies)
		recipe.diets.set(diets)
		recipe.save()

		# creates a recipe food for each food for this recipe
		for i in range(1, food_number+1):
			recipe_food = RecipeFood.create(recipe, food['food'+str(i)], portions['portions'+str(i)])
			recipe_food.save()

		return super(RecordRecipeView, self).form_valid(form)
		
		
# saves submitted info to database
class CopyRecipe(FormView):
	form_class = RecipeForm
	template_name = 'nutrihacker/recipe/copy_recipe.html'
	success_url = reverse_lazy('nutrihacker:list_recipe')
	recipe_id = 0 # id of recipe to be redirected to
	
	# override get_form_kwargs to get number of extra fields
	def get_form_kwargs(self):
		kwargs = super(CopyRecipe, self).get_form_kwargs()

		# checks whether form data was submitted
		if 'data' in kwargs: # if submitted, set 'extra' to 'extra_field_count' from form
			kwargs['extra'] = kwargs['data']['extra_field_count']
		else: # if not submitted, 'extra' is the number of RecipeFoods minus 1
			kwargs['extra'] = RecipeFood.objects.filter(recipe__id=self.kwargs['pk']).count() - 1
		
		return kwargs

	# override get_context_data to include form html
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['recipe_form'] = RecipeForm()
		
		recipe_source = Recipe.objects.get(id=self.kwargs['pk'])
		context['recipe_id'] = recipe_source.id
		
		return context

		
	# override get_initial to provide initial form values
	def get_initial(self):
		initial = super(CopyRecipe, self).get_initial()
		print(initial)
		ml = Recipe.objects.get(id=self.kwargs['pk'])

		self.recipe_id = ml.id

		initial['name'] = ml.name
		initial['servingsProduced'] = ml.servingsProduced
		initial['allergies'] = ml.allergies
		initial['diets'] = ml.diets
		initial['instruction'] = ml.instruction
		initial['is_public'] = ml.is_public

		mf_list = RecipeFood.objects.filter(recipe=ml)
		for i in range(mf_list.count()):
			initial['food'+str(i+1)] = mf_list[i].food
			initial['portions'+str(i+1)] = chop_zeros(mf_list[i].portions)
		
		return initial

	# override form_valid to create model instances from submitted info
	def form_valid(self, form):
		name = form.cleaned_data.get('name')
		servingsProduced = form.cleaned_data.get('servingsProduced')
		instruction = form.cleaned_data.get('instruction')
		name = form.cleaned_data.get('name')
		diets = form.cleaned_data.get('diets')
		allergies = form.cleaned_data.get('allergies')
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
		recipe.allergies = allergies
		recipe.diets = diets
		recipe.save()

		# creates a recipe food for each food for this recipe
		for i in range(1, food_number+1):
			recipe_food = RecipeFood.create(recipe, food['food'+str(i)], portions['portions'+str(i)])
			recipe_food.save()

		return super(CopyRecipe, self).form_valid(form)
