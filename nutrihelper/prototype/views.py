import decimal

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.contrib.auth import views as auth_views
from django.shortcuts import render

from .models import Food
from .models import Profile

class IndexView(TemplateView):
	template_name = 'prototype/index.html'

class DescriptionView(TemplateView):
	template_name = 'prototype/description.html'

# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == value.to_integral():
		return value.quantize(decimal.Decimal(1))
	else:
		return value.normalize()

# displays the nutrition information of a food
class FactsView(DetailView):
	model = Food
	template_name = 'prototype/nutrifacts.html'
	
	# overrides DetailView get_context_data
	def get_context_data(self, **kwargs):
		# get context
		context = super().get_context_data(**kwargs)
	
		# if there is a GET request
		if self.request.method == 'GET':
			# get the query value
			query = self.request.GET.get('portions')
			
			# if query empty
			if query == None:
				# set to 1
				query = decimal.Decimal(1)
			else:
				# convert query to python decimal
				query = decimal.Decimal(query)
		# no GET request
		else:
			# set query to 1
			query = decimal.Decimal(1)

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

# displays the food that match a search, passed to the template as a list
class SearchResultsView(ListView):
	model = Food
	template_name = 'prototype/search.html'
	
	# overrides ListView get_queryset to find names containing search term and pass them to template
	def get_queryset(self):
		query = self.request.GET.get('term')
		# TODO: change the case of no query terms from returning all food items to returning an empty list
		if (query == None):
			return Food.objects.all()
		else: # If there are any foods containing the query, they will be in the resulting object_list which is used by search.html in a for loop
			object_list = Food.objects.filter(
				Q(name__icontains = query)
			)
			return object_list


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'prototype/profile.html', {"user":user})


# displays the food that match a search, passed to the template as a list
class ProfileView(ListView):
	model = Profile
	template_name = 'prototype/profile.html'
	
	# overrides DetailView get_context_data
	def get_context_data(self, **kwargs):
		# get context
		context = super().get_context_data(**kwargs)
		
		# TODO: PUT SOMETHING HERE THAT MAKES SENSE

		return 

class LoginAccountView(auth_views.LoginView):
	template_name = "prototype/login.html"

class LogoutAccountView(auth_views.LogoutView):
	template_name = "prototype/logout.html"

class PasswordChangeAccountView(auth_views.PasswordChangeView):
	template_name = "prototype/changepassword.html"



		
		
		
	
	
	