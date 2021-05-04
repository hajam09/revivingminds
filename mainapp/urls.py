from django.urls import path
from mainapp import views

app_name = "mainapp"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('info/<slug:category>/', views.articles, name='articles'),
	path('info/<slug:category>/<slug:article>', views.article_page, name='article_page'),
	path('administrator/create_article', views.create_article, name='create_article'),
	path('nav/<slug:folder>/<slug:page>', views.nav_bar_pages, name='nav_bar_pages'),
]