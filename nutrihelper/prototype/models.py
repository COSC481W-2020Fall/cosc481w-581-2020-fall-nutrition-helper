import decimal

from django.db import models

#food model for database
class Food(models.Model):
	#id auto generated (egg is 1 broccoli is 2)
	name = models.CharField(max_length=50)
	servingSize = models.DecimalField(max_digits=5, decimal_places=2)
	calories = models.IntegerField()
	totalFat = models.DecimalField(max_digits=5, decimal_places=2)
	cholesterol = models.DecimalField(max_digits=5, decimal_places=2)
	sodium = models.DecimalField(max_digits=5, decimal_places=2)
	totalCarb = models.DecimalField(max_digits=5, decimal_places=2)
	protein = models.DecimalField(max_digits=5, decimal_places=2)
	
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
	