from django.contrib import admin

from .models import Food, Profile, DailyLog, MealLog, MealFood

# registers models in the admin site
admin.site.register(Food)
admin.site.register(Profile)
admin.site.register(DailyLog)
admin.site.register(MealLog)
admin.site.register(MealFood)
