import os
import django
import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
django.setup()

# Import models
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from jobs.models import Job, Application, GuestFeedback
from requests.models import JobRequest
from news.models import News

User = get_user_model()
fake = Faker()

# Constants
ROLE_CHOICES = ['candidate', 'client', 'recruiter']
APPLICATION_STATUS_CHOICES = ['submitted', 'reviewed', 'accepted', 'rejected']
TASK_PRIORITY_CHOICES = ['low', 'medium', 'high']
TASK_STATUS_CHOICES = ['open', 'in_progress', 'completed']
JOB_STATUS_CHOICES = ['open', 'closed']
JOB_REQUEST_STATUS_CHOICES = ['pending', 'processing', 'completed']
NEWS_ROLE_CHOICES = ['candidate', 'client', 'recruiter']


def generate_phone_number():
    return fake.numerify(text="+###########")


def create_user(role):
    email = fake.email()
    password = fake.password(length=12)
    user = User.objects.create_user(email=email, password=password, role=role)
    print(f"{role.capitalize()} email: {email}, password: {password}")
    return user


def create_candidate_profile():
    user = create_user('candidate')
    CandidateProfile.objects.create(
        user=user,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        phone_number=generate_phone_number(),
        location=fake.city(),
        bio=fake.text(max_nb_chars=200),
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
        skills=fake.text(max_nb_chars=200)
    )


def create_client_profile():
    user = create_user('client')
    ClientProfile.objects.create(
        user=user,
        phone_number=generate_phone_number(),
        location=fake.city(),
        bio=fake.text(max_nb_chars=200),
        company_name=fake.company(),
        industry=fake.job()
    )


def create_recruiter_profile():
    user = create_user('recruiter')
    RecruiterProfile.objects.create(
        user=user,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        phone_number=generate_phone_number(),
        location=fake.city(),
        bio=fake.text(max_nb_chars=200)
    )


def create_task():
    created_by = create_user(random.choice(ROLE_CHOICES))
    Task.objects.create(
        created_by=created_by,
        title=fake.sentence(),
        description=fake.text(max_nb_chars=200),
        priority=random.choice(TASK_PRIORITY_CHOICES),
        due_date=fake.date_between(start_date='today', end_date='+30d'),
        status=random.choice(TASK_STATUS_CHOICES)
    )


def create_job():
    recruiter = create_user('recruiter')
    Job.objects.create(
        title=fake.job(),
        recruiter=recruiter,
        description=fake.text(max_nb_chars=200),
        requirements=fake.text(max_nb_chars=200),
        salary=round(random.uniform(50000, 150000), 2),
        status=random.choice(JOB_STATUS_CHOICES)
    )


def create_application():
    job = Job.objects.order_by('?').first()
    applicant = create_user('candidate')
    Application.objects.create(
        job=job,
        applicant=applicant,
        cover_letter=fake.text(max_nb_chars=200),
        status=random.choice(APPLICATION_STATUS_CHOICES)
    )


def create_guest_feedback():
    job = Job.objects.order_by('?').first()
    GuestFeedback.objects.create(
        job=job,
        email=fake.email(),
        message=fake.text(max_nb_chars=200),
        phone_number=generate_phone_number()
    )


def create_job_request():
    employer = create_user('client')
    recruiter = User.objects.filter(role='recruiter').order_by('?').first()
    JobRequest.objects.create(
        employer=employer,
        title=fake.job(),
        description=fake.text(max_nb_chars=200),
        requirements=fake.text(max_nb_chars=200),
        status=random.choice(JOB_REQUEST_STATUS_CHOICES),
        recruiter=recruiter
    )


def create_news():
    News.objects.create(
        title=fake.sentence(),
        content=fake.text(max_nb_chars=200),
        role=random.choice(NEWS_ROLE_CHOICES)
    )


def populate_database():
    with transaction.atomic():
        for _ in range(50):
            create_candidate_profile()
            create_client_profile()
            create_recruiter_profile()
            create_task()
            create_job()
            create_application()
            create_guest_feedback()
            create_job_request()
            create_news()
    print("Database populated with 50 records for each table.")


if __name__ == '__main__':
    populate_database()
