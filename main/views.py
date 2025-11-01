from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .forms import ApplicationForm, EmployerProfileForm, JobForm, StudentProfileForm, UserRegistrationForm, LoginForm
from .models import Application, Saved, EmployerProfile, Job, StudentProfile, UserProfile

def home(request):
    # if request.user.is_authenticated:
    #     profile = UserProfile.objects.get(user=request.user)
    #     # redirect to specific page based on user role
    #     return redirect('student_page' if profile.role == 'student' else 'employer_page')
    
     # For visitors (not logged in) — show latest 12 featured jobs
    featured_jobs = Job.objects.filter(status='active').select_related('employer__userprofile__employerprofile').order_by('-created_at')[:9]

    return render(request, 'main/home.html', {'featured_jobs': featured_jobs})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'main/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                profile = UserProfile.objects.get(user=user)
                return redirect('job_list' if profile.role == 'student' else 'my_jobs')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
        
    return render(request, 'main/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

# @login_required
# def student_page(request):
#     profile = UserProfile.objects.get(user=request.user)
#     if profile.role != 'student':
#         messages.error(request, 'Access denied. Student access required.')
#         return redirect('home')
    
#     context = {
#         'user': request.user,
#         'profile': profile
#     }
    
#     return render(request, 'main/student_page.html', context)

# @login_required
# def employer_page(request):
#     profile = UserProfile.objects.get(user=request.user)
#     if profile.role != 'employer':
#         messages.error(request, 'Access denied. Employer access required.')
#         return redirect('home')
    
#     context = {
#         'user': request.user,
#         'profile': profile
#     }
    
#     return render(request, 'main/employer_page.html', context)


@login_required
def profile_view(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    # check role and get the specific profile
    if user_profile.role == 'student':
        profile, created = StudentProfile.objects.get_or_create(user_profile=user_profile)
        form = StudentProfileForm(request.POST or None, request.FILES or None, instance=profile)
    else:
        profile, created = EmployerProfile.objects.get_or_create(user_profile=user_profile)
        form = EmployerProfileForm(request.POST or None, request.FILES or None, instance=profile)

    # auto fill email for display
    user_email = user.email

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'form': form,
        'role': user_profile.role,
        'user_email': user_email,
    }

    return render(request, 'main/profile.html', context)

@login_required
def create_job(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('home')

    # only employer can create job
    if profile.role != 'employer':
        return redirect('home')
    
    employer_profile = EmployerProfile.objects.get(user_profile=profile)
    required_fields = [
        employer_profile.company_name,
        employer_profile.phone,
        employer_profile.company_address,
        employer_profile.industry,
        employer_profile.company_size,
        employer_profile.description,
    ]
    
    # complete profile first before creating job
    if not all(required_fields):
        messages.error(request, "Please complete your employer profile before creating a job.")
        return redirect('profile')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Job posting created successfully!')
            return redirect('home') # TODO: redirect to my jobs page
    else:
        form = JobForm()
    
    return render(request, 'main/create_job.html', {'form': form})

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('my_jobs')
    else:
        form = JobForm(instance=job)

    return render(request, 'main/create_job.html', {
        'form': form,
        'is_edit': True,  # 👈 pass flag to template
    })

# public view
def job_list(request):
    jobs = Job.objects.filter(status='active').order_by('-created_at')

    saved_jobs = []
    if request.user.is_authenticated:
        saved_jobs = Saved.objects.filter(user=request.user).values_list('job_id', flat=True)

    # filtering logic
    search_query = request.GET.get('search', '')
    location_query = request.GET.get('location', '')
    workplace_query = request.GET.get('workplace', '')
    work_type_query = request.GET.get('work_type', '')
    date_posted = request.GET.get('date_posted', '') 
    
    # can search by title, company, desc, summary
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(employer__userprofile__employerprofile__company_name__icontains=search_query) |
            Q(job_description__icontains=search_query) |
            Q(summary__icontains=search_query)
        )
    
    if location_query:
        jobs = jobs.filter(location__icontains=location_query)
    
    if workplace_query:
        jobs = jobs.filter(workplace=workplace_query)
    
    if work_type_query:
        jobs = jobs.filter(work_type=work_type_query)

    if date_posted:
        today = timezone.now().date()
        if date_posted == "today":
            jobs = jobs.filter(created_at__date=today)
        elif date_posted == "3days":
            jobs = jobs.filter(created_at__gte=today - timedelta(days=3))
        elif date_posted == "7days":
            jobs = jobs.filter(created_at__gte=today - timedelta(days=7))
        elif date_posted == "14days":
            jobs = jobs.filter(created_at__gte=today - timedelta(days=14))
        elif date_posted == "30days":
            jobs = jobs.filter(created_at__gte=today - timedelta(days=30))
    
    # 20 jobs per page
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    context = {
        'jobs': jobs_page,
        'saved_jobs': saved_jobs,
        'search_query': search_query,
        'location_query': location_query,
        'workplace_query': workplace_query,
        'work_type_query': work_type_query,
        'date_posted': date_posted,
    }
    
    return render(request, 'main/job_list.html', context)


# used in split layout on with job list
def job_detail_panel(request, job_id):
    # get job id, retturn 404 if it doesnt exist
    job = get_object_or_404(Job, id=job_id)
    
    has_applied = False
    # check if logged in user have already applied to the job
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
    }
    
    return render(request, 'main/job_detail_panel.html', context)

