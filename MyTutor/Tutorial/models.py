from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        myuser = MyUser.objects.get(wallet = self)
        return myuser.user.username + "'s wallet"


"""class User(models.Model):
    user_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    #tutorial_session = models.CharField(max_length=336)
    wallet = models.ForeignKey(Wallet, on_delete = models.CASCADE)
    def __str__(self):
        return self.name"""

class MyUser(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE )
    wallet = models.ForeignKey(Wallet, on_delete = models.CASCADE)
    def __str__(self):
        return self.user.username

class Student(models.Model):
    myuser = models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    def __str__(self):
        if self.myuser is None:
            return "null"
        else:
            return self.myuser.user.username

class Tutor(models.Model):
    myuser = models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    timeslot = models.CharField(max_length=336) #todo: should update every half an hour
    # 0-unavailable, 1-available, half an hour per digit, 336 timeslots is a week
    def __str__(self):
        if self.myuser is None:
            return "null"
        else:
            return self.myuser.user.username

class PrivateTutor(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	hourly_rate = models.IntegerField()
	def __str__(self):
		return self.tutor.myuser.user.username

class ContractedTutor(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	hourly_rate = 0
	def __str__(self):
		return self.tutor.myuser.user.username

class Notification(models.Model):
    content = models.CharField(max_length=500)
    myuser = models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    def __str__(self):
        if self.myuser is None:
            return "null"
        else:
            return self.myuser.user.username
class TutorialSession(models.Model):
    starttime = models.CharField(max_length=12)  # yyyymmddhhmm
    status = models.IntegerField()
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student =  models.ForeignKey(Student, on_delete=models.CASCADE)
    def __str__(self):
        return self.starttime + "-student-" + self.student.myuser.user.username + "-tutor-" + self.tutor.myuser.user.username
"""
status map:
0   upcoming can cancel
1   upcoming cannot cancel
2   attended
3   cancelled
4   evaluated
"""
