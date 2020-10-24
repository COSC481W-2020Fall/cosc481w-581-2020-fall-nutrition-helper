from dal import autocomplete

from django import forms

from .models import Food, Allergy, DietPreference

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
	portions1 = forms.DecimalField(label="Portions", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	# hidden field that keeps track of how many extra fields have been added
	extra_field_count = forms.CharField(widget=forms.HiddenInput())

	portions1.widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

	# override __init__ to create dynamic number of food and portions fields
	def __init__(self, *args, **kwargs):
		# get number of extra fields from kwargs
		extra_fields = kwargs.pop('extra', 0)
		
		super(LogForm, self).__init__(*args, **kwargs)
		self.fields['extra_field_count'].initial = extra_fields

		# add extra fields
		for i in range(int(extra_fields)):
			food_field = 'food%s' % (i+2)
			portions_field = 'portions%s' % (i+2)

			self.fields[food_field] = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all(),
				widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'), required=True
			)
			self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
				max_value=99, initial=1, required=True
			)
            
# form for users to log their meals
class RecipeForm(forms.Form):
	# form fields
	food1 = forms.ModelChoiceField(
		label="Choose a food", queryset=Food.objects.all(), widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'),
		required=True
	)
	portions1 = forms.DecimalField(label="Portions", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
	# hidden field that keeps track of how many extra fields have been added
	extra_field_count = forms.CharField(widget=forms.HiddenInput())

	portions1.widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

	# override __init__ to create dynamic number of food and portions fields
	def __init__(self, *args, **kwargs):
		# get number of extra fields from kwargs
		extra_fields = kwargs.pop('extra', 0)
		
		super(RecipeForm, self).__init__(*args, **kwargs)
		self.fields['extra_field_count'].initial = extra_fields

		# add extra fields
		for i in range(int(extra_fields)):
			food_field = 'food%s' % (i+2)
			portions_field = 'portion%s' % (i+2)

			self.fields[food_field] = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all(),
				widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'), required=True
			)
			self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
				max_value=99, initial=1, required=True
			)
