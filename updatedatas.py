import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
django.setup()

from  accounts.models import User, ApplicantProfile, EmployerProfile, RecruiterProfile, Task
from  jobs.models import Job, Application
# Создание пользователей с паролями
user1 = User.objects.create_user(email='candidate@example.com', password='candidate123', role='candidate')
user2 = User.objects.create_user(email='employer@example.com', password='employer123', role='employer')
user3 = User.objects.create_user(email='recruiter@example.com', password='recruiter123', role='recruiter')

# Создание профилей
ApplicantProfile.objects.create(
    user=user1,
    first_name='Ivan',
    last_name='Ivanov',
    phone_number='123456789',
    location='Kyiv',
    bio='Experienced developer',
    date_of_birth=date(1990, 1, 1),
    skills='Python, Django'
)

EmployerProfile.objects.create(
    user=user2,
    phone_number='987654321',
    location='Warsaw',
    bio='Tech startup',
    company_name='Tech Innovations',
    industry='IT'
)

RecruiterProfile.objects.create(
    user=user3,
    first_name='Anna',
    last_name='Smith',
    phone_number='123987456',
    location='London',
    bio='Recruiter with 10 years experience'
)

# Создание вакансий и заявлений
job = Job.objects.create(
    title='Senior Django Developer',
    recruiter=user3,
    description='We are looking for an experienced Django Developer.',
    requirements='At least 5 years of experience with Django.',
    salary=5000.00,
    status='open'
)

application = Application.objects.create(
    job=job,
    applicant=user1,
    cover_letter='I am very interested in this position.',
    status='submitted'
)

print("Data has been successfully added to the database!")
