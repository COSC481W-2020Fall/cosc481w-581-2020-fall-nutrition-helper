from django.contrib import admin

from .models import Food
from .models import Profile

# registers the Food model in the admin site
admin.site.register(Food)


# registers the Profile model in the admin site
admin.site.register(Profile)