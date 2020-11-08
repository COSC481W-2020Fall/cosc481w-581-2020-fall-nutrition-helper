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

i = 56

for i in range(60055):
    food = foods[i]
    factor = food.servingSize / 100
    totalFat = food.totalFat*factor
    cholesterol = food.cholesterol*factor
    sodium = food.sodium*factor
    totalCarb = food.totalCarb*factor
    protein = food.protein*factor
    calories = int(protein*Decimal(4.27) + totalFat*Decimal(8.79) + totalCarb*Decimal(3.87))
    food.totalFat = totalFat
    food.cholesterol = cholesterol
    food.sodium = sodium
    food.totalCarb = totalCarb
    food.protein = protein
    food.calories = calories
    food.save()
    