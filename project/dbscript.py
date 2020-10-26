##Script for adding foods into database from the csv files obtained from the usda database.

#required setup for django to run this script
import sys, os
sys.path.insert(0, "cosc481w-581-2020-fall-nutrition-helper")
from manage import DEFAULT_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
import django
django.setup()

#Reading an excel file using pandas you may need to install it - pip install pandas
import pandas as pd
from nutrihacker.models import Food, BrandedIds
from decimal import Decimal

#Storing branded ids
brandLoc = ("C:/Users/Johnny/usda data/branded_food.csv")
brandSheet = pd.read_csv(brandLoc, low_memory=False, memory_map=True)

foodLoc = ("C:/Users/Johnny/usda data/food.csv")
foodSheet = pd.read_csv(foodLoc, low_memory=False, memory_map=True, nrows=60002)

nutrientLoc = ("C:/Users/Johnny/usda data/food_nutrient.csv")
nutrientSheet = pd.read_csv(nutrientLoc, low_memory=False, memory_map=True, nrows=841514)

#adding fdc_ids into a table to use later

#last fcd id added 354603 -- 404604

#50000 number of ids to get from excel sheet
numberOfItemsToAdd = 50000
#number of item already in db update this after items are added
currentNumberOfItems = 10000

for i in range(numberOfItemsToAdd):

    
    idToStore = BrandedIds(fdcIds = int(brandSheet['fdc_id'].values[i+currentNumberOfItems]))
    idToStore.save()

#default values
name = "nothing"
servingSize = Decimal(0)
calories = 0
cholesterol = Decimal(0)
sodium = Decimal(0)
totalCarb = Decimal(0)
protein = Decimal(0)
totalFat = Decimal(0)

#these are used to stop the loop from going through every single row and pick up again at the place it stopped. will need to be updated after code is run
jOffset = 10000
offset = 169700

#the range is the number of items being added

#50000 change this the change the number of items to add must also change in next for loop
for i in range(numberOfItemsToAdd):      
    fdcId = BrandedIds.objects.get(id=i+(currentNumberOfItems+1)).fdcIds
    
    #checking to make sure both name and serving size have been set
    ssa = False
    na = False
    
    j = 0 + jOffset
    
    #getting name and serving size from food.csv
    while j <= 60002:       #This is the number of rows grabbed from the sheet use the fcd ids to 
        if fdcId == int(foodSheet['fdc_id'].values[j]):
            name = str(foodSheet['description'].values[j])
            na = True
        if fdcId == int(brandSheet['fdc_id'].values[j]):
            servingSize = Decimal(brandSheet['serving_size'].values[j])
            ssa = True
        if(na and ssa):
            jOffset += 1
            break
        j+=1
    
    #nutrient ids we need are cholesterol-1253 protein-1003 carbohydrate-1005 sodium-1093 fat-1004
    #calories obtained through calorie conversion factor protein*4.27 fat*8.79 carbohydrate*3.87
    
    start = False
    
    x = 0 + offset
    
    #getting nutrition numbers from food_nutrient.csv
    while x <= 841514:      #number of rows
        if fdcId == int(nutrientSheet['fdc_id'].values[x]):
            start = True
            if int(nutrientSheet['nutrient_id'].values[x]) == 1253:
                cholesterol = Decimal(nutrientSheet['amount'].values[x])
            if int(nutrientSheet['nutrient_id'].values[x]) == 1003:
                protein = Decimal(nutrientSheet['amount'].values[x])
            if int(nutrientSheet['nutrient_id'].values[x]) == 1005:
                totalCarb = Decimal(nutrientSheet['amount'].values[x])
            if int(nutrientSheet['nutrient_id'].values[x]) == 1093:
                sodium = Decimal(nutrientSheet['amount'].values[x])
            if int(nutrientSheet['nutrient_id'].values[x]) == 1004:
                totalFat = Decimal(nutrientSheet['amount'].values[x])
        elif start and fdcId != int(nutrientSheet['fdc_id'].values[x]):
            calories = int(protein*Decimal(4.27) + totalFat*Decimal(8.79) + totalCarb*Decimal(3.87))
            break
        
        offset += 1
        x += 1
    
    #adding foods to our table
    foodToStore = Food(name = name, servingSize = servingSize, calories=calories, cholesterol=cholesterol, sodium = sodium, totalCarb = totalCarb, protein = protein, totalFat = totalFat)
    foodToStore.save()

