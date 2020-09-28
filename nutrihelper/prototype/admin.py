from django.contrib import admin

from .models import Food

# registers the Food model in the admin site

admin.site.register(Food)
