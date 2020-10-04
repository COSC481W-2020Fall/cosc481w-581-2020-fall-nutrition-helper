from django.urls import path

from . import views

# this file is included as a url pattern in ../nutrihelper/urls.py
# lists routes urls to views

app_name = 'prototype'
urlpatterns = [
	# /prototype/
	path('', views.IndexView.as_view(), name='index'),
	# /prototype/nutrifacts/
	path('nutrifacts/<int:pk>/', views.FactsView.as_view(), name='nutrifacts'),
	# /prototype/description/
	path('description/', views.DescriptionView.as_view(), name='description'),
    # /prototype/search/
	path('search/', views.SearchResultsView.as_view(), name='search'),
    
    # /prototype/login/
    path('login/', views.LoginAccountView.as_view(), name='login'),
    # /prototype/logout/
    path('logout/', views.LogoutAccountView.as_view(), name='logout'),
    # /prototype/change_password/
    path('change_password/', views.PasswordChangeAccountView.as_view(), name='change_password'),
    
]