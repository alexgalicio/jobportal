from django.contrib import admin
from .models import Job, UserProfile, StudentProfile, EmployerProfile, Application, Saved

admin.site.register(UserProfile)
admin.site.register(StudentProfile)
admin.site.register(EmployerProfile)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Saved)
