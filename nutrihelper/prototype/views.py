import requests, json

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
	template_name = 'prototype/index.html'

class FactsView(TemplateView):
	template_name = 'prototype/nutrifacts.html'

	def get_facts(self):
		n_facts = []
		return n_facts