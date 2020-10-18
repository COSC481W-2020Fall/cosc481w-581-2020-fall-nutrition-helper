from django import forms

from .models import Allergy, DietPreference
from .models import DailyLog, MealLog, Food

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

class LogForm(forms.Form):
	date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
	time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
	food = forms.ModelChoiceField(label="Choose a food", queryset=Food.objects.all())
	portions = forms.DecimalField(decimal_places=2, min_value=0, max_value=99)

	portions.widget.attrs.update({'step': 'any'})

	# def __init__(self, *args, **kwargs):
	# 	super(LogForm, self).__init__(*args, **kwargs)

	# 	for k,v in args[0].items():
	# 		if k.startswith('food') and k not in self.fields.keys():
	# 			self.fields[k] = 