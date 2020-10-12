from django.contrib import admin


from .models import Food, Profile, Allergy, DietPreference, DailyLog, MealLog, MealFood, EatReport


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

# registers the Profile model in the admin site
admin.site.register(EatReport)


# Register your models here.
class RecipeAdmin(admin.ModelAdmin):
    pass


# Register your models here.
class RecipeFoodAdmin(admin.ModelAdmin):
    pass