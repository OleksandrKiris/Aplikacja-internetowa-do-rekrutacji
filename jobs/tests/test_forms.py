import pytest

from django.contrib.auth.models import User
from jobs.forms import JobForm, ApplicationForm, GuestFeedbackForm


@pytest.mark.django_db
def test_job_form_valid_data():
    form = JobForm(data={
        'title': 'Test Job',
        'description': 'This is a test job.',
        'requirements': 'Requirements for test job.',
        'salary': '5000.00',
        'status': 'open',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_job_form_invalid_data():
    form = JobForm(data={})
    assert not form.is_valid()
    assert len(form.errors) == 4  # All fields except salary are required


@pytest.mark.django_db
def test_application_form_valid_data():
    form = ApplicationForm(data={
        'cover_letter': 'This is my cover letter.'
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_application_form_invalid_data():
    form = ApplicationForm(data={})
    assert form.is_valid()  # Cover letter is not required in the model


@pytest.mark.django_db
def test_guest_feedback_form_valid_data():
    form = GuestFeedbackForm(data={
        'email': 'test@example.com',
        'message': 'This is a feedback message.',
        'phone_number': '123456789',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_guest_feedback_form_invalid_data():
    form = GuestFeedbackForm(data={
        'email': 'invalid-email',
        'message': '',
    })
    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'message' in form.errors


@pytest.mark.django_db
def test_guest_feedback_form_optional_phone_number():
    form = GuestFeedbackForm(data={
        'email': 'test@example.com',
        'message': 'This is a feedback message.',
    })
    assert form.is_valid()


# Тест для проверки валидности формы с недопустимым статусом в форме работы
@pytest.mark.django_db
def test_job_form_invalid_status():
    form = JobForm(data={
        'title': 'Test Job',
        'description': 'This is a test job.',
        'requirements': 'Requirements for test job.',
        'salary': '5000.00',
        'status': 'invalid_status',  # Попробуйте ввести недопустимый статус
    })
    assert not form.is_valid()  # Ожидается, что форма будет невалидной из-за недопустимого статуса


# Тест для проверки обязательности поля "Тема" в форме обратной связи
@pytest.mark.django_db
def test_guest_feedback_form_required_email():
    form = GuestFeedbackForm(data={
        'message': 'This is a feedback message.',
        'phone_number': '123456789',
    })
    assert not form.is_valid()  # Ожидается, что форма будет невалидной из-за отсутствия email


