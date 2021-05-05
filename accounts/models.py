from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
import uuid

# class User(AbstractUser):
#     is_therapist = models.BooleanField(default=False)
#     is_patient = models.BooleanField(default=False)

class Patient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	slug = models.SlugField(max_length=255, allow_unicode=True, default=uuid.uuid4, unique=True)
	date_of_birth = models.DateField(auto_now=False, auto_now_add=False)

class Therapist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	slug = models.SlugField(max_length=255, allow_unicode=True, default=uuid.uuid4, unique=True)
	profile_picture = models.ImageField(upload_to='profilepicture', blank=True, null=True)

	@property
	def profile_picture_url(self):
		if self.profile_picture:# or self.profile_picture != None:
			return self.profile_picture
		return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"

class Doctor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	slug = models.SlugField(max_length=255, allow_unicode=True, default=uuid.uuid4, unique=True)
	profile_picture = models.ImageField(upload_to='profilepicture', blank=True, null=True)

	@property
	def profile_picture_url(self):
		if self.profile_picture or self.profile_picture != None:
			return self.profile_picture
		return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"