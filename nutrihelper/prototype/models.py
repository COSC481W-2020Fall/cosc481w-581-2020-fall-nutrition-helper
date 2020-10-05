import decimal

from django.db import models
from django.db.models.functions import Floor
from django.contrib.auth.models import User

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

	# for display purposes
	# chops off extra zeros if unnecessary
	def chop_zeros(self, value):
		if value == value.to_integral():
			return value.quantize(decimal.Decimal(1))
		else:
			return value.normalize()

	# returns dictionary containing nutrient data fields
	def get_facts(self):
		return {
			'name':self.name,
			'servingSize':self.chop_zeros(self.servingSize),
			'calories':self.calories,
			'totalFat':self.chop_zeros(self.totalFat),
			'cholesterol':self.chop_zeros(self.cholesterol),
			'sodium':self.chop_zeros(self.sodium),
			'totalCarb':self.chop_zeros(self.totalCarb),
			'protein':self.chop_zeros(self.protein)
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

	# chops off extra zeros if unnecessary for display
    def chop_zeros(self, value):
        if value == value.to_integral():
            return value.quantize(decimal.Decimal(1))
        else:
            return value.normalize()

    def get_imperial_weight(self):
        return self.weight * 2.2046

    def get_imperial_height(self):
        return self.height * 3.28084

    def get_imperial_feet_and_inches(self):
        feet = Floor(self.get_imperial_height())
        inches = (self.get_imperial_height() - feet) * 12
        return {
                'feet':feet,
                'inches': inches
        }
    
    
    # returns dictionary containing nutrient data fields
    def get_metric_profile(self):
        return {
            'user':self.user,
            'gender':self.gender,
            'birthdate':self.birthdate,
            'height':self.chop_zeros(self.height),
            'weight':self.chop_zeros(self.weight),
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

