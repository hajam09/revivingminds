from django.urls import path
from payment.views import (
    CreateCheckoutSessionView,
    ProductLandingPageView,
    SuccessView,
    CancelView
)

app_name = "payment"

urlpatterns = [
	path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
	path('', ProductLandingPageView.as_view(), name='landing-page'),
	path('cancel/', CancelView.as_view(), name='cancel-page'),
	path('success/', SuccessView.as_view(), name='success-page'),
	path('', ProductLandingPageView.as_view(), name='landing-page'),
	# path('info/<slug:category>/', views.articles, name='articles'),
	# path('info/<slug:category>/<slug:article>', views.article_page, name='article_page'),
	# path('administrator/create_article', views.create_article, name='create_article'),
]