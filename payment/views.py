from accounts.models import Doctor
from accounts.models import Patient
from accounts.models import Therapist
from booking.models import Appointment
from booking.models import Session
from payment.models import Payment
from datetime import datetime
from datetime import timedelta
from django.conf import settings
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
from django.contrib import messages
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

			def getAppointmentsForDoctor( start_time ):
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				return Appointment(
					doctor=doctor,
					start_time=new_start_time,
					end_time=new_end_time,
					session_type=get_session,
					zoom_link=''
				)

			appointments = [
				getAppointmentsForDoctor(t)
				for t in cacheData['start_time']
			]

		# authenticated user books bulk appointment with the therapist.	
		elif self.request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'multiple-event':
			# cacheData = { "consultant_id": profile_obj.pk, "patient_email": request.user.email, "session_id": get_session[0].pk, "start_time": [], "number_of_appointments": quantity, "duration": duration, }
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			get_session = Session.objects.get(id=cacheData['session_id'])

			def getAppointmentsForTherapist( start_time ):
				new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
				new_end_time = new_start_time + timedelta(minutes = int(duration))
				return Appointment(
					therapist=therapist,
					start_time=new_start_time,
					end_time=new_end_time,
					session_type=get_session,
					zoom_link=''
				)

			appointments = [
				getAppointmentsForTherapist(t)
				for t in cacheData['start_time']
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

		# renew the cache so that the data wont be cleared during payment process.
		cache.set(self.request.session.session_key, cacheData, 600)

	def post(self, request, *args, **kwargs):

		therapy_session_id = self.kwargs["pk"]
		session_type = Session.objects.get(id=therapy_session_id)
		appointments = cache.get(self.request.session.session_key)
		YOUR_DOMAIN = "http://127.0.0.1:8000"
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
		userObject = None
		print("event: ", event)

		get_session = Session.objects.get(id=cacheData['session_id'])

		if request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'single-event' and payment_status == 'paid':
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			print("logged in with doctor and single-event paid")

		elif request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'single-event' and payment_status == 'paid':
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])

		elif request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'multiple-event' and payment_status == 'paid':
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])

		elif request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'multiple-event' and payment_status == 'paid':
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])

		elif not request.user.is_authenticated and cacheData['consultant'] == 'doctor' and cacheData['event_type'] == 'single-event' and payment_status == 'paid':
			doctor = Doctor.objects.get(id=cacheData['consultant_id'])
			patient_email = cacheData['patient_email']
			temp_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

			userObject = createNewUser(cacheData['patient_email'], temp_pass)
			newPatient = createNewPatient(userObject)
			sendMailToNewUser(cacheData['patient_email'], temp_pass)
			createSingleAppointmentWithDoctor(doctor, cacheData['start_time'], get_session, newPatient)

		elif not request.user.is_authenticated and cacheData['consultant'] == 'therapist' and cacheData['event_type'] == 'single-event' and payment_status == 'paid':
			therapist = Therapist.objects.get(id=cacheData['consultant_id'])
			patient_email = cacheData['patient_email']
			temp_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

			userObject = createNewUser(cacheData['patient_email'], temp_pass)
			newPatient = createNewPatient(userObject)
			sendMailToNewUser(cacheData['patient_email'], temp_pass)
			createSingleAppointmentWithTherapist(therapist, cacheData['start_time'], get_session, newPatient)


		# create a payment object for every payment for record keeping.
		# if userObject != None and payment_status == 'paid':
		# 	Payment.object.create(
		# 		user=userObject,
		# 		payment_status=payment_status.upper(),
		# 		paymentID=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
		# 		amount=get_session.get_display_price(),
		# 		session_type=get_session
		# 	)


			# 	new_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
			# 	new_end_time = new_start_time + timedelta(minutes = int(duration))

			# 	new_appointment = Appointment(
			# 			doctor=doctor,
			# 			start_time=new_start_time,
			# 			end_time=new_end_time,
			# 			session_type=get_session,
			# 			zoom_link=''
			# 		)
			# 	new_appointment.save()
			# 	new_appointment.patients.add(new_patient)

			# 	# TODO: check for appointments with doctor and the startime. if > 1, then send an email to the doctor.
			# 	# TODO: generate a zoom link and set it to the appointment.


	# Passed signature verification
	return HttpResponse(status=200)

def createNewUser(patient_email, temp_pass):
	new_user = User(
		username=patient_email,
		email=patient_email,
		password=temp_pass,
		)
	new_user.save()
	return new_user

def createNewPatient(newUser):
	new_patient = Patient(
		user=new_user,
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

def createSingleAppointmentWithDoctor(doctor, start_time, get_session, new_patient):
	new_appointment = Appointment(
		doctor=doctor,
		start_time=new_start_time,
		end_time=new_end_time,
		session_type=get_session,
		zoom_link=''
		)
	new_appointment.save()
	new_appointment.patients.add(new_patient)
	return

def createSingleAppointmentWithTherapist():
	return