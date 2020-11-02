from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User
from nutrihacker.models import DailyLog, MealLog, MealFood, Food

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

# creates a log with three meals (2:3:3 number of foods)
def create_one_log(client):
	create_foods()
	user = login_user(client)
	now = datetime.now().replace(second=0, microsecond=0)

	client.post(
		reverse('nutrihacker:log_create'),
		{
			'date':now.date(),
			'time':now.time(),
			'food1':Food.objects.get(id=1).id,
			'portions1':Decimal('1.1'),
			'food2':Food.objects.get(id=2).id,
			'portions2':Decimal('1.2'),
			'extra_field_count':1
		}
	)
	client.post(
		reverse('nutrihacker:log_create'),
		{
			'date':now.date(),
			'time':now.time(),
			'food1':Food.objects.get(id=3).id,
			'portions1':Decimal('1.3'),
			'food2':Food.objects.get(id=4).id,
			'portions2':Decimal('1.4'),
			'food3':Food.objects.get(id=5).id,
			'portions3':Decimal('1.5'),
			'extra_field_count':2
		}
	)
	client.post(
		reverse('nutrihacker:log_create'),
		{
			'date':now.date(),
			'time':now.time(),
			'food1':Food.objects.get(id=6).id,
			'portions1':Decimal('1.6'),
			'food2':Food.objects.get(id=7).id,
			'portions2':Decimal('1.7'),
			'food3':Food.objects.get(id=8).id,
			'portions3':Decimal('1.8'),
			'extra_field_count':2
		}
	)

	return user, now

class LogCreateTests(TestCase):
	# tests successful creation of a log using DailyLog, MealLog, and MealFood 
	def test_create_log(self):
		create_foods()
		user = login_user(self.client)
		now = datetime.now().replace(second=0, microsecond=0)
		
		# test creating a log with one food
		food1 = Food.objects.get(id=1)
		portions1 = Decimal('1.5')
		response = self.client.post(
			reverse('nutrihacker:log_create'),
			{
				'date':now.date(),
				'time':now.time(),
				'food1':food1.id,
				'portions1':portions1,
				'extra_field_count':0
			},
			follow=True
		)
		
		# confirm that the correct logs were created and user redirected to correct page
		self.assertQuerysetEqual(DailyLog.objects.all(), ['<DailyLog: ' + str(now.date()) + '>'])
		self.assertQuerysetEqual(MealLog.objects.all(), ['<MealLog: ' + str(now) + '>'])
		self.assertQuerysetEqual(MealFood.objects.all(), ['<MealFood: ' + str(now) + ' ' + food1.name + '>'])
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':1})))
		
		# test creating another MealLog of multiple foods for the same day
		food2 = Food.objects.get(id=2)
		portions2 = Decimal('1')
		food3 = Food.objects.get(id=3)
		portions3 = Decimal('0.75')
		food4 = Food.objects.get(id=4)
		portions4 = Decimal('2.5')
		response = self.client.post(
			reverse('nutrihacker:log_create'),
			{
				'date':now.date(),
				'time':now.time(),
				'food1':food2.id,
				'portions1':portions2,
				'food2':food3.id,
				'portions2':portions3,
				'food3':food4.id,
				'portions3':portions4,
				'extra_field_count':2
			},
			follow=True
		)

		# builds a list that mimics a QuerySet
		mealfood_qs = []
		for i in range(4):
			mealfood_qs.append('<MealFood: ' + str(now) + ' ' + Food.objects.get(id=i+1).name + '>')

		# confirm that the correct logs were created and user redirected to correct page
		self.assertQuerysetEqual(DailyLog.objects.all(), ['<DailyLog: ' + str(now.date()) + '>'])
		self.assertQuerysetEqual(MealLog.objects.all(), ['<MealLog: ' + str(now) + '>',
														 '<MealLog: ' + str(now) + '>'], ordered=False)
		self.assertQuerysetEqual(MealFood.objects.all(), mealfood_qs, ordered=False)
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':1})))
		
	# tests invalid future dates and times
	def test_create_future_log_not_allowed(self):
		create_foods()
		user = login_user(self.client)
		now = datetime.now().replace(second=0, microsecond=0)

		food1 = Food.objects.get(id=1)
		portions1 = Decimal('1.5')
		
		# test creating a log 30 minutes in the future
		future1 = now + timedelta(minutes=30)
		response = self.client.post(
			reverse('nutrihacker:log_create'),
			{
				'date':now.date(),
				'time':future1.time(),
				'food1':food1.id,
				'portions1':portions1,
				'extra_field_count':0
			},
			follow=True
		)

		# confirm that no logs were created and an error was raised
		self.assertQuerysetEqual(DailyLog.objects.all(), [])
		self.assertQuerysetEqual(MealLog.objects.all(), [])
		self.assertQuerysetEqual(MealFood.objects.all(), [])
		self.assertEqual(response.status_code, 200)

		# test creating a log 1 day in the future
		future2 = now + timedelta(days=1)
		response = self.client.post(
			reverse('nutrihacker:log_create'),
			{
				'date':future2.date(),
				'time':now.time(),
				'food1':food1.id,
				'portions1':portions1,
				'extra_field_count':0
			},
			follow=True
		)

		# confirm that no logs were created and an error was raised
		self.assertQuerysetEqual(DailyLog.objects.all(), [])
		self.assertQuerysetEqual(MealLog.objects.all(), [])
		self.assertQuerysetEqual(MealFood.objects.all(), [])
		self.assertEqual(response.status_code, 200)


