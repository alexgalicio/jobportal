from django.urls import path
from . import views

urlpatterns = [
    # home and auth
    path('', views.home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    
    # job details
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/partial/<int:job_id>/', views.job_detail_panel, name='job_detail_panel'),
    path('jobs/<int:job_id>/', views.job_detail_full, name='job_detail_full'),
    path('saved/<int:job_id>/', views.toggle_save, name='toggle_save'),
    
    # student
    # path('student/', views.student_page, name='student_page'),
    path('student/applied/', views.applied_jobs, name='applied_jobs'),
    path('student/apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('student/saved/', views.saved_jobs, name='saved_jobs'),

    # employer
    # path('employer/', views.employer_page, name='employer_page'),
    path('employer/create/', views.create_job, name='create_job'),
    path('employer/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('employer/my-jobs/', views.my_jobs, name='my_jobs'),
    path('employer/toggle-status/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),
    path('employer/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('employer/applications/<int:job_id>/', views.view_applications, name='view_applications'),
    path('application/<int:app_id>/accept/', views.accept_application, name='accept_application'),
    path('application/<int:app_id>/reject/', views.reject_application, name='reject_application'),

    # user shared page
    path('profile/', views.profile_view, name='profile'),
]
