import pytest
from django.contrib.auth import get_user_model
from requests.forms import JobRequestForm, JobRequestStatusUpdateForm
from requests.models import JobRequest

User = get_user_model()


@pytest.mark.django_db
def test_job_request_form_valid():
    employer = User.objects.create_user(email='employer@example.com', password='password')

    # Создайте рекрутера
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')

    job_request = JobRequest(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter  # Используйте созданного рекрутера
    )
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
        'recruiter': recruiter.id  # Используйте идентификатор созданного рекрутера
    }
    form = JobRequestForm(data=form_data, instance=job_request)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_job_request_form_invalid_recruiter_change():
    employer = User.objects.create_user(email='employer@example.com', password='password')
    recruiter1 = User.objects.create_user(email='recruiter1@example.com', password='password')
    recruiter2 = User.objects.create_user(email='recruiter2@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter1
    )
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
        'recruiter': recruiter2.id
    }
    form = JobRequestForm(data=form_data, instance=job_request)
    assert not form.is_valid()
    assert 'recruiter' in form.errors


@pytest.mark.django_db
def test_job_request_status_update_form_valid():
    employer = User.objects.create_user(email='employer@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter
    )
    form_data = {
        'new_status': JobRequest.RequestStatus.PROCESSING,
        'message': 'Processing job request'
    }
    form = JobRequestStatusUpdateForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_job_request_status_update_form_invalid_status():
    employer = User.objects.create_user(email='employer@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter
    )
    form_data = {
        'new_status': 'invalid_status',
        'message': 'Invalid status update'
    }
    form = JobRequestStatusUpdateForm(data=form_data)
    assert not form.is_valid()
    assert 'new_status' in form.errors


@pytest.mark.django_db
def test_job_request_form_readonly_recruiter():
    employer = User.objects.create_user(email='employer@example.com', password='password')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter
    )
    form = JobRequestForm(instance=job_request)
    assert form.fields['recruiter'].widget.attrs.get('readonly')


@pytest.mark.django_db
def test_job_request_form_clean_method():
    employer = User.objects.create_user(email='employer@example.com', password='password')
    recruiter1 = User.objects.create_user(email='recruiter1@example.com', password='password')
    job_request = JobRequest.objects.create(
        employer=employer,
        title='Test Job Request',
        description='Test description',
        requirements='Test requirements',
        status=JobRequest.RequestStatus.PENDING,
        recruiter=recruiter1
    )
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
        'recruiter': recruiter1.id
    }
    form = JobRequestForm(data=form_data, instance=job_request)
    form.instance.recruiter = recruiter1
    if form.is_valid():
        cleaned_data = form.cleaned_data
        assert cleaned_data['recruiter'] == recruiter1
    else:
        pytest.fail('Form is not valid when it should be')



@pytest.mark.django_db
def test_job_request_status_update_form_no_message_valid():
    form_data = {
        'new_status': JobRequest.RequestStatus.PROCESSING,
    }
    form = JobRequestStatusUpdateForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
def test_job_request_status_update_form_invalid_status():
    form_data = {
        'new_status': 'invalid_status',
        'message': 'Invalid status update'
    }
    form = JobRequestStatusUpdateForm(data=form_data)
    assert not form.is_valid()
    assert 'new_status' in form.errors


@pytest.mark.django_db
def test_job_request_form_invalid_recruiter():
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
        'recruiter': 'nonexistent_recruiter_id'
    }
    form = JobRequestForm(data=form_data)
    assert not form.is_valid()
    assert 'recruiter' in form.errors


@pytest.mark.django_db
def test_job_request_form_invalid_status():
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': 'invalid_status',
        'recruiter': None
    }
    form = JobRequestForm(data=form_data)
    assert not form.is_valid()
    assert 'status' in form.errors


@pytest.mark.django_db
def test_job_request_form_missing_recruiter():
    form_data = {
        'title': 'Test Job Request',
        'description': 'Test description',
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
    }
    form = JobRequestForm(data=form_data)
    assert not form.is_valid()
    assert 'recruiter' in form.errors


@pytest.mark.django_db
def test_job_request_form_long_description():
    long_description = 'a' * 1001  # Assuming the maximum length is 1000 characters
    form_data = {
        'title': 'Test Job Request',
        'description': long_description,
        'requirements': 'Test requirements',
        'status': JobRequest.RequestStatus.PENDING,
        'recruiter': None
    }
    form = JobRequestForm(data=form_data)
    assert not form.is_valid()
    assert 'description' in form.errors
