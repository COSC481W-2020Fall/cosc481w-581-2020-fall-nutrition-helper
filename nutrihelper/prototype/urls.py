from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings 

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
    
    # /prototype/profile/
	path('profile/', views.ProfileView.as_view(), name='profile'),
    # I don't know what this does for the user profile page, might be unnessesary but I got it from a tutorial
    url(r'profile/(?P<username>[a-zA-Z0-9]+)$', views.get_user_profile),
    # For updating user profiles
    # url(r'^update_profile/(?P<slug>[\-\w]+)/$', views.UpdateProfile.as_view(), name='update_profile'),
    path('update_profile/', views.UpdateProfile.as_view(), name='update_profile'),
    
    # /prototype/login/
    path('login/', views.LoginView.as_view(), name='login'),
    # /prototype/logout/
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # /prototype/change_password/
    path('change_password/', views.PasswordChangeView.as_view(), name='change_password'),
    # /prototype/register_account/
    path('register_account/', views.RegisterAccountView.as_view(), name='register_account'),
    
]