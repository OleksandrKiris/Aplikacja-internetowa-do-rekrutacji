import os
import django
import random
from django.utils import timezone
from django.db import transaction
from faker import Faker
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
django.setup()

# Import models
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, User
from jobs.models import Job, Application, GuestFeedback
from requests.models import JobRequest
from news.models import News

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
    while True:
        email = fake.unique.email()
        password = fake.password(length=12)
        try:
            user = User.objects.create_user(email=email, password=password, role=role)
            print(f"{role.capitalize()} - Email: {email}, Password: {password}")
            return user
        except ValidationError as e:
            print(f"Error: {e}")
            continue


def create_candidate_profile():
    user = create_user('candidate')
    profile = CandidateProfile.objects.create(
        user=user,
        first_name=fake.first_name()[:100],
        last_name=fake.last_name()[:100],
        phone_number=generate_phone_number()[:15],
        location=fake.city()[:100],
        bio=fake.text(max_nb_chars=500),
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
        skills=fake.text(max_nb_chars=500)
    )
    print(f"Candidate Profile: {profile}")


def create_client_profile():
    user = create_user('client')
    profile = ClientProfile.objects.create(
        user=user,
        phone_number=generate_phone_number()[:15],
        location=fake.city()[:100],
        bio=fake.text(max_nb_chars=500),
        company_name=fake.company()[:100],
        industry=fake.job()[:50]
    )
    print(f"Client Profile: {profile}")


def create_recruiter_profile():
    user = create_user('recruiter')
    profile = RecruiterProfile.objects.create(
        user=user,
        first_name=fake.first_name()[:100],
        last_name=fake.last_name()[:100],
        phone_number=generate_phone_number()[:15],
        location=fake.city()[:100],
        bio=fake.text(max_nb_chars=500)
    )
    print(f"Recruiter Profile: {profile}")


def create_job():
    recruiter = RecruiterProfile.objects.order_by('?').first().user
    job = Job.objects.create(
        title=fake.job()[:200],
        recruiter=recruiter,
        description=fake.text(max_nb_chars=500),
        requirements=fake.text(max_nb_chars=500),
        salary=round(random.uniform(50000, 150000), 2),
        status=random.choice(JOB_STATUS_CHOICES)
    )
    print(f"Job: {job}")


def create_application():
    job = Job.objects.order_by('?').first()
    applicant = CandidateProfile.objects.order_by('?').first().user
    application = Application.objects.create(
        job=job,
        applicant=applicant,
        cover_letter=fake.text(max_nb_chars=500),
        status=random.choice(APPLICATION_STATUS_CHOICES)
    )
    print(f"Application: {application}")


def create_guest_feedback():
    job = Job.objects.order_by('?').first()
    feedback = GuestFeedback.objects.create(
        job=job,
        email=fake.unique.email(),
        message=fake.text(max_nb_chars=500),
        phone_number=generate_phone_number()[:15]
    )
    print(f"Guest Feedback: {feedback}")


def create_job_request():
    employer = ClientProfile.objects.order_by('?').first().user
    recruiter = RecruiterProfile.objects.order_by('?').first().user
    job_request = JobRequest.objects.create(
        employer=employer,
        title=fake.job()[:200],
        description=fake.text(max_nb_chars=500),
        requirements=fake.text(max_nb_chars=500),
        status=random.choice(JOB_REQUEST_STATUS_CHOICES),
        recruiter=recruiter
    )
    print(f"Job Request: {job_request}")


def create_news():
    news = News.objects.create(
        title=fake.sentence()[:200],
        content=fake.text(max_nb_chars=500),
        role=random.choice(NEWS_ROLE_CHOICES)
    )
    print(f"News: {news}")


def populate_database():
    with transaction.atomic():
        for _ in range(50):
            create_candidate_profile()
            create_client_profile()
            create_recruiter_profile()
        for _ in range(1000):
            create_job()
            create_application()
            create_guest_feedback()
            create_job_request()
            create_news()
    print("Database populated with 50 users and 1000 records for each specified table.")


if __name__ == '__main__':
    populate_database()
