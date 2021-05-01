from django.urls import path
from mainapp import views

app_name = "mainapp"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('info/<slug:category>/<slug:url>', views.information, name='information'),
	path('info/<slug:category>/', views.articles, name='articles'),
	path('administrator/create_article', views.create_article, name='create_article'),
]