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

	def get_facts(self):
		return {
			'name':self.name,
			'servingSize':self.servingSize,
			'calories':self.calories,
			'totalFat':self.totalFat,
			'cholesterol':self.cholesterol,
			'sodium':self.sodium,
			'totalCarb':self.totalCarb,
			'protein':self.protein
		}
	