from django.db import models

# Create your models here.
class Wallet(models.Model):
	balance = models.DecimalField(max_digits=10, decimal_places=2)
		
class User(models.Model):
    user_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    tutorial_session = models.CharField(max_length=336)
    wallet = models.ForeignKey(Wallet, on_delete = models.CASCADE)
    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.name

class Tutor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeslot = models.CharField(max_length=336)
    # 0-unavailable, 1-available, half an hour per digit, 336 timeslots is a week  
    def __str__(self):
        return self.user.name

"""class Tutor2(models.Model):
	#tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	hourly_rate = models.IntegerField(max_length=5)
	#def __str__(self):
		#return self.tutor.user.name
"""
class PrivateTutor(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	hourly_rate = models.IntegerField(max_length=5)
	def __str__(self):
		return self.tutor.user.name

class Notification(models.Model):
	content = models.CharField(max_length=500)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return self.user.name

		
