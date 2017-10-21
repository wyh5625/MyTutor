from django.db import models

# Create your models here.
"""class User(models.Model):
    user_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.name"""

class Student(models.Model):
    user_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Tutor(models.Model):
    user_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class PrivateTutor
