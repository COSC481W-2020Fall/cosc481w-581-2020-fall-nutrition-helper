from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.contrib.auth import views as auth_views

from .models import Food

class IndexView(TemplateView):
	template_name = 'prototype/index.html'

class DescriptionView(TemplateView):
	template_name = 'prototype/description.html'

# displays the nutrition information of a food obtained from a GET request
class FactsView(TemplateView):
	template_name = 'prototype/nutrifacts.html'
	
	# overrides TemplateView get_context_data in order to pass nutrition information to the template in context
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		# gets the HTTPRequest object from the view and accesses the 'food' field
		query = self.request.GET['food']
		
		# gets a dictionary of nutrition information from the food model that start with the query
		# 404s if the food is not found in the model
		context['f_list'] = get_object_or_404(Food, name__startswith=query).get_facts()
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

class LoginAccountView(auth_views.LoginView):
    template_name = "prototype/login.html"

class LogoutAccountView(auth_views.LogoutView):
    template_name = "prototype/logout.html"

class PasswordChangeAccountView(auth_views.PasswordChangeView):
    template_name = "prototype/changepassword.html"



        
        
        
    
    
    