from accounts.models import Doctor
from accounts.models import Patient
from accounts.models import Therapist
from booking.models import Appointment
from booking.models import Session
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from payment.models import Payment
import json
import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessView(TemplateView):
	template_name = "payment/success.html"

class CancelView(TemplateView):
	template_name = "payment/cancel.html"

class ProductLandingPageView(TemplateView):
	template_name = "payment/landing.html"

	def get(self, *args, **kwargs):
		cacheData = cache.get(self.request.session.session_key)
		if cacheData == None:
			return redirect('mainapp:nav_bar_pages', folder='healthcare', page='appointment_booking_and_prices')

		if cacheData['consultant'] == "doctor" and cacheData['event_type'] == 'single-event':
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if Appointment.objects.filter(doctor=doctor, start_time=start_time).exists():
				# just in nick of time if the appointment has been booked by some other patient while processing.
				messages.add_message(self.request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=doctor.slug)

		if cacheData['consultant'] == "therapist" and cacheData['event_type'] == 'single-event':
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if Appointment.objects.filter(therapist=therapist, start_time=start_time).exists():
				# just in nick of time if the appointment has been booked by some other patient while processing.
				messages.add_message(self.request,messages.INFO,"Unfortunately the slot has been booking by someone else. Please try another one.")
				return redirect('booking:view_schedule', profile=therapist.slug)

		# no need to check if appointments are pre-booked when applying bulk appointments.

		return super().get(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ProductLandingPageView, self).get_context_data(**kwargs)
		cacheData = cache.get(self.request.session.session_key)
		appointments = []

		duration = cacheData['duration']

		# CREATE 'Appointment' OBJECTS FOR DISPLAY ONLY AND NOT TO BE SAVED. WHICH WILL BE DONE AFTER PAYMENT IS SUCCESS.

		# authenticated user books a single appointment with the doctor.
		if self.request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'single-event':
			#cacheData = {"consultant_id": profile_obj.pk, "patient_email": request.user.email, "session_id": get_session[0].pk, "start_time": start_time, "duration": duration, }
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if not Appointment.objects.filter(doctor=doctor, start_time=start_time).exists():
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				get_session = Session.objects.get(id=cacheData['session_id'])
				appointments = [
					Appointment(
						doctor=doctor,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link=''
					)
				]

		# authenticated user books a single appointment with the therapist.	
		elif self.request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'single-event':
			# cacheData = { "consultant_id": profile_obj.pk, "patient_email": request.user.email, "session_id": get_session[0].pk, "start_time": start_time, "duration": duration, }
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if not Appointment.objects.filter(therapist=therapist, start_time=start_time).exists():
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				get_session = Session.objects.get(id=cacheData['session_id'])
				appointments = [
					Appointment(
						therapist=therapist,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link=''
					)
				]
				
		# authenticated user books bulk appointment with the doctor.	
		elif self.request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'multiple-event':
			# cacheData = {"consultant_id": profile_obj.pk, "patient_email": request.user.email, "session_id": get_session[0].pk, "start_time": [], "number_of_appointments": quantity, "duration": duration, }
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			get_session = Session.objects.get(id=cacheData['session_id'])
			start_date_and_time = cacheData['start_time']

			def getAppointmentsForDoctor( index ):
				new_start_time = datetime.strptime(start_date_and_time, '%Y-%m-%dT%H:%M:%S')
				start_dt_for_each_week = new_start_time + timedelta(weeks = index)
				end_dt_for_each_week = start_dt_for_each_week + timedelta(minutes = int(duration))
				return Appointment(
					doctor=doctor,
					start_time=start_dt_for_each_week,
					end_time=end_dt_for_each_week,
					session_type=get_session,
					zoom_link=''
				)

			appointments = [
				getAppointmentsForDoctor(i)
				for i in range(int(cacheData['number_of_appointments']))
			]

		# authenticated user books bulk appointment with the therapist.	
		elif self.request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'multiple-event':
			# cacheData = { "consultant_id": profile_obj.pk, "patient_email": request.user.email, "session_id": get_session[0].pk, "start_time": [], "number_of_appointments": quantity, "duration": duration, }
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			get_session = Session.objects.get(id=cacheData['session_id'])
			start_date_and_time = cacheData['start_time']

			def getAppointmentsForTherapist( index ):
				new_start_time = datetime.strptime(start_date_and_time, '%Y-%m-%dT%H:%M:%S')
				start_dt_for_each_week = new_start_time + timedelta(weeks = index)
				end_dt_for_each_week = start_dt_for_each_week + timedelta(minutes = int(duration))
				return Appointment(
					therapist=therapist,
					start_time=start_dt_for_each_week,
					end_time=end_dt_for_each_week,
					session_type=get_session,
					zoom_link=''
				)

			appointments = [
				getAppointmentsForTherapist(i)
				for i in range(int(cacheData['number_of_appointments']))
			]

		# un-authenticated user books a single appointment with the doctor.	
		elif not self.request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'single-event':
			# cacheData = { "consultant_id": profile_obj.pk, "patient_email": email, "session_id": get_session[0].pk, "start_time": start_time, "duration": duration, }
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if not Appointment.objects.filter(doctor=doctor, start_time=start_time).exists():
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				get_session = Session.objects.get(id=cacheData['session_id'])
				appointments = [
					Appointment(
						doctor=doctor,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link=''
					)
				]

		# un-authenticated user books a single appointment with the therapist.	
		elif not self.request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'single-event':
			# cacheData = { "consultant_id": profile_obj.pk, "patient_email": email, "session_id": get_session[0].pk, "start_time": start_time, "duration": duration, }
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			start_time = cacheData['start_time']

			if not Appointment.objects.filter(therapist=therapist, start_time=start_time).exists():
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				get_session = Session.objects.get(id=cacheData['session_id'])
				appointments = [
					Appointment(
						therapist=therapist,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link=''
					)
				]

		context.update({
			"appointments": appointments,
			"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
		})
		return context

