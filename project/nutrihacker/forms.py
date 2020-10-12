from django import forms
from .models import Allergy, DietPreference

# creates a multiple choice select field to add allergies
class AllergyChoiceForm(forms.Form):
    allergy_select = forms.ModelChoiceField(label="Add allergy", queryset=Allergy.objects.all())

# similar to AlleryChoiceForm but for diet preferences
class DietChoiceForm(forms.Form):
    diet_select = forms.ModelChoiceField(label="Add diet preference", queryset=DietPreference.objects.all())