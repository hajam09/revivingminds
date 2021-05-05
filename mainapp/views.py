from django.shortcuts import render
from mainapp.models import Category
from mainapp.models import Article
from accounts.models import Doctor
from accounts.models import Therapist
from booking.models import Session
import random

def nav_bar_pages(request, folder, page):
	context = {}

	if folder == "about" and page == "contact":
		# Parse all the forms on the about/contact.html page

		if request.method == "POST" and "contact-us-form-in-about-contact" in request.POST:
			full_name = request.POST["full-name"]
			email = request.POST["email"]
			subject = request.POST["subject"]
			message = request.POST["message"]
			# TODO: create a model and store this data in that model.
			context["message"] = "Thank you for your interst. We will get back to you soon."

	elif folder == "healthcare" and page == "appointment_booking_and_prices":
		# In this page, display all the doctors and the therapist to book the appointment and the prices.
		doctors = Doctor.objects.all()
		therapists = Therapist.objects.all()
		context["doctors"] = doctors
		context["therapists"] = therapists
		# context["doctors_and_therapists"] = list(doctors) + list(therapists)
		# may need to fetch consultation for doctor and normal session separately.
		context["session_with_doctor"] = Session.objects.filter(doctor=doctors[0]).order_by('cost')[:2]
		context["session_with_therapist"] = Session.objects.filter(doctor=None).order_by('cost')[:1]
		# print(context["doctors_and_therapists"])

	template = "mainapp/"+folder+"/"+page+".html"
	return render(request, template, context)


def mainpage(request):

	items = list(Article.objects.filter(show=True))
	the_articles = random.sample(items, 6)

	context = {
		"the_articles": the_articles
	}
	return render(request, "mainapp/mainpage.html", context)

def article_page(request, category, article):

	all_category = Category.objects.all()
	recent_posts = Article.objects.all().order_by('-created_at')[:5]

	article = Article.objects.get(
		slug=article,
		show=True
	)

	context = {
		"all_category": all_category,
		"article": article,
		"recent_posts": recent_posts
	}
	return render(request, "mainapp/information.html", context)

def create_article(request):
	context = {

	}
	return render(request, "mainapp/create_article.html", context)

def articles(request, category):
	# list of all the articles for this category.
	category = Category.objects.get(slug=category)
	all_articles = Article.objects.filter(category=category, show=True)

	context = {
		"category": category,
		"all_articles": all_articles
	}
	return render(request, "mainapp/articles.html", context)