# standalone job detail page
def job_detail_full(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
    }
    
    return render(request, 'main/job_detail_full.html', context)

@login_required
def apply_job(request, job_id):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('home')

    # only student can apply job
    if profile.role != 'student':
        return redirect('job_list')
    
    # get job id, return 404 if it doesnt exist
    job = get_object_or_404(Job, id=job_id)

    # check if user already applied
    # existing_application = Application.objects.filter(job=job, applicant=request.user).first()
    # if existing_application:
    #     messages.warning(request, "You already applied for this job.")
    #     return redirect('job_detail_full', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Your application was submitted successfully!")
            return redirect('job_detail_full', job_id=job.id)
    else:
        form = ApplicationForm()
        
    context = {
        'form': form,
        'job': job
    }

    return render(request, 'main/apply_job.html', context)

@login_required
def applied_jobs(request):
    applications = Application.objects.filter(applicant=request.user).select_related('job', 'job__employer').order_by('-applied_at')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # can search by title, company
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__employer__userprofile__employerprofile__company_name__icontains=search_query)
        )

    if status_filter:
        applications = applications.filter(job__status=status_filter)
        
    # 10 applications per page
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)

    context = {
        'jobs': applications_page,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'main/applied_jobs.html', context)

@login_required
def toggle_save(request, job_id):
    job = Job.objects.get(pk=job_id)
    save, created = Saved.objects.get_or_create(user=request.user, job=job)

    if not created:
        save.delete()
        is_saved = False
    else:
        is_saved = True

    return JsonResponse({'is_saved': is_saved})

@login_required
def saved_jobs(request):
    saves = Saved.objects.filter(user=request.user).select_related('job')

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # can search by title, company
    if search_query:
        saves = saves.filter(
            Q(job__title__icontains=search_query) |
            Q(job__employer__userprofile__employerprofile__company_name__icontains=search_query)
        )

    if status_filter:
        saves = saves.filter(job__status=status_filter)
        
    paginator = Paginator(saves, 10)
    page_number = request.GET.get('page')
    save_page = paginator.get_page(page_number)

    saved_job_ids = [save.job.id for save in save_page]

    context = {
        'save_page': save_page,
        'saved_jobs': saved_job_ids,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'main/saved_jobs.html', context)

@login_required
def my_jobs(request):
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # can search by title, company
    if search_query:
        jobs = jobs.filter(
            Q(job__title__icontains=search_query) |
            Q(job__employer__userprofile__employerprofile__company_name__icontains=search_query)
        )

    if status_filter:
        jobs = jobs.filter(status=status_filter)

    jobs = jobs.annotate(app_count=Count('applications'))

    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)

    context = {
        'jobs': jobs_page,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'main/my_jobs.html', context)

@login_required
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)

    if job.status == 'expired':
        job.status = 'active'
        messages.success(request, f"'{job.title}' has been marked as active again.")
    else:
        job.status = 'expired'
        messages.info(request, f"'{job.title}' has been marked as expired.")

    job.save()
    return redirect('my_jobs')


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)

    if request.method == 'POST':
        job.delete()
        messages.success(request, f'Job "{job.title}" has been deleted successfully.')

    return redirect('my_jobs')

@login_required
def view_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)

    applications = Application.objects.filter(job=job).select_related('applicant__userprofile').order_by('-applied_at')

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'main/view_applications.html', context)