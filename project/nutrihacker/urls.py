from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django import forms 

from . import views

# this file is included as a url pattern in ../nutrihelper/urls.py
# lists routes urls to views

app_name = 'nutrihacker'
urlpatterns = [
	# /nutrihacker/
    path('', views.IndexView.as_view(), name='index'),
	# /nutrihacker/nutrifacts/
    path('nutrifacts/<int:pk>/', views.FactsView.as_view(), name='nutrifacts'),
	# /nutrihacker/description/
    path('description/', views.DescriptionView.as_view(), name='description'),
    # /nutrihacker/search/
    path('search/', views.SearchResultsView.as_view(), name='search'),
    
    #----------------------   LOG STUFF   -----------------------------------------------

    # /nutrihacker/log
    path('log/', views.LogView.as_view(), name='log'),
    # /nutrihacker/record_log
    path('record_log/', views.RecordLogView.as_view(), name='record_log'),
    
    
    #------------------------- PROFILE STUFF ---------------------------------------------------
    # /nutrihacker/profile/
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # For updating user profiles
    path('update_profile/<profile_id>/', views.UpdateProfile.as_view(), name='update_profile'),
    
    
    
    #----------------------   ALLERGY STUFF   -----------------------------------------------
    
    # /nutrihacker/diet_and_allergies/
    path('diet_and_allergies/', views.DietAndAllergiesView.as_view(), name='diet_and_allergies'),
    # /nutrihacker/add_allergy/
    path('add_allergy/', views.AddAllergyView.as_view(), name='add_allergy'),
    # /nutrihacker/add_diet_preference/
    path('add_diet_preference/', views.AddDietPreferenceView.as_view(), name='add_diet_preference'),
    # /nutrihacker/delete_allergy/
    path('delete_allergy/', views.DeleteAllergyView.as_view(), name='delete_allergy'),
    # /nutrihacker/delete_diet_preference/
    path('delete_diet_preference/', views.DeleteDietPreferenceView.as_view(), name='delete_diet_preference'),
    
    
    
    #----------------------   CREDENTIAL STUFF   -----------------------------------------------
    # /nutrihacker/login/
    path('login/', views.LoginView.as_view(), name='login'),
    # /nutrihacker/logout/
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # /nutrihacker/change_password/
    path('change_password/', views.PasswordChangeView.as_view(), name='change_password'),
    # /nutrihacker/register_account/
    path('register_account/', views.RegisterAccountView.as_view(), name='register_account'),
    
    
    #----------------------   RECIPE STUFF   -----------------------------------------------
    
    path('recipe/', views.ListRecipe, name='list-recipe'),
    path('recipe/create/', views.CreateRecipe.as_view(), name='create_recipe'),
    path('recipe/<int:pk>/', views.DetailRecipe.as_view(), name='detail_recipe'),
    path('recipe/<int:pk>/update/', views.UpdateRecipe.as_view(), name='update_recipe'),
    path('recipe/<int:pk>/delete/', views.DeleteRecipe.as_view(), name='delete_recipe'),
    
    path('record_recipe/', views.RecordRecipeView.as_view(), name='record_recipe'),
    
    
    
    
    
    path('recipefood/', views.ListRecipeFood.as_view(), name='list_recipefood'),
    path('recipefood/create/', views.CreateRecipeFood.as_view(), name='create_recipefood'),
    path('recipefood/<int:pk>/', views.DetailRecipeFood.as_view(), name='detail_recipefood'),
    path('recipefood/<int:pk>/update/', views.UpdateRecipeFood.as_view(), name='update_recipefood'),
    path('recipefood/<int:pk>/delete/', views.DeleteRecipeFood.as_view(), name='delete_recipefood'),
    
    #---------------------------------------------------------------------
]