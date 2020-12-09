from django.http import HttpResponseRedirect	
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from nutrihacker.models import Profile, Allergy, DietPreference
from nutrihacker.forms import AllergyChoiceForm, DietChoiceForm, AllergyDeleteForm, DietDeleteForm
from nutrihacker.forms import UserForm, ProfileForm

class ProfileView(ListView):
	model = Profile
	template_name = 'nutrihacker/profile.html'

class UpdateProfile(LoginRequiredMixin, TemplateView):
	template_name = 'nutrihacker/update_profile.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile = get_object_or_404(Profile, user=self.request.user)
		context['user_form'] = UserForm(instance=self.request.user)
		context['profile_form'] = ProfileForm(instance=profile, initial={'height':profile.get_height(), 'weight':profile.get_weight()})
		return context
		
	def post(self, request):

#since our profile picture is in the file data not in database

		file_data = request.FILES

		profile = get_object_or_404(Profile, user=self.request.user)
		user_form = UserForm(request.POST, instance=self.request.user)
		profile_form = ProfileForm(request.POST, file_data, instance=profile) #the image field is in profile form so file_data will be in profileForm
				
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			profile = profile_form.save(commit=False)
			profile.set_height(profile_form.cleaned_data.get('height'))
			profile.set_weight(profile_form.cleaned_data.get('weight'))
			profile.set_caloriegoal(profile_form.cleaned_data.get('caloriegoal'))
			profile.save()
			return HttpResponseRedirect(reverse('nutrihacker:profile'))

		context = {'user_form':user_form, 'profile_form':profile_form}
		return self.render_to_response(context)


# Page to add dietary preferences and allergies.
# Login is required to view
class DietAndAllergiesView(LoginRequiredMixin, TemplateView):
	model = Allergy
	template_name = 'nutrihacker/diet_and_allergies.html'
	 
	# passes add/delete allergy/diet preference forms to the template
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile = Profile.objects.get(user=self.request.user)
		context['allergy_choice_form'] = AllergyChoiceForm(current_profile=profile)
		context['diet_choice_form'] = DietChoiceForm(current_profile=profile)
		context['allergy_delete_form'] = AllergyDeleteForm(current_profile=profile)
		context['diet_delete_form'] = DietDeleteForm(current_profile=profile)
		return context

# adds allergy to user from the AllergyChoiceForm form, always redirects back to DietAndAllergiesView		 
def add_allergy(request):
	if request.method == 'POST':
		form = AllergyChoiceForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			allergy = form.cleaned_data.get('allergy_select')
			allergy.profiles.add(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# adds diet preference to user from the DietChoiceForm form, always redirects back to DietAndAllergiesView
def add_diet_preference(request):
	if request.method == 'POST':
		form = DietChoiceForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			diet = form.cleaned_data.get('diet_select')
			diet.profiles.add(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# deletes allergies from user from the AllergyDeleteForm form, always redirects back to DietAndAllergiesView  
def delete_allergy(request):
	if request.method == 'POST':
		form = AllergyDeleteForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			allergy_list = form.cleaned_data.get('allergy_checkbox')
			for allergy in allergy_list:
				allergy.profiles.remove(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))

# deletes diet preferences from user from the DietDeleteForm form, always redirects back to DietAndAllergiesView  
def delete_diet_preference(request):
	if request.method == 'POST':
		form = DietDeleteForm(request.POST)
		
		if form.is_valid():
			profile = Profile.objects.get(user=request.user)
			diet_list = form.cleaned_data.get('diet_checkbox')
			for diet in diet_list:
				diet.profiles.remove(profile)
	
	return HttpResponseRedirect(reverse('nutrihacker:diet_and_allergies'))
	

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
