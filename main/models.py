from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('employer', 'Employer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class StudentProfile(models.Model):
    YEAR_LEVEL_CHOICES = [
        ('', 'Select year level'),
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('graduate', 'Graduate'),
    ]

    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    profile_img = models.ImageField(
        upload_to='user_profile_img/', blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    school = models.CharField(max_length=200)
    course = models.CharField(max_length=200)
    year_level = models.CharField(
        max_length=20, choices=YEAR_LEVEL_CHOICES)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    bio = models.TextField(blank=True, max_length=1000)

    def __str__(self):
        return self.user_profile.user.username


class EmployerProfile(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('', 'Select no. of employees'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]

    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    company_address = models.CharField(max_length=300)
    industry = models.CharField(max_length=100)
    company_size = models.CharField(
        max_length=20, choices=COMPANY_SIZE_CHOICES)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.user_profile.user.username


class Job(models.Model):
    WORKPLACE_CHOICES = [
        ('', 'Select workplace'),
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
    ]

    WORK_TYPE_CHOICES = [
        ('', 'Select work type'),
        ('internship', 'Internship'),
        ('full', 'Full-time'),
        ('part', 'Part-time'),
        ('contract', 'Contract'),
        ('casual', 'Casual'),
    ]

    PAY_TYPE_CHOICES = [
        ('', 'Select pay type'),
        ('hourly', 'Hourly rate'),
        ('monthly', 'Monthly salary'),
        ('annual', 'Annual salary'),
        ('annual-plus', 'Annual plus commision'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='jobs')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    workplace = models.CharField(max_length=20, choices=WORKPLACE_CHOICES)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES)
    pay_type = models.CharField(max_length=20, choices=PAY_TYPE_CHOICES)
    pay_min = models.DecimalField(max_digits=10, decimal_places=2)
    pay_max = models.DecimalField(max_digits=10, decimal_places=2)
    job_description = models.TextField()
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE,
                            related_name='applications')
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # prevent duplicate applications
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


class Saved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
