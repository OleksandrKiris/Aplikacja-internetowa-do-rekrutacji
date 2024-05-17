import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from requests.models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter
from accounts.models import RecruiterProfile

User = get_user_model()


@pytest.mark.django_db
def test_create_job_request():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=user,
        title='Test Job',
        description='Job Description',
        requirements='Job Requirements',
        status='pending',
        recruiter=recruiter
    )
    assert job_request.title == 'Test Job'
    assert job_request.description == 'Job Description'
    assert job_request.requirements == 'Job Requirements'
    assert job_request.status == 'pending'
    assert job_request.employer == user
    assert job_request.recruiter == recruiter


@pytest.mark.django_db
def test_update_job_request_status():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=user,
        title='Test Job',
        description='Job Description',
        requirements='Job Requirements',
        status='pending',
        recruiter=recruiter
    )
    status_update = JobRequestStatusUpdate.objects.create(
        job_request=job_request,
        new_status='completed',
        updated_by=recruiter,
        message='Job completed successfully'
    )
    assert status_update.new_status == 'completed'
    assert status_update.updated_by == recruiter
    assert status_update.message == 'Job completed successfully'
    assert status_update.job_request == job_request


@pytest.mark.django_db
def test_favorite_recruiter():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter_user = User.objects.create_user(email='recruiter@example.com', password='password')
    recruiter_profile = RecruiterProfile.objects.create(user=recruiter_user, first_name="Test", last_name="Recruiter")
    favorite = FavoriteRecruiter.objects.create(user=user, recruiter=recruiter_profile)
    assert favorite.user == user
    assert favorite.recruiter == recruiter_profile


@pytest.mark.django_db
def test_job_request_str():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=user,
        title='Test Job',
        description='Job Description',
        requirements='Job Requirements',
        status='pending',
        recruiter=recruiter
    )
    assert str(job_request) == 'Test Job - Oczekujące'


@pytest.mark.django_db
def test_job_request_status_update_str():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=user,
        title='Test Job',
        description='Job Description',
        requirements='Job Requirements',
        status='pending',
        recruiter=recruiter
    )
    status_update = JobRequestStatusUpdate.objects.create(
        job_request=job_request,
        new_status='completed',
        updated_by=recruiter,
        message='Job completed successfully'
    )
    assert str(status_update) == 'Test Job - Zakończone'


@pytest.mark.django_db
def test_create_job_request_without_required_fields():
    user = User.objects.create_user(email='user@example.com', password='password')
    with pytest.raises(IntegrityError):
        JobRequest.objects.create(
            employer=user,
            description='Job Description',
            requirements='Job Requirements',
            status='pending'
        )


@pytest.mark.django_db
def test_create_job_request_status_update_without_required_fields():
    user = User.objects.create_user(email='user@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=user,
        title='Test Job',
        description='Job Description',
        requirements='Job Requirements',
        status='pending',
        recruiter=recruiter
    )
    with pytest.raises(IntegrityError):
        JobRequestStatusUpdate.objects.create(
            job_request=job_request,
            updated_by=recruiter,
            new_status=None  # Явно указываем на отсутствие значения
        )


@pytest.mark.django_db
def test_create_favorite_recruiter_without_required_fields():
    user = User.objects.create_user(email='user@example.com', password='password')
    with pytest.raises(IntegrityError):
        FavoriteRecruiter.objects.create(user=user)
