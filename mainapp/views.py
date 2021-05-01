from django.shortcuts import render
from mainapp.models import Category
from mainapp.models import Article

def mainpage(request):
	return render(request, "mainapp/mainpage.html")

def information(request, category, url):
	all_category = Category.objects.all()
	article = Article.objects.get(
		slug=url,
		show=True
	)
	context = {
		"all_category": all_category,
		"article": article
	}
	return render(request, "mainapp/information.html", context)

def create_article(request):
	context = {

	}
	return render(request, "mainapp/create_article.html", context)

def articles(request, category):
	category = Category.objects.get(slug=category)
	all_articles = Article.objects.filter(category=category, show=True)
	print(all_articles)
	context = {
		"category": category,
		"all_articles": all_articles
	}
	return render(request, "mainapp/articles.html", context)
