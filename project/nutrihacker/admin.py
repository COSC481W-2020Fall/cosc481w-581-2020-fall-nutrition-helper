from django.contrib import admin


from .models import Food, Profile, Allergy, DietPreference, DailyLog, MealLog, MealFood


# registers models in the admin site
admin.site.register(Food)
admin.site.register(Profile)

# Allergy model
admin.site.register(Allergy)

# DietPreference model
admin.site.register(DietPreference)

admin.site.register(DailyLog)
admin.site.register(MealLog)
admin.site.register(MealFood)

