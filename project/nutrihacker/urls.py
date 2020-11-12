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
    # /nutrihacker/food_autocomplete/
    path('food_autocomplete/', views.FoodAutocomplete.as_view(), name='food_autocomplete'),
    # /nutrihacker/search/
    path('search/', views.SearchFoodView.as_view(), name='search'),
    path('search-recipe/', views.SearchRecipeView.as_view(), name='search-recipe'),
    
    #----------------------   LOG STUFF   -----------------------------------------------

    # /nutrihacker/logs/
    path('logs/', views.LogListView.as_view(), name='log_list'),
    # /nutrihacker/log_create/
    path('log_create/', views.LogCreateView.as_view(), name='log_create'),
    # /nutrihacker/log_detail/
    path('log_detail/<int:pk>/', views.LogDetailView.as_view(), name='log_detail'),
    # /nutrihacker/dailylog_delete/
    path('dailylog_delete/', views.DailyLogDeleteView.as_view(), name='dailylog_delete'),
    # /nutrihacker/meallog_delete/
    path('meallog_delete/', views.MealLogDeleteView.as_view(), name='meallog_delete'),
    # /nutrihacker/mealfood_delete/
    #path('mealfood_delete/', views.MealFoodDeleteView.as_view(), name='mealfood_delete'),
    # /nutrihacker/log_update/
    path('log_update/<int:pk>/', views.LogUpdateView.as_view(), name='log_update'),

    #------------------------- PROFILE STUFF ---------------------------------------------------
    
    # /nutrihacker/profile/
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # For updating user profiles
    path('update_profile/', views.UpdateProfile.as_view(), name='update_profile'),
    
    #----------------------   ALLERGY STUFF   -----------------------------------------------
    
    # /nutrihacker/diet_and_allergies/
    path('diet_and_allergies/', views.DietAndAllergiesView.as_view(), name='diet_and_allergies'),
    # /nutrihacker/add_allergy/
    path('add_allergy/', views.add_allergy, name='add_allergy'),
    # /nutrihacker/add_diet_preference/
    path('add_diet_preference/', views.add_diet_preference, name='add_diet_preference'),
    # /nutrihacker/delete_allergy/
    path('delete_allergy/', views.delete_allergy, name='delete_allergy'),
    # /nutrihacker/delete_diet_preference/
    path('delete_diet_preference/', views.delete_diet_preference, name='delete_diet_preference'),
    
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
    
    path('recipe/', views.ListRecipe.as_view(), name='list_recipe'),
    path('recipe/<int:pk>/', views.DetailRecipe.as_view(), name='detail_recipe'),
    path('recipe/create/', views.RecordRecipeView.as_view(), name='create_recipe'),
    path('recipe/<int:pk>/update/', views.UpdateRecipe.as_view(), name='update_recipe'),
    path('recipe/<int:pk>/delete/', views.DeleteRecipe.as_view(), name='delete_recipe'),
    
    
    #------------------------PI-CHART STUFF-------------------------------------------

    path('pi_chart/', views.FactsView.as_view() , name='pi_chart')
    #----------------------------------------------------------------------------------
]