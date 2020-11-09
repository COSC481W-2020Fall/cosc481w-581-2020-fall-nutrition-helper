from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import Recipe, RecipeFood, Food

# populates temp database
def create_foods():
	foods = {
		'sweetroll': ['Sweetroll', Decimal('38.20'), Decimal('200.00'), Decimal('5.40'), Decimal('10.00'), Decimal('0.00'),
			Decimal('14.00'), Decimal('1.10')
		],
		'mubcrablegs': ['Mudcrab Legs', Decimal('54.90'), Decimal('150.00'), Decimal('2.10'), Decimal('340.00'), Decimal('20.00'),
			Decimal('2.00'), Decimal('9.00')
		],
		'eidarcheese': ['Eidar Cheese', Decimal('100.00'), Decimal('90.00'), Decimal('80.00'), Decimal('70.00'), Decimal('60.00'),
			Decimal('50.00'), Decimal('40.00')
		],
		'soulhusk': ['Soul Husk', Decimal('10.00'), Decimal('20.00'), Decimal('30.00'), Decimal('40.00'), Decimal('50.00'),
			Decimal('60.00'), Decimal('70.00')
		],
		'mammothsteak': ['Mammoth Steak', Decimal('20.00'), Decimal('40.00'), Decimal('60.00'), Decimal('80.00'), Decimal('100.00'),
			Decimal('120.00'), Decimal('140.00')
		],
		'horkerstew': ['Horker Stew', Decimal('110.00'), Decimal('120.00'), Decimal('130.00'), Decimal('140.00'), Decimal('150.00'),
			Decimal('160.00'), Decimal('170.00')
		],
		'garlicbread': ['Garlic Bread', Decimal('77.70'), Decimal('66.60'), Decimal('55.50'), Decimal('44.40'), Decimal('33.30'),
			Decimal('22.20'), Decimal('11.10')
		],
		'spicedwine': ['Spiced Wine', Decimal('100.00'), Decimal('98.00'), Decimal('86.00'), Decimal('74.00'), Decimal('62.00'),
			Decimal('50.00'), Decimal('48.00')
		],
	}

	for key in foods:
		Food.objects.create(
			name=foods[key][0],
			servingSize=foods[key][1],
			calories=foods[key][2],
			totalFat=foods[key][3],
			cholesterol=foods[key][4],
			sodium=foods[key][5],
			totalCarb=foods[key][6],
			protein=foods[key][7]
		)
		
		

# creates and logs in a user
def login_user(client):
	name = 'test'
	pword = 'djangotest159'
	user = User.objects.create_user(name, password=pword)
	client.login(username=name, password=pword)
	return user

class RecipeTests(TestCase):
	# tests successful creation of daily log and related models
	def test_create_recipe(self):
		create_foods()
		user = login_user(self.client)
		name = "Hotdog Helicopter"
		instruction = "Build a helicopter out of hot dogs"
		servingsProduced = Decimal('4.0')
		
		# test creating a daily log and meal log of one food
		food1 = Food.objects.get(id=1)
		portions1 = Decimal('1.50')
		response = self.client.post(
			reverse('nutrihacker:create_recipe'),
			{'name':name, 'servingsProduced':servingsProduced, 'instruction':instruction, 'food1':food1.id, 'portions1':portions1, 'extra_field_count':0},
			follow=False
		)
		
		
		self.assertQuerysetEqual(User.objects.all(), ['<User: test>'])
		self.assertQuerysetEqual(Recipe.objects.all(), ['<Recipe: ' + 'test, ' + name + '>'])
		firstRecipeFoodString = '<RecipeFood: ' + 'test, ' + name + ', ' + food1.name + ', 1.50>'
		self.assertQuerysetEqual(RecipeFood.objects.all(), [firstRecipeFoodString])
	
	
	def test_create_recipe_multi_ingredients(self):
		create_foods()
		user = login_user(self.client)
		name = "Yodel Syrup"
		instruction = "Gargle syrup and spit into a crystal goblet"
		servingsProduced = Decimal('1.5')
		
		
		# test creating another meal log of multiple foods for the same day
		food2 = Food.objects.get(id=2)
		portions2 = Decimal('1')
		food3 = Food.objects.get(id=3)
		portions3 = Decimal('0.75')
		food4 = Food.objects.get(id=4)
		portions4 = Decimal('2.5')
		
		response = self.client.post(
			reverse('nutrihacker:create_recipe'),
			{'name':name, 'servingsProduced':servingsProduced, 'instruction':instruction, 'food1':food2.id, 'portions1':portions2, 'food2':food3.id, 'portions2':portions3,
			'food3':food4.id, 'portions3':portions4, 'extra_field_count':2},
			follow=False
		)

		# builds a list that mimics a QuerySet
		recipefood_qs = []
		for i in range(3):
			recipefood_qs.append('<RecipeFood: ' + 'test, ' + name + ', ' + RecipeFood.objects.get(id=i+1).food.name + ', ' + str(RecipeFood.objects.get(id=i+1).portions) + '>')


		self.assertQuerysetEqual(Recipe.objects.all(), ['<Recipe: ' + 'test, ' + name + '>'], ordered=False)
		self.assertQuerysetEqual(RecipeFood.objects.all(), recipefood_qs, ordered=False)
