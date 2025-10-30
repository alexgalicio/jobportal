from django.contrib import admin
from .models import Job, StudentProfile, EmployerProfile, Application

admin.site.register(StudentProfile)
admin.site.register(EmployerProfile)
admin.site.register(Job)
admin.site.register(Application)
