from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from booking.models import Session

class Payment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	payment_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	payment_status = models.CharField(max_length=255) # Approved, Pending or Rejected
	paymentID = models.CharField(max_length=255) # Genereated by django uuid incase if patient raises a dispute.
	session_type = models.ForeignKey(Session, on_delete=models.PROTECT, blank=True, null=True)
	amount = models.DecimalField(max_digits=5, decimal_places=2)