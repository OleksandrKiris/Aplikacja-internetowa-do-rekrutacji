import os
import django
import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

# Переместите импорты после вызова django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
django.setup()

from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from jobs.models import Job, Application, GuestFeedback
from requests.models import JobRequest

User = get_user_model()

@transaction.atomic
def create_accounts_data():
    # Создаем и сохраняем 30 экземпляров модели CandidateProfile
    for i in range(30):
        email = f'candidate{i+30}@example.com'
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='password123',
                role='candidate'
            )
            CandidateProfile.objects.create(
                user=user,
                first_name=f'CandidateFirstName{i}',
                last_name=f'CandidateLastName{i}',
                phone_number='+1234567890',
                location='Location',
                bio='Bio',
                date_of_birth=timezone.now().date(),
                skills='Skills'
            )

    # Создаем и сохраняем 30 экземпляров модели ClientProfile
    for i in range(30):
        email = f'client{i+30}@example.com'
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='password123',
                role='client'
            )
            ClientProfile.objects.create(
                user=user,
                phone_number='+1234567890',
                location='Location',
                bio='Bio',
                company_name=f'Company{i}',
                industry='Industry'
            )

    # Создаем и сохраняем 30 экземпляров модели RecruiterProfile
    for i in range(30):
        email = f'recruiter{i+30}@example.com'
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password='password123',
                role='recruiter'
            )
            RecruiterProfile.objects.create(
                user=user,
                first_name=f'RecruiterFirstName{i}',
                last_name=f'RecruiterLastName{i}',
                phone_number='+1234567890',
                location='Location',
                bio='Bio'
            )

@transaction.atomic
def create_jobs_data():
    for i in range(30):
        recruiter_email = f'recruiter{i+30}@example.com'
        if User.objects.filter(email=recruiter_email).exists():
            recruiter = User.objects.get(email=recruiter_email)
            job = Job.objects.create(
                title=f'JobTitle{i}',
                recruiter=recruiter,
                description=f'Description{i}',
                requirements=f'Requirements{i}',
                salary=random.randint(1000, 5000),
                created_at=timezone.now(),
                status=random.choice(['open', 'closed'])
            )

            # Создаем и сохраняем 30 экземпляров модели Task для каждой вакансии
            for j in range(30):
                Task.objects.create(
                    created_by=recruiter,
                    title=f'Task{j} for Job {i}',
                    description=f'Task description for Job {i}',
                    priority=random.choice(['low', 'medium', 'high']),
                    due_date=timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
                    status=random.choice(['open', 'in_progress', 'completed'])
                )

            # Создаем и сохраняем 30 экземпляров модели Application для каждой вакансии
            for j in range(30):
                applicant_email = f'applicant{i*30+j+30}@example.com'
                if not User.objects.filter(email=applicant_email).exists():
                    applicant = User.objects.create_user(
                        email=applicant_email,
                        password='password123',
                        role='candidate'
                    )
                else:
                    applicant = User.objects.get(email=applicant_email)
                Application.objects.create(
                    job=job,
                    applicant=applicant,
                    cover_letter=f'CoverLetter{j}',
                    created_at=timezone.now(),
                    status=random.choice(['submitted', 'reviewed', 'accepted', 'rejected'])
                )

            # Создаем и сохраняем 30 экземпляров модели GuestFeedback для каждой вакансии
            for j in range(30):
                GuestFeedback.objects.create(
                    job=job,
                    email=f'guest{j}@example.com',
                    message=f'Message{j}',
                    created_at=timezone.now(),
                    phone_number='+1234567890'
                )


@transaction.atomic
def create_requests_data():
    for i in range(30):
        employer_email = f'employer{i}@example.com'
        if User.objects.filter(email=employer_email).exists():
            employer = User.objects.get(email=employer_email)
            job_request = JobRequest.objects.create(
                employer=employer,
                title=f'RequestTitle{i}',
                description=f'Description{i}',
                requirements=f'Requirements{i}',
                created_at=timezone.now(),
                status=random.choice(['pending', 'processing', 'completed'])
            )

            # Если запрос на работу находится в статусе "processing" или "completed",
            # создаем связанную вакансию
            if job_request.status in ['processing', 'completed']:
                recruiter_email = f'recruiter{i}@example.com'
                if User.objects.filter(email=recruiter_email).exists():
                    recruiter = User.objects.get(email=recruiter_email)
                    Job.objects.create(
                        title=f'Job for Request {i}',
                        recruiter=recruiter,
                        description=f'Description for Job {i}',
                        requirements=f'Requirements for Job {i}',
                        salary=random.randint(1000, 5000),
                        created_at=timezone.now(),
                        status=random.choice(['open', 'closed'])
                    )

# Запускаем функции для создания данных для каждого приложения
create_accounts_data()
create_jobs_data()
create_requests_data()
