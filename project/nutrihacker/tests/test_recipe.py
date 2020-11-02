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
		portions1 = Decimal('1.5')
		response = self.client.post(
			reverse('nutrihacker:record_recipe'),
			{'name':name, 'servingsProduced':servingsProduced, 'instruction':instruction, 'food1':food1.id, 'portions1':portions1, 'extra_field_count':0},
			follow=False
		)
		
		
		self.assertQuerysetEqual(User.objects.all(), ['<User: test>'])
		self.assertQuerysetEqual(Recipe.objects.all(), ['<Recipe: ' + 'test\'s ' + name + '>'])
		self.assertQuerysetEqual(RecipeFood.objects.all(), ['<RecipeFood: ' + 'test\'s ' + name + ' - ' + food1.name + ', ' + str(portions1) + '>'])
		
		
		
		name2 = "Yodel Syrup"
		instruction2 = "Gargle syrup and spit into a crystal goblet"
		servingsProduced2 = Decimal('1.5')
		
		# test creating another meal log of multiple foods for the same day
		food2 = Food.objects.get(id=2)
		portions2 = Decimal('1')
		food3 = Food.objects.get(id=3)
		portions3 = Decimal('0.75')
		food4 = Food.objects.get(id=4)
		portions4 = Decimal('2.5')
		response = self.client.post(
			reverse('nutrihacker:record_recipe'),
			{'name':name2, 'servingsProduced':servingsProduced2, 'instruction':instruction2, 'food1':food2.id, 'portions1':portions2, 'food2':food3.id, 'portions2':portions3,
			'food3':food4.id, 'portions3':portions4, 'extra_field_count':2},
			follow=True
		)

		# builds a list that mimics a QuerySet
		recipefood_qs = []
		for i in range(4):
			recipefood_qs.append(['<RecipeFood: ' + 'test\'s ' + name + ' - ' + Food.objects.get(id=i+1).name + ', ' + Food.objects.get(id=i+1).portions + '>'])

		self.assertQuerysetEqual(Recipe.objects.all(), ['<Recipe: ' + 'test\'s ' + name + '>', '<Recipe: ' + 'test\'s ' + name + '>'], ordered=False)
		self.assertQuerysetEqual(RecipeFood.objects.all(), recipefood_qs, ordered=False)
		
	# # tests invalid future dates and times
	# def test_future_log_not_allowed(self):
		# create_foods()
		# user = login_user(self.client)
		# now = datetime.now().replace(second=0, microsecond=0)

		# food1 = Food.objects.get(id=1)
		# portions1 = Decimal('1.5')
		
		# # test creating a daily log and meal log 30 minutes in the future
		# now1 = now + timedelta(minutes=30)
		# response = self.client.post(
			# reverse('nutrihacker:log'),
			# {'date':now1.date(), 'time':now1.time(), 'food1':food1.id, 'portions1':portions1, 'extra_field_count':0},
			# follow=True
		# )

		# self.assertQuerysetEqual(DailyLog.objects.all(), [])
		# self.assertQuerysetEqual(MealLog.objects.all(), [])
		# self.assertQuerysetEqual(MealFood.objects.all(), [])
		# self.assertEqual(response.status_code, 200)

		# # test creating a daily log and meal log 1 day in the future
		# now2 = now + timedelta(days=1)
		# response = self.client.post(
			# reverse('nutrihacker:log'),
			# {'date':now2.date(), 'time':now2.time(), 'food1':food1.id, 'portions1':portions1, 'extra_field_count':0},
			# follow=True
		# )

		# self.assertQuerysetEqual(DailyLog.objects.all(), [])
		# self.assertQuerysetEqual(MealLog.objects.all(), [])
		# self.assertQuerysetEqual(MealFood.objects.all(), [])
		# self.assertEqual(response.status_code, 200)

	# # tests the get_total function for DailyLog, MealLog, MealFood
	# # DL's get_total is dependent on ML's which is dependent on MF's, so testing DL's means testing all of them
	# def test_get_total(self):
		# create_foods()
		# user = login_user(self.client)
		# now = datetime.now().replace(second=0, microsecond=0)

		# # create a daily log with meal logs and meal foods
		# dl = DailyLog.objects.create(user=user, date=now.date())
		# ml1 = MealLog.objects.create(log_time=now.time(), daily_log=dl)
		# MealFood.objects.create(meal_log=ml1, food=Food.objects.get(id=1), portions=Decimal('1.1'))
		# MealFood.objects.create(meal_log=ml1, food=Food.objects.get(id=2), portions=Decimal('1.2'))
		# ml2 = MealLog.objects.create(log_time=now.time(), daily_log=dl)
		# MealFood.objects.create(meal_log=ml2, food=Food.objects.get(id=3), portions=Decimal('1.3'))
		# MealFood.objects.create(meal_log=ml2, food=Food.objects.get(id=4), portions=Decimal('1.4'))
		# MealFood.objects.create(meal_log=ml2, food=Food.objects.get(id=5), portions=Decimal('1.5'))
		# ml3 = MealLog.objects.create(log_time=now.time(), daily_log=dl)
		# MealFood.objects.create(meal_log=ml3, food=Food.objects.get(id=6), portions=Decimal('1.6'))
		# MealFood.objects.create(meal_log=ml3, food=Food.objects.get(id=7), portions=Decimal('1.7'))
		# MealFood.objects.create(meal_log=ml3, food=Food.objects.get(id=8), portions=Decimal('1.8'))

		# total = {
			# 'calories':0,
			# 'totalFat':0,
			# 'cholesterol':0,
			# 'sodium':0,
			# 'totalCarb':0,
			# 'protein':0
		# }

		# # calculate the total nutrients for the daily log
		# portions = Decimal('1.1')
		# for mf in MealFood.objects.all():
			# # get the nutrients of each food
			# nutrients = mf.food.get_nutrients()
			# # add the nutrients multiplied by portions
			# for key in total:
				# total[key] += nutrients[key] * portions
			# # increment portions as they were hardcoded
			# portions += Decimal('0.1')

		# # test the get_total calculation against hardcoded calculation
		# self.assertEqual(dl.get_total(), total)
		
