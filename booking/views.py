from django.shortcuts import render
from accounts.models import Therapist
from accounts.models import Doctor
from django.contrib.auth.models import User
from django.http import Http404
from booking.models import Session
from booking.models import Appointment
from datetime import datetime
from datetime import timedelta
from django.shortcuts import redirect
from django.core.cache import cache

def view_schedule(request, profile):
	if not request.session.session_key:
		request.session.save()
	print(request.session.session_key)
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
		# redirect user to the payment page
		if(isinstance(profile_obj, Doctor)):
			if 'single-event' in request.POST:
				# booking a single appointment.
				if(Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name, quantity=1).exists()):

					new_session = Session.objects.filter(doctor=profile_obj, session_name__iexact=session_name)[0]
					start_time = request.POST['edate']
					duration = request.POST['duration']

					if not Appointment.objects.filter(doctor=profile_obj, start_time=start_time).exists():
						new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
						new_end_time = new_start_time + timedelta(minutes = int(duration))
						new_appointment = Appointment(
								doctor=profile_obj,
								start_time=new_start_time,
								end_time=new_end_time,
								session_type=new_session,
								zoom_link=''
							)
						cache.set(request.session.session_key, [new_appointment], 300)
						# set this object in the cache for 5 minutes.
						return redirect('payment:landing-page')

		elif(isinstance(profile_obj, Therapist)):
			if 'single-event' in request.POST:
				# booking a single appointment.
				if(Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name, quantity=1).exists()):

					new_session = Session.objects.filter(therapist=profile_obj, session_name__iexact=session_name)[0]
					start_time = request.POST['edate']
					duration = request.POST['duration']

					if not Appointment.objects.filter(therapist=profile_obj, start_time=start_time).exists():
						new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
						new_end_time = new_start_time + timedelta(minutes = int(duration))
						new_appointment = Appointment(
								therapist=profile_obj,
								start_time=new_start_time,
								end_time=new_end_time,
								session_type=new_session,
								zoom_link=''
							)
						cache.set(request.session.session_key, [new_appointment], 300)
						# set this object in the cache for 5 minutes.
						return redirect('payment:landing-page')

	return render(request, "booking/view_booking_schedule.html")