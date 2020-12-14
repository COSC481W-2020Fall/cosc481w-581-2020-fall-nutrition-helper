from datetime import datetime
from dal import autocomplete

from django import forms
from django.utils.translation import ugettext as _

from django.forms import ModelForm
from django.contrib.auth.models import User

from .models import Food, Recipe, Allergy, DietPreference, Profile

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
		
class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['gender', 'profilePic', 'birthdate', 'height', 'weight', 'caloriegoal','showmetric']
		
class FilterFoodForm(forms.Form):
	nutrient_choices = [
		('calories', 'Calories'), 
		('totalFat', 'Total Fat'), 
		('cholesterol', 'Cholesterol'), 
		('sodium', 'Sodium'), 
		('totalCarb', 'Total Carb'), 
		('protein', 'Protein'), 
		('servingSize', 'Serving Size')
	]
	nutrient1 = forms.ChoiceField(choices=nutrient_choices, label="Nutrient")
	nutrient_min1 = forms.IntegerField(label="Range", min_value=0, max_value=10000, required=False, widget=forms.NumberInput(attrs={'class':'nutrient_range'}))
	nutrient_max1 = forms.IntegerField(label="to", min_value=0, max_value=10000, required=False, widget=forms.NumberInput(attrs={'class':'nutrient_range'}))
	
	# override __init__ to create dynamic number of fields
	def __init__(self, *args, **kwargs):
		# get number of extra fields from kwargs
		extra_fields = kwargs.pop('extra', 0)
		
		super(FilterFoodForm, self).__init__(*args, **kwargs)
		
		form_data = {}

		# add extra fields
		for i in range(int(extra_fields)):
			nutrient_field = 'nutrient%s' % (i+2)
			min_field = 'nutrient_min%s' % (i+2)
			max_field = 'nutrient_max%s' % (i+2)
			
			self.fields[nutrient_field] = forms.ChoiceField(choices=self.nutrient_choices, label="Nutrient")
			self.fields[min_field] = forms.IntegerField(label="Range", min_value=0, max_value=10000, required=False, widget=forms.NumberInput(attrs={'class':'nutrient_range'}))
			self.fields[max_field] = forms.IntegerField(label="to", min_value=0, max_value=10000, required=False, widget=forms.NumberInput(attrs={'class':'nutrient_range'}))

class FilterRecipeForm(forms.Form):
	allergy_filter = forms.ModelMultipleChoiceField(label="Exclude allergy", queryset=Allergy.objects.all(), required=False, widget=autocomplete.ModelSelect2Multiple())
	diet_filter = forms.ModelMultipleChoiceField(label="Include diet", queryset=DietPreference.objects.all(), required=False, widget=autocomplete.ModelSelect2Multiple())
	calories_min = forms.IntegerField(label="Calorie range", min_value=0, max_value=10000, required=False)
	calories_max = forms.IntegerField(label="to", min_value=0, max_value=10000, required=False)
	food_filter = forms.ModelChoiceField(
		label="Include food", queryset=Food.objects.all(), widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'),
		required=False
	)

# creates a model choice select field to add allergies
class AllergyChoiceForm(forms.Form):
	allergy_select = forms.ModelChoiceField(label="Add allergy", queryset=Allergy.objects.all())
	
	def __init__(self,*args,**kwargs):
		self.current_profile = kwargs.pop('current_profile', None) 
		super(AllergyChoiceForm,self).__init__(*args,**kwargs)
		# exclude choices if they've already been added to the profile
		if self.current_profile != None:
			self.fields['allergy_select'].queryset = Allergy.objects.exclude(profiles=self.current_profile)

# similar to AlleryChoiceForm but for diet preferences
class DietChoiceForm(forms.Form):
	diet_select = forms.ModelChoiceField(label="Add diet preference", queryset=DietPreference.objects.all())
	
	def __init__(self,*args,**kwargs):
		self.current_profile = kwargs.pop('current_profile', None)
		super(DietChoiceForm,self).__init__(*args,**kwargs)
		# exclude choices if they've already been added to the profile
		if self.current_profile != None:
			self.fields['diet_select'].queryset = DietPreference.objects.exclude(profiles=self.current_profile)

