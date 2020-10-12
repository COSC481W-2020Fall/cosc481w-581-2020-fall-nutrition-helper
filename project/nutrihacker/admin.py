from django.contrib import admin

from .models import Food, Profile, Allergy, DietPreference


# registers the Food model in the admin site
admin.site.register(Food)


# registers the Profile model in the admin site
admin.site.register(Profile)

# Allergy model
admin.site.register(Allergy)

# DietPreference model
admin.site.register(DietPreference)