class CreateCheckoutSessionView(View):
	def get(self, request, *args, **kwargs):
		cacheData = cache.get(self.request.session.session_key)

		if cacheData == None:
			messages.add_message(self.request,messages.INFO,"Error occured. Please try again.")
			return redirect('mainapp:nav_bar_pages', folder='healthcare', page='appointment_booking_and_prices')

		# renew the cache so that the data won't be cleared during payment process.
		cache.set(self.request.session.session_key, cacheData, 600)

	def post(self, request, *args, **kwargs):

		therapy_session_id = self.kwargs["pk"]
		session_type = Session.objects.get(id=therapy_session_id)
		appointments = cache.get(self.request.session.session_key)
		YOUR_DOMAIN = "http://localhost:8000"
		cacheData = cache.get(self.request.session.session_key)

		checkout_session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=[
				{
					'price_data': {
						'currency': 'gbp',
						'unit_amount': session_type.cost,
						'product_data': {
							'name': session_type.session_name
						},
					},
					'quantity': 1,
				},
			],
			metadata=cacheData,
			mode='payment',
			success_url=YOUR_DOMAIN + '/payment/success/',
			cancel_url=YOUR_DOMAIN + '/payment/cancel/',
		)
		return JsonResponse({
			'id': checkout_session.id
		})

