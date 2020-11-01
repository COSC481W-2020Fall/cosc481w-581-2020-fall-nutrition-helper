from datetime import datetime
from dal import autocomplete

from django import forms
from django.utils.translation import ugettext as _

from django.forms import ModelForm
from django.contrib.auth.models import User

from .models import Food, Allergy, DietPreference, Profile

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
		
class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['gender', 'birthdate', 'height', 'weight', 'showmetric']

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
			self.fields[portions_field].widget.attrs.update({'step': 'any', 'style': 'width: 48px'})

	# override clean to add other errors
	def clean(self):
		cleaned_data = super(LogForm, self).clean()
		
		now = datetime.now().replace(second=0, microsecond=0)
		
		# raises an error if date/time is in the future
		if cleaned_data['date'] > now.date():
			self.add_error('date', forms.ValidationError(_('Invalid date: cannot create a log for the future'), code='future date'))
		elif datetime.combine(cleaned_data['date'], cleaned_data['time']) > now:
			self.add_error('time', forms.ValidationError(_('Invalid time: cannot create a log for the future'), code='future time'))
		
		return cleaned_data
            
# form for users to log their recipes
class RecipeForm(forms.Form):
    # form fields
    name = forms.CharField(label="Name the recipe", max_length=50, strip=True, required=True)
    servingsProduced = forms.DecimalField(label="Servings produced", decimal_places=2, min_value=0, max_value=99, initial=1, required=True)
    allergy = forms.ModelChoiceField(label="Allergy information", queryset=Allergy.objects.all())
    diet = forms.ModelChoiceField(label="Diet type", queryset=DietPreference.objects.all())
    instruction = forms.CharField(label="How it's made", widget=forms.Textarea)
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
            portions_field = 'portions%s' % (i+2)

            self.fields[food_field] = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all(),
                widget=autocomplete.ModelSelect2(url='nutrihacker:food_autocomplete'), required=True
            )
            self.fields[portions_field] = forms.DecimalField(label="Portions", decimal_places=2, min_value=0,
                max_value=99, initial=1, required=True
            )

