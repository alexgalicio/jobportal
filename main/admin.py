from django.contrib import admin
from .models import Job, UserProfile, StudentProfile, EmployerProfile, Application, Saved


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'first_name', 'last_name',
                    'school', 'course', 'year_level')
    search_fields = ('user_profile__user__username',
                     'first_name', 'last_name', 'school', 'course')


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'company_name', 'industry', 'company_size')
    search_fields = ('user_profile__user__username',
                     'company_name', 'industry')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'workplace',
                    'work_type', 'pay_type', 'status', 'created_at')
    search_fields = ('title', 'employer__username', 'location',
                     'work_type', 'pay_type', 'status')
    list_filter = ('status', 'workplace', 'work_type', 'pay_type')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    search_fields = ('job__title', 'applicant__username', 'status')
    list_filter = ('status',)


@admin.register(Saved)
class SavedAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('created_at',)
