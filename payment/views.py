from django.views import View
import stripe
import json
from django.conf import settings
from booking.models import Session
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessView(TemplateView):
	template_name = "payment/success.html"

class CancelView(TemplateView):
	template_name = "payment/cancel.html"

class ProductLandingPageView(TemplateView):
	template_name = "payment/landing.html"

	def get_context_data(self, **kwargs):
		context = super(ProductLandingPageView, self).get_context_data(**kwargs)
		context.update({
			"therapy_session": Session.objects.get(id=1),
			"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
		})
		return context

class CreateCheckoutSessionView(View):
	def post(self, request, *args, **kwargs):
		print("YES")

		therapy_session_id = self.kwargs["pk"] # to het which booking package patient is going for.
		session_type = Session.objects.get(id=therapy_session_id)
		print(session_type)
		YOUR_DOMAIN = "http://127.0.0.1:8000"

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
			metadata={
				"session_type_id": session_type.id
			},
			mode='payment',
			success_url=YOUR_DOMAIN + '/payment/success/',
			cancel_url=YOUR_DOMAIN + '/payment/cancel/',
		)
		return JsonResponse({
			'session_id': checkout_session.id
		})