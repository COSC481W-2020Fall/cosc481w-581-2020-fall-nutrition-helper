import requests, json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
	template_name = 'prototype/index.html'

class DescriptionView(TemplateView):
	template_name = 'prototype/description.html'

class FactsView(TemplateView):
	template_name = 'prototype/nutrifacts.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['food'] = self.request.GET['food']
		return context
