from accounts.models import Doctor
from accounts.models import Patient
from accounts.models import Therapist
from booking.models import Appointment
from booking.models import Session
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
import random
import string

def view_schedule(request, profile):
	if not request.session.session_key:
		request.session.save()

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

	if request.method == "POST" and 'create-appointment-for-unauthenticated-user' in request.POST:
		email = request.POST['email']
		session_name = request.POST['event-name']
		if User.objects.filter(email=email).exists():
			# redirect to login page
			pass

		# for this doctor or therapist get the consultation session for pricing
		if(isinstance(profile_obj, Doctor)):
			if 'single-event' in request.POST:
				# booking a single appointment.
				get_session = Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name, quantity=1)
				if get_session.exists():

					new_session = get_session[0]
					start_time = request.POST['edate']
					duration = request.POST['duration']

					cacheData = {
						"consultant": 'doctor',
						"consultant_id": profile_obj.pk,
						"patient_email": email,
						"event_type": 'single-event',
						"session_id":new_session.pk,
						"start_time": start_time,
						"duration": duration,
					}

					if not Appointment.objects.filter(doctor=profile_obj, start_time=start_time).exists():
						cache.set(request.session.session_key, cacheData, 600)
						# set this object in the cache for 5 minutes.
						return redirect('payment:landing-page')
			else:
				# bulk booking with doctor.
				pass

		elif(isinstance(profile_obj, Therapist)):
			if 'single-event' in request.POST:
				# booking a single appointment.
				get_session = Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name, quantity=1)
				if get_session.exists():

					new_session = get_session[0]
					start_time = request.POST['edate']
					duration = request.POST['duration']

					cacheData = {
						"consultant": 'therapist',
						"consultant_id": profile_obj.pk,
						"patient_email": email,
						"event_type": 'single-event',
						"session_id":new_session.pk,
						"start_time": start_time,
						"duration": duration,
					}

					if not Appointment.objects.filter(therapist=profile_obj, start_time=start_time).exists():
						cache.set(request.session.session_key, cacheData, 600)
						return redirect('payment:landing-page')
			else:
				# bulk-booking with therapist
				pass

	return render(request, "booking/view_booking_schedule.html")