@csrf_exempt
def stripe_webhook(request):
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None

	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
		)
	except ValueError as e:
		# Invalid payload
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		return HttpResponse(status=400)

	# Handle the checkout.session.completed event
	if event['type'] == 'checkout.session.completed':# or event['type'] == 'checkout.session.async_payment_succeeded':
		session = event['data']['object']
		
		# Fulfill the purchase...
		customer_email = session["customer_details"]["email"]
		payment_status = session["payment_status"]
		cacheData = session["metadata"]

		if cacheData and payment_status == 'paid':
			get_session = Session.objects.get(id=cacheData['session_id'])
			patient_email = cacheData['patient_email']
			start_time = cacheData['start_time']
			duration = cacheData['duration']

			try:
				userObject = User.objects.get(email=patient_email)
				patientObject = Patient.objects.get(user=userObject)
			except(User.DoesNotExist, Patient.DoesNotExist):
				# new patient enrolment into the system.
				temp_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
				userObject = createNewUser(patient_email, temp_pass)
				patientObject = createNewPatient(userObject)
				sendMailToNewUser(patient_email, temp_pass)


			if cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'single-event':
				doctor = Doctor.objects.get(id=cacheData['consultant_id'])
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))

				app = Appointment(
						doctor=doctor,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link='',
					)
				app.save()
				app.patients.add(patientObject)

			elif cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'single-event':
				therapist = Therapist.objects.get(id=cacheData['consultant_id'])
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))

				app = Appointment(
						therapist=therapist,
						start_time=new_start_time,
						end_time=new_end_time,
						session_type=get_session,
						zoom_link='',
					)
				app.save()
				app.patients.add(patientObject)

			elif cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'multiple-event':
				doctor = Doctor.objects.get(id=cacheData['consultant_id'])
				start_date_and_time = cacheData['start_time']

				for i in range(int(cacheData['number_of_appointments'])):
					new_start_time = datetime.strptime(start_date_and_time, '%Y-%m-%dT%H:%M:%S')
					start_dt_for_each_week = new_start_time + timedelta(weeks = i)
					end_dt_for_each_week = start_dt_for_each_week + timedelta(minutes = int(duration))

					app = Appointment(
						doctor=doctor,
						start_time=start_dt_for_each_week,
						end_time=end_dt_for_each_week,
						session_type=get_session,
						zoom_link='',
					)
					app.save()
					app.patients.add(patientObject)

					# checking if appointment overlapping.
					# if Appointment(doctor=doctor, start_time__lt=start_dt_for_each_week, end_time__gt=start_dt_for_each_week).count()>1:
					# 	print("overlapping")
					# elif Appointment(doctor=doctor, start_time__lt=end_dt_for_each_week, end_time__gt=end_dt_for_each_week).count()>1:
					# 	print("overlapping")
					# elif Appointment(doctor=doctor, start_time__gt=start_dt_for_each_week, end_time__lt=end_dt_for_each_week).count()>1:
					# 	print("overlapping")
					# elif Appointment(doctor=doctor, start_time__lt=start_dt_for_each_week, end_time__gt=end_dt_for_each_week).count()>1:
					# 	print("overlapping")
					# else:
					# 	print("clear")

			elif cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'multiple-event':
				therapist = Therapist.objects.get(id=cacheData['consultant_id'])
				start_date_and_time = cacheData['start_time']

				for i in range(int(cacheData['number_of_appointments'])):
					new_start_time = datetime.strptime(start_date_and_time, '%Y-%m-%dT%H:%M:%S')
					start_dt_for_each_week = new_start_time + timedelta(weeks = i)
					end_dt_for_each_week = start_dt_for_each_week + timedelta(minutes = int(duration))

					app = Appointment(
						therapist=therapist,
						start_time=start_dt_for_each_week,
						end_time=end_dt_for_each_week,
						session_type=get_session,
						zoom_link='',
					)
					app.save()
					app.patients.add(patientObject)

			pay = Payment(
				user=userObject,
				payment_status=payment_status.upper(),
				paymentID=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
				session_type=get_session,
				amount=get_session.get_display_price()
			)
			pay.save()
			
	# Passed signature verification
	return HttpResponse(status=200)

def createNewUser(patient_email, temp_pass):
	new_user = User.objects.create_user(
		username=patient_email,
		email=patient_email,
		password=temp_pass,
		)
	return new_user

def createNewPatient(newUser):
	new_patient = Patient(
		user=newUser,
		date_of_birth=datetime.today().strftime('%Y-%m-%d')
		)
	new_patient.save()
	return new_patient

def sendMailToNewUser(patient_email, temp_pass):
	message = """
		Dear user,

		Welcome to Reviving Minds, thank you for your joining our service.
		We have created an account for you to unlock more features.
		Please login with the following details and change password as soon as you can.

		email: {},
		password: {}

		Thanks,
		The Reviving Minds Team
	""".format(patient_email, temp_pass)
	send_mail(
		subject='Welcome to Reviving Minds',
		message=message,
		recipient_list=[patient_email],
		from_email=settings.EMAIL_HOST_USER
	)
	return