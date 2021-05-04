from django.contrib import admin
from accounts.models import Patient
from accounts.models import Therapist
from accounts.models import Doctor

admin.site.register(Patient)
admin.site.register(Therapist)
admin.site.register(Doctor)