from django.urls import path

from . import views

app_name = 'prototype'
urlpatterns = [
	# ex: /prototype/
	path('', views.IndexView.as_view(), name='index'),
	# ex: /prototype/nutrifacts/
	#path('nutrifacts/', views.DetailView.as_view(), name='nutrifacts'),
]