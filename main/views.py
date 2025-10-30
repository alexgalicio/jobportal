from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ApplicationForm, EmployerProfileForm, JobForm, StudentProfileForm, UserRegistrationForm, LoginForm
from .models import Application, Saved, EmployerProfile, Job, StudentProfile, UserProfile

def home(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # redirect to specific page based on user role
        return redirect('main:student_page' if profile.role == 'student' else 'main:employer_page')

    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'main/register.html', {'form': form})

def custom_login(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('main:student_page' if profile.role == 'student' else 'main:employer_page')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                profile = UserProfile.objects.get(user=user)
                return redirect('main:student_page' if profile.role == 'student' else 'main:employer_page')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
        
    return render(request, 'main/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('main:home')

@login_required
def student_page(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'student':
        messages.error(request, 'Access denied. Student access required.')
        return redirect('main:home')
    
    context = {
        'user': request.user,
        'profile': profile
    }
    
    return render(request, 'main/student_page.html', context)

@login_required
def employer_page(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'employer':
        messages.error(request, 'Access denied. Employer access required.')
        return redirect('main:home')
    
    context = {
        'user': request.user,
        'profile': profile
    }
    
    return render(request, 'main/employer_page.html', context)

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
        return redirect('main:profile')
    
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
        return redirect('main:home')

    # only employer can create job
    if profile.role != 'employer':
        return redirect('main:home')
    
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
        return redirect('main:profile')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Job posting created successfully!')
            return redirect('main:home') # TODO: redirect to my jobs page
    else:
        form = JobForm()
    
    return render(request, 'main/create_job.html', {'form': form})

# public view
def job_list(request):   
    jobs = Job.objects.all().order_by('-created_at')

    saved_jobs = []
    if request.user.is_authenticated:
        saved_jobs = Saved.objects.filter(user=request.user).values_list('job_id', flat=True)

    # filtering logic
    search_query = request.GET.get('search', '')
    location_query = request.GET.get('location', '')
    workplace_query = request.GET.get('workplace', '')
    work_type_query = request.GET.get('work_type', '')
    
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
        saved_jobs = Saved.objects.filter(user=request.user).values_list('job_id', flat=True)
    else:
        saved_jobs = []

    context = {
        'job': job,
        'has_applied': has_applied,
        'saved_jobs': saved_jobs,
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
    # get job id, return 404 if it doesnt exist
    job = get_object_or_404(Job, id=job_id)

    # check if user already applied
    # existing_application = Application.objects.filter(job=job, applicant=request.user).first()
    # if existing_application:
    #     messages.warning(request, "You already applied for this job.")
    #     return redirect('main:job_detail_full', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Your application was submitted successfully!")
            return redirect('main:job_detail_full', job_id=job.id)
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
        applications = applications.filter(status=status_filter)
        
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

    jobs = [save.job for save in saves]

    context = {
        'jobs': jobs,
    }
    return render(request, 'main/saved_jobs.html', context)