# creates a form of checkboxes for deleting allergies, dynamically removes allergies if profile doesn't have them
class AllergyDeleteForm(forms.Form):
	allergy_checkbox = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, queryset=Allergy.objects.all())
	def __init__(self,*args,**kwargs):
		self.current_profile = kwargs.pop('current_profile', None) 
		super(AllergyDeleteForm,self).__init__(*args,**kwargs)
		# only include allergy selection if they've already been added to the profile
		if self.current_profile != None:
			self.fields['allergy_checkbox'].queryset = Allergy.objects.filter(profiles=self.current_profile)
		 
class DietDeleteForm(forms.Form):
	diet_checkbox = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, queryset=DietPreference.objects.all())
	def __init__(self,*args,**kwargs):
		self.current_profile = kwargs.pop('current_profile', None) 
		super(DietDeleteForm,self).__init__(*args,**kwargs)
		# only include diet selection if they've already been added to the profile
		if self.current_profile != None:
			self.fields['diet_checkbox'].queryset = DietPreference.objects.filter(profiles=self.current_profile)

# form for users to log their meals
class LogForm(forms.Form):
	# form fields
	date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
	time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)
	food1 = forms.ModelChoiceField(
		label="Choose a food", queryset=Food.objects.all(), widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'),
		required=True
	)
	food_portions1 = forms.DecimalField(label="Portions", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	recipe1 = forms.ModelChoiceField(
		label="Choose a recipe", queryset=Recipe.objects.all(), widget=autocomplete.ModelSelect2(url='nutrihacker:recipe_autocomplete'),
		required=True
	)
	recipe_portions1 = forms.DecimalField(label="Portions", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	
	# hidden fields that keep track of how many extra fields have been added
	extra_food_count = forms.CharField(widget=forms.HiddenInput())
	extra_recipe_count = forms.CharField(widget=forms.HiddenInput())

	food_portions1.widget.attrs.update({'step': 'any', 'style': 'width: 48px'})
	recipe_portions1.widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

	# override __init__ to create dynamic number of food and portions fields
	def __init__(self, *args, **kwargs):
		# get number of extra fields from kwargs
		extra_foods = kwargs.pop('f_extra', 0)
		extra_recipes = kwargs.pop('r_extra', 0)
		
		super(LogForm, self).__init__(*args, **kwargs)
		
		self.fields['extra_food_count'].initial = extra_foods
		self.fields['extra_recipe_count'].initial = extra_recipes

		form_data = {}
		
		submitted = 'data' in kwargs
		if submitted:
			form_data = kwargs['data']

			if 'food1' not in form_data:
				del self.fields['food1']
				del self.fields['food_portions1']
			if 'recipe1' not in form_data:
				del self.fields['recipe1']
				del self.fields['recipe_portions1']

		if extra_foods == -1:
			del self.fields['food1']
			del self.fields['food_portions1']
		if extra_recipes == -1:
			del self.fields['recipe1']
			del self.fields['recipe_portions1']

		# add extra food fields
		for i in range(int(extra_foods)):
			food_field = 'food'+str(i+2)
			portions_field = 'food_portions'+str(i+2)

			# checks if current food and portions field exists
			if not submitted or food_field in form_data:
				self.fields[food_field] = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all(),
					widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'), required=True
				)
				self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
					max_value=99, initial=1, required=True
				)
				self.fields[portions_field].widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

		# add extra recipe fields
		for i in range(int(extra_recipes)):
			recipe_field = 'recipe'+str(i+2)
			portions_field = 'recipe_portions'+str(i+2)

			# checks if current recipe and portions field exists
			if not submitted or recipe_field in form_data:
				self.fields[recipe_field] = forms.ModelChoiceField(label="Choose a recipe", queryset=Recipe.objects.all(),
					widget=autocomplete.ModelSelect2(url='nutrihacker:recipe_autocomplete'), required=True
				)
				self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
					max_value=99, initial=1, required=True
				)
				self.fields[portions_field].widget.attrs.update({'step': 'any', 'style': 'width: 48px'})			

	# override clean to add other errors
	def clean(self):
		cleaned_data = super(LogForm, self).clean()
		
		now = datetime.now().replace(second=0, microsecond=0)
		
		# raises an error if date/time is in the future
		if cleaned_data['date'] > now.date():
			self.add_error('date', forms.ValidationError(_('Invalid future date'), code='future date'))
		elif datetime.combine(cleaned_data['date'], cleaned_data['time']) > now:
			self.add_error('time', forms.ValidationError(_('Invalid future time'), code='future time'))

		empty = True
		# loops through all food/recipe and portions fields
		for i in range(max(int(cleaned_data['extra_food_count']), int(cleaned_data['extra_recipe_count']))+1):
			portions_field = 'food_portions'+str(i+1)
			# check if food field exists
			if portions_field in cleaned_data:
				empty = False
				# check if portions field is zero
				if cleaned_data[portions_field] == 0:
					self.add_error(portions_field, forms.ValidationError(_('Must be greater than zero'), code='zero portions'))
		
			portions_field = 'recipe_portions'+str(i+1)
			# check if recipe field exists
			if portions_field in cleaned_data:
				empty = False
				# check if portions field is zero
				if cleaned_data[portions_field] == 0:
					self.add_error(portions_field, forms.ValidationError(_('Must be greater than zero'), code='zero portions'))
		
		if empty:
			self.add_error(None, forms.ValidationError(_('Must have at least one food or recipe'), code='empty log'))

		return cleaned_data
	
