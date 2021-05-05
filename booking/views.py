from django.shortcuts import render
from accounts.models import Therapist
from accounts.models import Doctor
from django.http import Http404

def view_schedule(request, profile):
	try:
		profile = Therapist.objects.get(slug=profile)
	except Therapist.DoesNotExist:
		raise Http404

	context = {}
	return render(request, "booking/view_booking_schedule.html", context)