##Script for adding foods into database from the csv files obtained from the usda database.

#required setup for django to run this script
import sys, os
sys.path.insert(0, "cosc481w-581-2020-fall-nutrition-helper")
from manage import DEFAULT_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
import django
django.setup()

#Reading an excel file using pandas you may need to install it - pip install pandas
from nutrihacker.models import Food, BrandedIds
from decimal import Decimal

foods = Food.objects.all()

for i in foods:
    savedOne = False
    foodsToDel = Food.objects.filter(name = i.name)
    for j in foodsToDel:
        if savedOne:
            j.delete()
        else:
            savedOne = True