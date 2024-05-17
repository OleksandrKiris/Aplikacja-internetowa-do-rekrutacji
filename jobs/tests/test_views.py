import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from jobs.models import Job, Application, GuestFeedback, Like, Favorite, TempGuestFeedback
from accounts.models import CandidateProfile, RecruiterProfile
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def recruiter():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    user.is_active = True
    user.save()
    RecruiterProfile.objects.create(user=user, first_name='John', last_name='Doe', phone_number='+123456789',
                                    location='City', bio='Recruiter bio')
    return user


@pytest.fixture
def candidate():
    user = User.objects.create_user(email='candidate@example.com', password='password', role='candidate')
    user.is_active = True
    user.save()
    CandidateProfile.objects.create(user=user, first_name='Jane', last_name='Smith', phone_number='+123456789',
                                    location='City', bio='Candidate bio', date_of_birth='1990-01-01',
                                    skills='Python, Django')
    return user


@pytest.fixture
def job(recruiter):
    return Job.objects.create(
        title='Test Job',
        recruiter=recruiter,
        description='This is a test job.',
        requirements='Requirements for test job.',
        salary=Decimal('5000.00'),
        status='open',
    )


@pytest.mark.django_db
def test_job_list_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.get(reverse('jobs:job_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_common_create_job_view(client, recruiter):
    client.login(email='recruiter@example.com', password='password')
    response = client.post(reverse('jobs:create_job'), {
        'title': 'New Job',
        'description': 'New job description',
        'requirements': 'Job requirements',
        'salary': '6000.00',
        'status': 'open',
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного создания
    assert Job.objects.filter(title='New Job').exists()


@pytest.mark.django_db
def test_common_job_detail_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.get(reverse('jobs:job_detail', args=[job.id]))
    assert response.status_code == 200
    assert 'job' in response.context
    assert response.context['job'] == job


@pytest.mark.django_db
def test_create_application_view(client, candidate, recruiter, job):
    client.login(email='candidate@example.com', password='password')
    response = client.post(reverse('jobs:create_application', args=[job.id]), {
        'cover_letter': 'This is my cover letter'
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного создания заявки
    assert Application.objects.filter(job=job, applicant=candidate).exists()


@pytest.mark.django_db
def test_guest_feedback_view(client, recruiter, job):
    response = client.post(reverse('jobs:guest_feedback', args=[job.id]), {
        'email': 'guest@example.com',
        'message': 'This is my feedback',
        'phone_number': '1234567890'
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного создания обратной связи
    temp_feedback = TempGuestFeedback.objects.filter(job=job, email='guest@example.com').exists()
    assert temp_feedback


@pytest.mark.django_db
def test_update_job_status(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.post(reverse('jobs:update_job_status', args=[job.id]), {
        'title': 'Updated Job',
        'description': 'Updated description',
        'requirements': 'Updated requirements',
        'salary': '7000.00',
        'status': 'closed',
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного обновления работы
    job.refresh_from_db()
    assert job.title == 'Updated Job'
    assert job.description == 'Updated description'
    assert job.requirements == 'Updated requirements'
    assert job.salary == Decimal('7000.00')
    assert job.status == 'closed'


@pytest.mark.django_db
def test_like_job(client, candidate, recruiter, job):
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:like_job', args=[job.id]))
    assert response.status_code == 302  # Проверка перенаправления после лайка
    assert Like.objects.filter(user=candidate, job=job).exists()


@pytest.mark.django_db
def test_favorite_job(client, candidate, recruiter, job):
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:favorite_job', args=[job.id]))
    assert response.status_code == 302  # Проверка перенаправления после добавления в избранное
    assert Favorite.objects.filter(user=candidate, job=job).exists()


@pytest.mark.django_db
def test_verify_feedback_view(client, recruiter, job):
    temp_feedback = TempGuestFeedback.objects.create(
        job=job,
        email='guest@example.com',
        message='This is my feedback',
        phone_number='1234567890',
        verification_token='testtoken'
    )
    response = client.get(reverse('jobs:guest_feedback_verify', args=['testtoken']))
    assert response.status_code == 302
    assert GuestFeedback.objects.filter(job=job, email='guest@example.com', is_verified=True).exists()


@pytest.mark.django_db
def test_guest_applications_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=None,  # Заявка без назначенного заявителя
        cover_letter='This is a guest application.',
        status='submitted'
    )
    response = client.get(reverse('jobs:guest_applications'))
    assert response.status_code == 200
    assert 'applications' in response.context
    assert len(response.context['applications']) == 1


@pytest.mark.django_db
def test_recruiter_applications_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=recruiter,
        cover_letter='This is a cover letter.',
        status='submitted'
    )
    response = client.get(reverse('jobs:recruiter_applications'))
    assert response.status_code == 200
    assert 'applications' in response.context
    assert len(response.context['applications']) == 1


@pytest.mark.django_db
def test_registered_applications_for_job_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=recruiter,
        cover_letter='This is a cover letter.',
        status='submitted'
    )
    response = client.get(reverse('jobs:registered_applications_for_job', args=[job.id]))
    assert response.status_code == 200
    assert 'applications' in response.context
    assert len(response.context['applications']) == 1


@pytest.mark.django_db
def test_guest_applications_view(client, recruiter, job):
    # Авторизуемся как рекрутер
    client.login(email='recruiter@example.com', password='password')

    # Создаем заявку без назначенного заявителя
    application = Application.objects.create(
        job=job,
        cover_letter='This is a guest application.',
        status='submitted'
    )

    # Проверяем, что страница загружается корректно и что заявка была добавлена
    response = client.get(reverse('jobs:guest_applications'))
    assert response.status_code == 200
    assert 'applications' in response.context
    assert len(response.context['applications']) == 1


@pytest.mark.django_db
def test_update_application_status(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=recruiter,
        cover_letter='This is a cover letter.',
        status='submitted'
    )
    response = client.post(reverse('jobs:update_application_status', args=[application.id]), {
        'status': 'accepted'
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного обновления статуса
    application.refresh_from_db()
    assert application.status == 'accepted'


@pytest.mark.django_db
def test_recruiter_job_list_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.get(reverse('jobs:recruiter_job_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_liked_jobs_list_view(client, candidate, job):
    Like.objects.create(user=candidate, job=job)
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:liked_jobs_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_favorited_jobs_list_view(client, candidate, job):
    Favorite.objects.create(user=candidate, job=job)
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:favorited_jobs_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1

@pytest.mark.django_db
def test_update_application_status(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=recruiter,
        cover_letter='This is a cover letter.',
        status='submitted'
    )
    response = client.post(reverse('jobs:update_application_status', args=[application.id]), {
        'status': 'accepted'
    })
    assert response.status_code == 302  # Проверка перенаправления после успешного обновления статуса
    application.refresh_from_db()
    assert application.status == 'accepted'


@pytest.mark.django_db
def test_recruiter_job_list_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.get(reverse('jobs:recruiter_job_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_liked_jobs_list_view(client, candidate, job):
    Like.objects.create(user=candidate, job=job)
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:liked_jobs_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_favorited_jobs_list_view(client, candidate, job):
    Favorite.objects.create(user=candidate, job=job)
    client.login(email='candidate@example.com', password='password')
    response = client.get(reverse('jobs:favorited_jobs_list'))
    assert response.status_code == 200
    assert 'jobs' in response.context
    assert len(response.context['jobs']) == 1


@pytest.mark.django_db
def test_registered_applications_for_job_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    application = Application.objects.create(
        job=job,
        applicant=recruiter,
        cover_letter='This is a cover letter.',
        status='submitted'
    )
    response = client.get(reverse('jobs:registered_applications_for_job', args=[job.id]))
    assert response.status_code == 200
    assert 'applications' in response.context
    assert len(response.context['applications']) == 1





@pytest.mark.django_db
def test_common_job_detail_view(client, recruiter, job):
    client.login(email='recruiter@example.com', password='password')
    response = client.get(reverse('jobs:job_detail', args=[job.id]))
    assert response.status_code == 200
    assert 'job' in response.context
    assert response.context['job'] == job



