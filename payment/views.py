from django.views import View
import stripe
import json
from django.conf import settings
from booking.models import Session
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.urls import reverse
from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponseRedirect

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessView(TemplateView):
	template_name = "payment/success.html"

class CancelView(TemplateView):
	template_name = "payment/cancel.html"

class ProductLandingPageView(TemplateView):
	template_name = "payment/landing.html"

	def get(self, *args, **kwargs):
		appointments = cache.get(self.request.session.session_key)
		print("appointments",appointments)
		if appointments == None:
			return redirect('mainapp:nav_bar_pages', folder='healthcare', page='appointment_booking_and_prices')
		return super().get(*args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(ProductLandingPageView, self).get_context_data(**kwargs)
		appointments = cache.get(self.request.session.session_key)
		print(self.request.session.session_key)

		context.update({
			"appointments": appointments,
			"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
		})
		return context

class CreateCheckoutSessionView(View):
	def post(self, request, *args, **kwargs):

		therapy_session_id = self.kwargs["pk"]
		session_type = Session.objects.get(id=therapy_session_id)
		print(session_type)
		YOUR_DOMAIN = "http://127.0.0.1:8000"

		# checkout_session = stripe.checkout.Session.create(
		# 	payment_method_types=['card'],
		# 	line_items=[
		# 		{
		# 			'price_data': {
		# 				'currency': 'gbp',
		# 				'unit_amount': session_type.cost,
		# 				'product_data': {
		# 					'name': session_type.session_name
		# 				},
		# 			},
		# 			'quantity': 1,
		# 		},
		# 	],
		# 	metadata={
		# 		"session_type_id": session_type.id
		# 	},
		# 	mode='payment',
		# 	success_url=YOUR_DOMAIN + '/payment/success/',
		# 	cancel_url=YOUR_DOMAIN + '/payment/cancel/',
		# )
		return JsonResponse({
			'session_id': "checkout_session.id"
		})