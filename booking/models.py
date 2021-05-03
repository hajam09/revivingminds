from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from accounts.models import Patient
from accounts.models import Therapist

class Session(models.Model):
	session_name = models.CharField(max_length=255)
	cost = models.DecimalField(max_digits=5, decimal_places=2)
	quantity = models.IntegerField()# number of recurring session

"""
reason I made quantity with sesion is coz with bulk session booking there is discount price.
e.g 

consultation, £50, 1
theraphy, £100, 1
theraphy, £290, 2
theraphy, £380, 3
... something like this.
"""


class Appointment(models.Model):
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	#OR
	participants = models.ManyToManyField(Patient, related_name='appointment_participants') # check with this
	therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
	start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	session_type = models.ForeignKey(Session, on_delete=models.CASCADE)
	zoom_link = models.URLField(max_length=500)
	