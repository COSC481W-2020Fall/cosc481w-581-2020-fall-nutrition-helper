from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings 

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
    # /nutrihacker/Food_intake
    path('Food_intake/',views.FoodIntakeView.as_view(), name='Food_intake'),
    
    
    
    #------------------------- PROFILE STUFF ---------------------------------------------------
    # /nutrihacker/profile/
	path('profile/', views.ProfileView.as_view(), name='profile'),
    # I don't know what this does for the user profile page, might be unnessesary but I got it from a tutorial
    url(r'profile/(?P<username>[a-zA-Z0-9]+)$', views.get_user_profile),
    # For updating user profiles
    # url(r'^update_profile/(?P<slug>[\-\w]+)/$', views.UpdateProfile.as_view(), name='update_profile'),
    path('update_profile/', views.UpdateProfile.as_view(), name='update_profile'),
    
    
    
    #----------------------   ALLERGY STUFF   -----------------------------------------------
    
    # /nutrihacker/diet_and_allergies/
    path('diet_and_allergies/', views.DietAndAllergiesView.as_view(), name='diet_and_allergies'),
    # /nutrihacker/add_allergy/
    path('add_allergy/', views.AddAllergyView.as_view(), name='add_allergy'),
    # /nutrihacker/add_diet_preference/
    path('add_diet_preference/', views.AddDietPreferenceView.as_view(), name='add_diet_preference'),
    
    
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
    path('recipe/<int:pk>/', views.DetailRecipe.as_view(), name='detail-recipe'),
    path('recipe/create/', views.CreateRecipe.as_view(), name='create-recipe'),
    path('recipe/<int:pk>/update/', views.UpdateRecipe.as_view(), name='update-recipe'),
    path('recipe/<int:pk>/delete/', views.DeleteRecipe.as_view(), name='delete-recipe'),
    
    
    path('recipefood/', views.ListRecipeFood.as_view(), name='list-recipefood'),
    path('recipefood/<int:pk>/', views.DetailRecipeFood.as_view(), name='detail-recipefood'),
    path('recipefood/create/', views.CreateRecipeFood.as_view(), name='create-recipefood'),
    path('recipefood/<int:pk>/update/', views.UpdateRecipeFood.as_view(), name='update-recipefood'),
    path('recipefood/<int:pk>/delete/', views.DeleteRecipeFood.as_view(), name='delete-recipefood'),
    
    #----------------------   ??? STUFF   -----------------------------------------------
    
    
    
    #---------------------------------------------------------------------
]