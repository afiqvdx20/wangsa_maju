from django.contrib.auth.models import Permission, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Car(models.Model):
	title   	= models.CharField(max_length=200)
	price  		= models.CharField(max_length=100)
	bodytype  	= models.CharField(max_length=100)
	seatnumber  = models.CharField(max_length=100)
	transmission  = models.CharField(max_length=100)
	cc_car  = models.CharField(max_length=100)
	car_img  = models.FileField()

	def __str__(self):
		return self.title

class Myrating(models.Model):
	user   	= models.ForeignKey(User,on_delete=models.CASCADE)
	car 	= models.ForeignKey(Car,on_delete=models.CASCADE)
	rating 	= models.IntegerField(default=1,validators=[MaxValueValidator(5),MinValueValidator(0)])
