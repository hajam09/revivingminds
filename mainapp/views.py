from django.shortcuts import render
from mainapp.models import Category
from mainapp.models import Article

def mainpage(request):
	return render(request, "mainapp/mainpage.html")

def article_page(request, category, article):
	# article page
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
	# list of all the articles
	category = Category.objects.get(slug=category)
	all_articles = Article.objects.filter(category=category, show=True)

	context = {
		"category": category,
		"all_articles": all_articles
	}
	return render(request, "mainapp/articles.html", context)
