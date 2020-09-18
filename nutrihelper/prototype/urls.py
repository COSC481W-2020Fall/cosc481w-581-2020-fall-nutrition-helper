from django.urls import path

from . import views

app_name = 'prototype'
urlpatterns = [
	# /prototype/
	path('', views.IndexView.as_view(), name='index'),
	# /prototype/nutrifacts/
	path('nutrifacts/', views.FactsView.as_view(), name='nutrifacts'),
	# /prototype/description/
	path('description/', views.DescriptionView.as_view(), name='description')
]