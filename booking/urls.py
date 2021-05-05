from django.urls import path
from booking import views

app_name = "booking"

urlpatterns = [
	path('view_schedule/<slug:profile>/', views.view_schedule, name='view_schedule'),
]