from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from accounts.models import Patient
from accounts.models import Therapist
from accounts.models import Doctor

class Session(models.Model):
	"""
		think of: the "consultation" session with "therapist" would cost "10.00" for "1" session/quantity where you can book for "30 mins"
	"""
	session_name = models.CharField(max_length=255)
	therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, blank=True, null=True)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True, null=True)
	cost = models.IntegerField()
	quantity = models.IntegerField()# number of recurring session
	max_mins = models.IntegerField()# max number of minutes the session can last.

	def __str__(self):
		return "{}, {}, {}".format(self.session_name, self.cost, self.quantity)

	def get_display_price(self):
		return "{0:.2f}".format(self.cost / 100)

	def mins_to_hrs(self):
		hours = self.max_mins // 60
		minutes = self.max_mins % 60
		return "{}:{} {}".format(hours, minutes, "Hrs")


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
	patients = models.ManyToManyField(Patient, related_name='appointment_participants') # check with this
	# appointment can be with either therapist or doctor. set null when dealting with other
	therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, blank=True, null=True)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True, null=True)
	start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
	session_type = models.ForeignKey(Session, on_delete=models.CASCADE)
	zoom_link = models.URLField(max_length=500)