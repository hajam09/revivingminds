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
from django.contrib import messages
import random
from django.utils import timezone
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

	# process authenticated user
	if request.method == "POST" and request.user.is_authenticated:
		session_name = request.POST['event-name']

		# for this doctor get the session to determine pricing for a single appointment.
		if isinstance(profile_obj, Doctor) and 'single-event' in request.POST:
			get_session = Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name, quantity=1)
			start_time = request.POST['edate']
			duration = request.POST['duration']

			# session found to get the price and the slot is available to book with the doctor.
			if get_session.exists() and not Appointment.objects.filter(doctor=profile_obj, start_time=start_time).exists():
				cacheData = {
					"consultant": 'doctor',
					"consultant_id": profile_obj.pk,
					"patient_email": request.user.email,
					"event_type": 'single-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				return redirect('payment:landing-page')
			else:
				messages.add_message(request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=profile)

		# for this therapist get the session to determine pricing for a single appointment.
		if isinstance(profile_obj, Therapist) and 'single-event' in request.POST:
			get_session = Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name, quantity=1)
			start_time = request.POST['edate']
			duration = request.POST['duration']

			# session found to get the price and the slot is available to book with the therapist.
			if get_session.exists() and not Appointment.objects.filter(therapist=profile_obj, start_time=start_time).exists():
				cacheData = {
					"consultant": 'therapist',
					"consultant_id": profile_obj.pk,
					"patient_email": request.user.email,
					"event_type": 'single-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				return redirect('payment:landing-page')
			else:
				messages.add_message(request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=profile)

		# for this doctor get the session to determine pricing for a bulk appointment.
		if isinstance(profile_obj, Doctor) and 'multiple-event' in request.POST:
			quantity = request.POST['numberOfAppointments']
			get_session = Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name, quantity=quantity)
			duration = request.POST['duration']
			start_time = request.POST['edate']

			# session found to get the price for bulk-appointments.
			# no need to check if appointment slot is free for each week. Raise alert/ticket to the appropriate consultant for each overlapping appointment.
			if get_session.exists():
				cacheData = {
					"consultant": 'doctor',
					"consultant_id": profile_obj.pk,
					"patient_email": request.user.email,
					"event_type": 'multiple-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"number_of_appointments": quantity,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				return redirect('payment:landing-page')

		# for this therapist get the session to determine pricing for a bulk appointment.
		if isinstance(profile_obj, Therapist) and 'multiple-event' in request.POST:
			quantity = request.POST['numberOfAppointments']
			get_session = Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name, quantity=quantity)
			start_time = request.POST['edate']
			duration = request.POST['duration']

			# session found to get the price for bulk-appointments.
			# no need to check if appointment slot is free for each week. Raise alert/ticket to the appropriate consultant for each overlapping appointment.
			if get_session.exists():
				cacheData = {
					"consultant": 'therapist',
					"consultant_id": profile_obj.pk,
					"patient_email": request.user.email,
					"event_type": 'multiple-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"number_of_appointments": quantity,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				return redirect('payment:landing-page')

	#################################################################################################################################

	# process un-authenticated user and they cannot book bulk appointments, therefore only 'single-event'.
	if request.method == "POST" and not request.user.is_authenticated:
		email = request.POST['email']
		session_name = request.POST['event-name']

		if User.objects.filter(email=email).exists():
			# redirect to login page incase the email already exists.
			pass

		# for this doctor get the session to determine pricing for a single appointment.
		if isinstance(profile_obj, Doctor) and 'single-event' in request.POST:
			get_session = Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name, quantity=1)
			start_time = request.POST['edate']
			duration = request.POST['duration']

			# session found to get the price and the slot is available to book with the doctor.
			if get_session.exists() and not Appointment.objects.filter(doctor=profile_obj, start_time=start_time).exists():
				cacheData = {
					"consultant": 'doctor',
					"consultant_id": profile_obj.pk,
					"patient_email": email,
					"event_type": 'single-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				# return redirect('payment:landing-page')
			else:
				messages.add_message(request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=profile)


		# for this therapist get the session to determine pricing for a single appointment.
		if isinstance(profile_obj, Therapist) and 'single-event' in request.POST:
			get_session = Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name, quantity=1)
			start_time = request.POST['edate']
			duration = request.POST['duration']

			# session found to get the price and the slot is available to book with the therapist.
			if get_session.exists() and not Appointment.objects.filter(therapist=profile_obj, start_time=start_time).exists():
				cacheData = {
					"consultant": 'therapist',
					"consultant_id": profile_obj.pk,
					"patient_email": email,
					"event_type": 'single-event',
					"session_id": get_session[0].pk,
					"start_time": start_time,
					"duration": duration,
				}

				cache.set(request.session.session_key, cacheData, 600)
				# return redirect('payment:landing-page')
			else:
				messages.add_message(request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=profile)

	existing_appointments = Appointment.objects.filter(doctor=profile_obj) if isinstance(profile_obj, Doctor) else Appointment.objects.filter(therapist=profile_obj)
	therapy_sessions = Session.objects.filter(doctor=profile_obj, session_name__iexact='therapy') if isinstance(profile_obj, Doctor) else Session.objects.filter(therapist=profile_obj, session_name__iexact='therapy')

	context = {
		"existing_appointments": existing_appointments,
		"therapy_sessions": therapy_sessions
	}
	return render(request, "booking/view_booking_schedule.html", context)