class LogUpdateTests(TestCase):
	def test_update_log_date_time(self):
		user, now = create_one_log(self.client)
		
		# test updating a log to 30 minutes in the past
		past1 = now - timedelta(minutes=30)
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':1}),
			{
				'date':now.date(),
				'time':past1.time(),
				'food1':Food.objects.get(id=1).id,
				'portions1':Decimal('1.1'),
				'food2':Food.objects.get(id=2).id,
				'portions2':Decimal('1.2'),
				'extra_field_count':1
			},
			follow=True
		)

		# confirm that MealLog time was changed and user redirected to correct page
		self.assertQuerysetEqual(MealLog.objects.filter(id=1), ['<MealLog: ' + str(past1) + '>'])
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':1})))

		# test updating a log to 1 day in the past
		past2 = now - timedelta(days=1)
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':2}),
			{
				'date':past2.date(),
				'time':now.time(),
				'food1':Food.objects.get(id=3).id,
				'portions1':Decimal('1.3'),
				'food2':Food.objects.get(id=4).id,
				'portions2':Decimal('1.4'),
				'food3':Food.objects.get(id=5).id,
				'portions3':Decimal('1.5'),
				'extra_field_count':2
			},
			follow=True
		)

		# confirm that a new DailyLog was created, MealLog date was changed, and user redirected to correct page
		self.assertQuerysetEqual(DailyLog.objects.filter(id=2), ['<DailyLog: ' + str(past2.date()) + '>'])
		self.assertQuerysetEqual(MealLog.objects.filter(id=2), ['<MealLog: ' + str(past2) + '>'])
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':2})))

		# test updating a log's date to an existing DailyLog
		past3 = now - timedelta(days=2)
		dl = DailyLog.create(user, past3.date()) # create a DailyLog using past3
		dl.save()
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':3}),
			{
				'date':past3.date(),
				'time':now.time(),
				'food1':Food.objects.get(id=6).id,
				'portions1':Decimal('1.6'),
				'food2':Food.objects.get(id=7).id,
				'portions2':Decimal('1.7'),
				'food3':Food.objects.get(id=8).id,
				'portions3':Decimal('1.8'),
				'extra_field_count':2
			},
			follow=True
		)

		# confirm that MealLog date was changed to existing DailyLog, and user redirected to correct page
		self.assertQuerysetEqual(MealLog.objects.filter(id=3), ['<MealLog: ' + str(past3) + '>'])
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':dl.id})))

	def test_update_log_food_portions(self):
		user, now = create_one_log(self.client)

		# test updating by changing the food and portions for existing fields and adding more food+portions
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':1}),
			{
				'date':now.date(),
				'time':now.time(),
				'food1':Food.objects.get(id=3).id,
				'portions1':Decimal('1.3'),
				'food2':Food.objects.get(id=4).id,
				'portions2':Decimal('1.4'),
				'food3':Food.objects.get(id=5).id,
				'portions3':Decimal('1.5'),
				'food4':Food.objects.get(id=6).id,
				'portions4':Decimal('1.6'),
				'extra_field_count':3
			},
			follow=True
		)

		# builds a list that mimics a QuerySet
		mealfood_qs = []
		for i in range(4):
			mealfood_qs.append('<MealFood: ' + str(now) + ' ' + Food.objects.get(id=i+3).name + '>')

		mealfood_list = MealFood.objects.filter(meal_log__id=1) # get MealFood list for the MealLog
		portions = Decimal('1.3')
		for mealfood in mealfood_list:
			# confirm that each MealFood's portions field is correct
			self.assertEqual(mealfood.portions, portions)
			portions += Decimal('0.1')

		# confirm that MealFood list is correct, and user redirected to correct page
		self.assertQuerysetEqual(mealfood_list, mealfood_qs, ordered=False)
		self.assertRedirects(response, (reverse('nutrihacker:log_detail', kwargs={'pk':1})))

	# tests invalid future dates and times
	def test_update_to_future_date_not_allowed(self):
		user, now = create_one_log(self.client)
		
		# test updating a log to 30 minutes in the future
		future1 = now + timedelta(minutes=30)
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':1}),
			{
				'date':now.date(),
				'time':future1.time(),
				'food1':Food.objects.get(id=1).id,
				'portions1':Decimal('1.1'),
				'food2':Food.objects.get(id=2).id,
				'portions2':Decimal('1.2'),
				'extra_field_count':1
			},
			follow=True
		)

		# confirm that the MealLog time did not change and an error was raised
		self.assertQuerysetEqual(MealLog.objects.filter(id=1), ['<MealLog: ' + str(now) + '>'])
		self.assertEqual(response.status_code, 200)

		future2 = now + timedelta(days=1)
		response = self.client.post(
			reverse('nutrihacker:log_update', kwargs={'pk':1}),
			{
				'date':future2.date(),
				'time':now.time(),
				'food1':Food.objects.get(id=1).id,
				'portions1':Decimal('1.1'),
				'food2':Food.objects.get(id=2).id,
				'portions2':Decimal('1.2'),
				'extra_field_count':1
			},
			follow=True
		)

		# confirm that no DailyLog was created, MealLog date did not change, and an error was raised
		self.assertQuerysetEqual(DailyLog.objects.all(), ['<DailyLog: ' + str(now.date()) + '>'])
		self.assertQuerysetEqual(MealLog.objects.filter(id=1), ['<MealLog: ' + str(now) + '>'])
		self.assertEqual(response.status_code, 200)


class LogModelTests(TestCase):
	# tests the get_total function for DailyLog, MealLog, MealFood
	# DL's get_total is dependent on ML's which is dependent on MF's, so testing DL's means testing all of them
	def test_get_total(self):
		create_one_log(self.client)

		dl = DailyLog.objects.get(id=1)

		total = {
			'calories':0,
			'totalFat':0,
			'cholesterol':0,
			'sodium':0,
			'totalCarb':0,
			'protein':0
		}

		# calculate the total nutrients for the daily log
		portions = Decimal('1.1')
		for mf in MealFood.objects.all():
			# get the nutrients of each food
			nutrients = mf.food.get_nutrients()
			# add the nutrients multiplied by portions
			for key in total:
				total[key] += nutrients[key] * portions
			# increment portions as they were hardcoded
			portions += Decimal('0.1')

		# test the get_total calculation against hardcoded calculation
		self.assertEqual(dl.get_total(), total)
		
