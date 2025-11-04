# 🎓 Job Portal for Students
A Job Portal for Students built with Django that helps students find jobs and connect with potential employers.

## 🚀 Features
### 👩‍🎓 Students
- **Browse Jobs** - Explore all available jobs in the portal
- **View Job Details** – Check job details in either full page or a quick side panel view
- **Apply for Jobs** – Submit applications directly through the portal
- **Save Jobs** – Bookmark interesting job posts to revisit later
- **View Saved Jobs** – Access all saved jobs in one place
- **Track Applications** – View the list of jobs you’ve applied for and monitor application status

### 🏢 Employers
- **Create Job Listings** – Create new job listings
- **Edit or Delete Jobs** – Manage job posts
- **Toggle Job Status** – Mark jobs as active or closed
- **View My Jobs** – See all job listings created
- **View Applications** – Review all student applications for each job
- **Accept or Reject Applications** – Manage applicants and update their statuses

## ✨ Screenshots

| Home Page |
| --- |
| <img src="main/static/main/images/home_page.png" width="650" alt="Home Page"/> | 

### 🛠️ Student Page

| Job List | Job Detail | Apply Job |
| --- | --- | --- |
| <img src="main/static/main/images/student_jobs.png" width="650" alt="Job List"/> | <img src="main/static/main/images/student_job_detail.png" width="650" alt="Job Detail"/> | <img src="main/static/main/images/student_apply.png" width="650" alt="Apply Job"/> |

| View Saved Jobs | Track Applications | Profile |
| --- | --- | --- |
| <img src="main/static/main/images/student_saves.png" width="650" alt="View Saved Jobs"/> | <img src="main/static/main/images/student_applied.png" width="650" alt="Track Applications"/> | <img src="main/static/main/images/student_profile.png" width="650" alt="Profile"/> |

### 🛠️ Employer Page

| Create Job | Manage Jobs |
| --- | --- |
| <img src="main/static/main/images/employer_create.png" width="650" alt="Create Job"/> | <img src="main/static/main/images/employer_jobs.png" width="650" alt="Manage Jobs"/> |

| Manage Applications | Profile |
| --- | --- |
| <img src="main/static/main/images/employer_applicants.png" width="650" alt="Manage Applications"/> | <img src="main/static/main/images/employer_profile.png" width="650" alt="Profile Feed"/> |


## ⚙️ Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/alexgalicio/jobportal.git
   cd jobportal
   ```

2. **Install dependencies**
   ```bash
   pip install django
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

 Open `http://127.0.0.1:8000/` with your browser to see the result.