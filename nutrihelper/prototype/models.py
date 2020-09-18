from django.db import models

#food model for database
class food(models.Model):
    #id auto generated (egg is 1 broccoli is 2)
    name = models.CharField(max_length=20)
    servingSize = models.CharField(max_length=10)
    calories = models.IntegerField()
    totalFat = models.CharField(max_length=10)
    cholesterol = models.CharField(max_length=10)
    sodium = models.CharField(max_length=10)
    totalCarb = models.CharField(max_length=10)
    protein = models.CharField(max_length=10)
    
    #currently just gets the name
    def __str__(self):
        return self.name
    