# form for users to log their recipes
class RecipeForm(forms.Form):
	# form fields
	name = forms.CharField(label="Name the recipe", max_length=50, strip=True, required=True)
	servingsProduced = forms.DecimalField(label="Servings produced", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	allergies = forms.ModelMultipleChoiceField(label="Allergy information", queryset=Allergy.objects.all(), required=False)
	diets = forms.ModelMultipleChoiceField(label="Diet type", queryset=DietPreference.objects.all(), required=False)
	instruction = forms.CharField(label="How it's made", widget=forms.Textarea, required=False)
	is_public = forms.BooleanField(initial=True, required=False)
	food1 = forms.ModelChoiceField(
		label="Choose a food", queryset=Food.objects.all(), widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'),
		required=True
	)
	portions1 = forms.DecimalField(label="Portions", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	recipe_image = forms.ImageField(label='Upload Recipe Image', required=False)
	# hidden field that keeps track of how many extra fields have been added
	extra_field_count = forms.CharField(widget=forms.HiddenInput())

	portions1.widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

	# override __init__ to create dynamic number of food and portions fields
	def __init__(self, *args, **kwargs):
		# get number of extra fields from kwargs
		extra_fields = kwargs.pop('extra', 0)
		
		super(RecipeForm, self).__init__(*args, **kwargs)
		self.fields['extra_field_count'].initial = extra_fields
		
		form_data = {}
		
		submitted = 'data' in kwargs
		if submitted:
			form_data = kwargs['data']

		if submitted and 'food1' not in form_data:
			del self.fields['food1']
			del self.fields['portions1']

		# add extra fields
		for i in range(int(extra_fields)):
			food_field = 'food%s' % (i+2)
			portions_field = 'portions%s' % (i+2)
			
			# checks if current food and portions field exists
			if not submitted or food_field in form_data:
				self.fields[food_field] = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all(),
					widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'), required=True
				)
				self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
					max_value=99, initial=1, required=True
				)
	
	# override clean to add other errors
	def clean(self):
		cleaned_data = super(RecipeForm, self).clean()
		
		
		for i in range(int(cleaned_data['extra_field_count'])+1):
			for j in range(int(cleaned_data['extra_field_count'])+1):
				if (i != j):
					if ('food'+str(i+1)) in cleaned_data and ('food'+str(j+1)) in cleaned_data and cleaned_data['food'+str(i+1)] == cleaned_data['food'+str(j+1)]:
						self.add_error('food'+str(j+1), forms.ValidationError(_('More than one of same food'), code='duplicate food'))

		for i in range(int(cleaned_data['extra_field_count'])+1):
			if ('portions'+str(i+1)) in cleaned_data and cleaned_data['portions'+str(i+1)] == 0:
				self.add_error('portions'+str(i+1), forms.ValidationError(_('Must be greater than zero'), code='zero portions'))
		
		return cleaned_data

