import requests, json

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import TemplateView

class IndexView(TemplateView):
	template_name = 'prototype/index.html'

X_APP_ID = '4341d1c0'
X_APP_KEY = 'd9a495c01cc4e73cb411da7f663f0819'
X_REMOTE_USER_ID = '0'

url = "https://trackapi.nutritionix.com/v2/natural/nutrients"

class FactsView(TemplateView):
	template_name = 'prototype/nutrifacts.html'

	def get_facts(self):
		payload = {
			"query":"1 serving broccoli"
		}

		headers = {
			'x-app-id': X_APP_ID,
			'x-app-key': X_APP_KEY,
			'x-remote-user-id': X_REMOTE_USER_ID
		}

		response = requests.request("POST", url, headers=headers, data = payload)

		info = json.loads(response.text)

		n_facts = [
			info['foods'][0]['food_name'],
			info['foods'][0]['serving_weight_grams'],
			info['foods'][0]['nf_calories'],
			info['foods'][0]['nf_total_fat'],
			info['foods'][0]['nf_cholesterol'],
			info['foods'][0]['nf_sodium'],
			info['foods'][0]['nf_total_carbohydrate'],
			info['foods'][0]['nf_protein']
		]

		return n_facts