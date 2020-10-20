import decimal

from django.db import models
from django.db.models.functions import Floor
from django.contrib.auth.models import User
from datetime import datetime

# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == value.to_integral():
		return value.quantize(decimal.Decimal(1))
	else:
		return value.normalize()

class RecipePreset(models.Model):
	#id auto generated
	name = models.CharField(max_length=30)
	ingredientOne = models.CharField(max_length=30)
	ingredientTwo = models.CharField(max_length=30)
	ingredientThree = models.CharField(max_length=30)
	ingredientFour = models.CharField(max_length=30)
	ingredientFive = models.CharField(max_length=30)
	ingredientSix = models.CharField(max_length=30)
	ingredientSeven = models.CharField(max_length=30)
	ingredientEight = models.CharField(max_length=30)

	def __str__(self):
		return self.name


#food model for database
class Food(models.Model):
	#id auto generated (egg is 1 broccoli is 2)
	name = models.CharField(max_length=100)
	servingSize = models.DecimalField(max_digits=8, decimal_places=2)
	calories = models.IntegerField()
	totalFat = models.DecimalField(max_digits=8, decimal_places=2)
	cholesterol = models.DecimalField(max_digits=8, decimal_places=2)
	sodium = models.DecimalField(max_digits=8, decimal_places=2)
	totalCarb = models.DecimalField(max_digits=8, decimal_places=2)
	protein = models.DecimalField(max_digits=8, decimal_places=2)
	
	#currently just gets the name
	def __str__(self):
		return self.name

	# returns dictionary containing just nutrients
	def get_nutrients(self):
		return {
			'calories':self.calories,
			'totalFat':self.totalFat,
			'cholesterol':self.cholesterol,
			'sodium':self.sodium,
			'totalCarb':self.totalCarb,
			'protein':self.protein
		}

	# returns dictionary containing nutrient data fields
	def get_facts(self):
		return {
			'name':self.name,
			'servingSize':chop_zeros(self.servingSize),
			'calories':self.calories,
			'totalFat':chop_zeros(self.totalFat),
			'cholesterol':chop_zeros(self.cholesterol),
			'sodium':chop_zeros(self.sodium),
			'totalCarb':chop_zeros(self.totalCarb),
			'protein':chop_zeros(self.protein)
		}

#User data model for database
class Profile(models.Model):
	#userdata id auto generated, but then is 1:1 with users ()
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	gender = models.CharField(max_length=1, null=True)
	birthdate = models.DateField(null=True)
	height = models.DecimalField(max_digits=5, decimal_places=2, null=True)
	weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
	showmetric = models.BooleanField(default=True)
    
    
	#currently just gets the associated user
	def __str__(self):
		return self.user.username
    
    #def get_imperial_weight(self):
     #   return self.weight * 2.2046
    
	#def get_imperial_height(self):
	#	return self.height * 3.28084
    
	#def get_imperial_feet_and_inches(self):
	#	feet = Floor(self.get_imperial_height())
	#	inches = (self.get_imperial_height() - feet) * 12
	#	return {
	#			'feet':feet,
	#			'inches': inches
	#	}
	
	
	# returns dictionary containing nutrient data fields
	def get_metric_profile(self):
		return {
			'user':self.user,
			'gender':self.gender,
			'birthdate':self.birthdate,
			'height':chop_zeros(self.height),
			'weight':chop_zeros(self.weight),
			'showmetric':self.showmetric
		}

# User's allergies. In the future maybe this should be related to profile instead of user.
class Allergy(models.Model):
    profiles = models.ManyToManyField(Profile, blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name
        
    class Meta:
        # correct spelling of plural form of allergy
        verbose_name_plural = "Allergies"

# Dietary preferences i.e vegetarian, pescatarian, keto, etc. Similar to allergies.
class DietPreference(models.Model):
    profiles = models.ManyToManyField(Profile, blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name

# daily log of meals
class DailyLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField()

	@classmethod
	def create(cls, user, date):
		daily_log = cls(user=user, date=date)
		return daily_log

	def __str__(self):
		return str(self.date)

	# function that calculates total nutrition information of the daily log
	def calc_total(self):
		total = {
			'calories':0,
			'totalFat':0,
			'cholesterol':0,
			'sodium':0,
			'totalCarb':0,
			'protein':0
		}

		# gets list of meal logs for this daily log
		meal_log_list = MealLog.objects.filter(daily_log__user__id=self.user.id)
		
		# for each meal log
		for m_log in meal_log_list:
			# gets list of meal foods in current meal log
			meal_food_list = MealFood.objects.filter(meal_log__id=m_log.id)
			
			# for each meal food
			for m_food in meal_food_list:
				# gets nutrients of current food
				nutrients = m_food.food.get_nutrients()
				
				# for each nutrient
				for key in total:
					# adds the food's nutrients times the portion size
					total[key] += nutrients[key] * m_food.portions

		# chops all unnecessary zeros
		for key in total:
			total[key] = chop_zeros(total[key])
		
		return total

# meal log that contains time and key to daily log
class MealLog(models.Model):
	log_time = models.TimeField()
	daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)

	@classmethod
	def create(cls, log_time, daily_log):
		meal_log = cls(log_time=log_time, daily_log=daily_log)
		return meal_log

	def __str__(self):
		return str(self.daily_log.date) + " " + str(self.log_time)

# meal food model that contains key to meal log, key to food, and portion size
class MealFood(models.Model):
	meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE)
	food = models.ForeignKey(Food, on_delete=models.CASCADE)
	portions = models.DecimalField(max_digits=5, decimal_places=2)

	@classmethod
	def create(cls, meal_log, food, portions):
		meal_food = cls(meal_log=meal_log, food=food, portions=portions)
		return meal_food

	def __str__(self):
		return str(self.meal_log.daily_log.date) + " " + str(self.meal_log.log_time) + " " + self.food.name

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="Custom Recipe")
    in_progress = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    
    @classmethod
    def create(cls, user):
        recipe = cls(user=user)
        return recipe
    
    def __str__(self):
        return str(self.name)
        

class RecipeFood(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    amount_unit = models.CharField(max_length=50, default="g")

    @classmethod
    def create(cls, meal_log, food, portions):
        meal_food = cls(recipe=recipe, food=food, amount=portions)
        return meal_food

    def __str__(self):
        return  self.client + " - " + self.food + ", " + self.amount + self.amount_unit
        
        

#fdcid model for database
class BrandedIds(models.Model):
    id = models.IntegerField(primary_key=True)
    fdcIds = models.IntegerField(default=0)

    #currently just gets the name
    def fdcId(self):
        return self.fdcId

