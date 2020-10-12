import decimal

from django.db import models
from django.db.models.functions import Floor
from django.contrib.auth.models import User

# for display purposes
# chops off extra zeros if unnecessary
def chop_zeros(value):
	if value == value.to_integral():
		return value.quantize(decimal.Decimal(1))
	else:
		return value.normalize()

#food model for database
class Food(models.Model):
	#id auto generated (egg is 1 broccoli is 2)
	name = models.CharField(max_length=50)
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
	gender = models.CharField(max_length=1)
	birthdate = models.DateField()
	height = models.DecimalField(max_digits=5, decimal_places=2)
	weight = models.DecimalField(max_digits=5, decimal_places=2)
	showmetric = models.BooleanField()
    
    
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
#Reporting the consumption of a food. At this time only one food at a time, but in the future it might have a different table for each food attached to the eatreport.
class EatReport(models.Model):
	#many to one with users and with food
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    food = models.ForeignKey(Food, on_delete = models.CASCADE)
    portion = models.DecimalField(max_digits=3, decimal_places=2)
    timestamp = models.DateTimeField()
    
    #currently just gets the associated user
    def __str__(self):
    	return self.user.username + ", " + self.food.name + " x" + self.portion + ", " + self.timestamp

# User's allergies. In the future maybe this should be related to profile instead of user.
class Allergy(models.Model):
    users = models.ManyToManyField(User, blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name
        
    class Meta:
        # correct spelling of plural form of allergy
        verbose_name_plural = "Allergies"

# Dietary preferences i.e vegetarian, pescatarian, keto, etc. Similar to allergies.
class DietPreference(models.Model):
    users = models.ManyToManyField(User, blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name

# daily log of meals
class DailyLog(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField()

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
	log_time = models.DateTimeField()
	daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.log_time)

# meal food model that contains key to meal log, key to food, and portion size
class MealFood(models.Model):
	meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE)
	food = models.ForeignKey(Food, on_delete=models.CASCADE)
	portions = models.DecimalField(max_digits=5, decimal_places=2)

	def __str__(self):
		return self.food.name
