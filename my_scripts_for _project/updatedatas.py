import os
import django
import random
from django.utils import timezone
from django.db import transaction
from faker import Faker

# Настройка окружения Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
django.setup()

# Импорт моделей
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, User, Task
from jobs.models import Job, Application, GuestFeedback
from requests.models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter
from news.models import News

# Локали для Faker
locales = ['pl_PL', 'de_DE', 'en_US', 'ru_RU', 'uk_UA', 'ka_GE', 'tr_TR']
fake = Faker(locales)

# Constants
ROLE_CHOICES = ['candidate', 'client', 'recruiter']
APPLICATION_STATUS_CHOICES = ['submitted', 'reviewed', 'accepted', 'rejected']
TASK_PRIORITY_CHOICES = ['low', 'medium', 'high']
TASK_STATUS_CHOICES = ['open', 'in_progress', 'completed']
JOB_STATUS_CHOICES = ['open', 'closed']
JOB_REQUEST_STATUS_CHOICES = ['pending', 'processing', 'completed']
NEWS_ROLE_CHOICES = ['candidate', 'client', 'recruiter']


# Helper function to truncate string
def truncate_string(value, max_length):
    if len(value) > max_length:
        return value[:max_length]
    return value


# Helper function to generate a unique email
def generate_unique_email():
    while True:
        email = fake.email()
        if not User.objects.filter(email=email).exists():
            return email


# Создание пользователей и профилей
@transaction.atomic
def create_users_with_profiles():
    users = {role: [] for role in ROLE_CHOICES}

    for role in ROLE_CHOICES:
        print(f"Creating users and profiles for role: {role}")
        for _ in range(10):  # Сократим до 10 пользователей для примера
            email = generate_unique_email()
            password = fake.password()
            user = User.objects.create_user(email=email, password=password, role=role, is_active=True)
            users[role].append(user)

            if role == 'candidate':
                profile = CandidateProfile.objects.create(
                    user=user,
                    first_name=truncate_string(fake.first_name(), 100),
                    last_name=truncate_string(fake.last_name(), 100),
                    phone_number=truncate_string(fake.phone_number(), 15),
                    photo=None,
                    location=truncate_string(fake.city(), 100),
                    bio=fake.text(),
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
                    skills=fake.text()
                )
                print(profile)
            elif role == 'client':
                profile = ClientProfile.objects.create(
                    user=user,
                    phone_number=truncate_string(fake.phone_number(), 15),
                    photo=None,
                    location=truncate_string(fake.city(), 100),
                    bio=fake.text(),
                    company_name=truncate_string(fake.company(), 100),
                    industry=truncate_string(fake.job(), 50)
                )
                print(profile)
            elif role == 'recruiter':
                profile = RecruiterProfile.objects.create(
                    user=user,
                    first_name=truncate_string(fake.first_name(), 100),
                    last_name=truncate_string(fake.last_name(), 100),
                    phone_number=truncate_string(fake.phone_number(), 15),
                    photo=None,
                    location=truncate_string(fake.city(), 100),
                    bio=fake.text()
                )
                print(profile)

        # Создание задач для рекрутеров
        if role == 'recruiter':
            print(f"Creating tasks for recruiters")
            for user in users[role]:
                for _ in range(5):
                    task = Task.objects.create(
                        created_by=user,
                        title=truncate_string(fake.job(), 200),
                        description=fake.text(),
                        priority=random.choice(TASK_PRIORITY_CHOICES),
                        due_date=fake.date_this_year(),
                        status=random.choice(TASK_STATUS_CHOICES)
                    )
                    print(task)

    return users


# Создание заданий и заявок на работу
def create_jobs_and_applications(recruiters, candidates):
    jobs = []
    print(f"Creating jobs and applications")
    for recruiter in recruiters:
        for _ in range(5):  # Сократим до 5 вакансий на рекрутера для примера
            job = Job.objects.create(
                title=truncate_string(fake.job(), 200),
                recruiter=recruiter,
                description=fake.text(),
                requirements=fake.text(),
                salary=f"{random.uniform(30000, 100000):.2f}",
                created_at=timezone.now(),
                status=random.choice(JOB_STATUS_CHOICES)
            )
            jobs.append(job)
            print(job)

    for job in jobs:
        for candidate in random.sample(candidates, 3):  # Сократим до 3 заявок на вакансию для примера
            application = Application.objects.create(
                job=job,
                applicant=candidate,
                cover_letter=fake.text(),
                created_at=timezone.now(),
                status=random.choice(APPLICATION_STATUS_CHOICES)
            )
            print(application)

    return jobs


# Создание отзывов и временных отзывов
def create_feedbacks(jobs):
    print(f"Creating feedbacks")
    email_counter = 0
    for job in jobs:
        for _ in range(5):  # Сократим до 5 отзывов на вакансию для примера
            email = f"feedback_{email_counter}@example.com"
            email_counter += 1
            feedback = GuestFeedback.objects.create(
                job=job,
                email=email,
                message=fake.text(),
                created_at=timezone.now(),
                phone_number=truncate_string(fake.phone_number(), 15),
                is_verified=True,
            )
            print(feedback)


# Создание запросов на работу
def create_job_requests(clients, recruiters):
    print(f"Creating job requests")
    for client in clients:
        for _ in range(3):  # Сократим до 3 запросов на клиента для примера
            recruiter = random.choice(recruiters)
            job_request = JobRequest.objects.create(
                employer=client,
                title=truncate_string(fake.job(), 200),
                description=fake.text(),
                requirements=fake.text(),
                created_at=timezone.now(),
                status=random.choice(JOB_REQUEST_STATUS_CHOICES),
                recruiter=recruiter
            )
            print(f"{job_request.title} - {job_request.status}")

            # Создание обновлений статуса для запросов на работу
            for _ in range(2):  # Сократим до 2 обновлений статуса на запрос для примера
                status_update = JobRequestStatusUpdate.objects.create(
                    job_request=job_request,
                    new_status=random.choice(JOB_REQUEST_STATUS_CHOICES),
                    updated_by=recruiter,
                    updated_at=timezone.now(),
                    message=fake.text()
                )
                print(status_update)


# Создание новостей
def create_news():
    print(f"Creating news")
    for _ in range(10):  # Сократим до 10 новостей для примера
        news = News.objects.create(
            title=truncate_string(fake.sentence(), 200),
            content=fake.text(),
            date_posted=timezone.now(),
            role=random.choice(NEWS_ROLE_CHOICES)
        )
        print(news)


# Выполнение функций для создания данных
@transaction.atomic
def populate_database():
    print("Starting database population")
    users = create_users_with_profiles()
    jobs = create_jobs_and_applications(users['recruiter'], users['candidate'])
    create_feedbacks(jobs)
    create_job_requests(users['client'], users['recruiter'])
    create_news()
    print("Database population complete")


# Запуск функции заполнения базы данных
populate_database()
