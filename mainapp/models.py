from django.db import models
from datetime import datetime

class Category(models.Model):
	slug = models.SlugField(max_length=255, allow_unicode=True)
	name = models.CharField(max_length=255)

	def __str__ (self):
		return self.name

class Article(models.Model):
	slug = models.SlugField(max_length=255, allow_unicode=True)
	title = models.CharField(max_length=255)
	image = models.ImageField(upload_to='article_image', blank=True, null=True)
	description = models.TextField()
	related_articles = models.ManyToManyField("self", blank=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
	show = models.BooleanField(default=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True)

	def __str__ (self):
		return self.title