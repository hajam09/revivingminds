from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

# class User(AbstractUser):
#     is_therapist = models.BooleanField(default=False)
#     is_patient = models.BooleanField(default=False)

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False)

class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)