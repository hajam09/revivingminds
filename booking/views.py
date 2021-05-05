from django.shortcuts import render
from accounts.models import Therapist
from accounts.models import Doctor
from django.http import Http404

def view_schedule(request, profile):
	profile_obj = None
	try:
		profile_obj = Therapist.objects.get(slug=profile)
	except Therapist.DoesNotExist:
		pass

	try:
		profile_obj = Doctor.objects.get(slug=profile)
	except Doctor.DoesNotExist:
		pass

	if profile_obj == None:
		raise Http404

	context = {}
	return render(request, "booking/view_booking_schedule.html", context)