from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    def __str__(self):
        myuser = MyUser.objects.filter(wallet = self)
        if myuser.count() == 0:
            return "null"
        else:
            myuser = MyUser.objects.get(wallet = self)
            return myuser.user.username + "'s wallet"



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

class University(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.name

class Tutor(models.Model):
    myuser = models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    timeslot = models.CharField(max_length=672, default="111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111") #for private tutor todo: should update every half an hour
    # 0-unavailable, 1-available, half an hour per digit, 336 timeslots is a week
    hourly_rate = models.IntegerField(default=0) #todo: eight digit for student so can tell if he have
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True)
    def __str__(self):
        if self.myuser is None:
            return "null"
        else:
            return self.myuser.user.username
    def create(cls, username, email, password):
        user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
        tutor = cls(myuser=user)
        return tutor


class PrivateTutor(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	#hourly_rate = models.IntegerField()
	def __str__(self):
		return self.tutor.myuser.user.username

class ContractedTutor(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    #self.tutor.timeslot = '111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
	#hourly_rate = 0
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
    price = models.IntegerField(default=0) #TODO: notice that this price does not include commission fee
    #TODO: intensive change: now has done: when booking, store into price,  when cancel, check price instead of hourly rate, when end, money of price added instead of hourly rate
    def __str__(self):
        return self.starttime + "-student-" + self.student.myuser.user.username + "-tutor-" + self.tutor.myuser.user.username
class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    tutors = models.ManyToManyField(Tutor)
    def __str__(self):
        return self.name

class Transaction(models.Model):
    myuser = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    time = models.CharField(max_length=12)  # transaction time, yyyymmddhhmm
    cashflow = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) #this should be double instead of integer because deposit can be double
    information = models.ForeignKey(TutorialSession, on_delete=models.CASCADE, blank=True, null=True) #can be himself, or another user
    type = models.IntegerField()
    def __str__(self):
        if self.myuser is None:
            return "null"
        else:
            return self.myuser.user.username + "'s transaction on " + self.time
"""
type map
0   deposit
1   withdraw
2   cancel(student)
3   booking(student)
4   booking(tutor)
"""
class Course(models.Model):
    course_code = models.CharField(max_length=64, unique=True)
    tutors = models.ManyToManyField(Tutor)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    def __str__(self):
        return self.course_code

"""
status map:
0   upcoming can cancel
1   upcoming cannot cancel
2   attended(invite to evaluate)
3   cancelled
4   evaluated
5   in progress
"""

"""
booking map:
0   tutor set unavailable
1   available
2   booked
3   passed/has been within 24 hours so status cannot be changed, this is more powerful than previous three
"""

"""
type map
0   deposit
1   withdraw
2   cancel(student)
3   booking(student)
4   booking(tutor)
"""