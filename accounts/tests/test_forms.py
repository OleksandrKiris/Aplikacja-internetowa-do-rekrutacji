import pytest
from django.contrib.auth import get_user_model
from accounts.forms import (
    UserRegistrationForm, CandidateProfileForm, ClientProfileForm, RecruiterProfileForm,
    UserLoginForm, TaskForm, AdminUserCreationForm, PasswordChangeForm, AdminUserChangeForm
)
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from datetime import date

User = get_user_model()

@pytest.mark.django_db
def test_user_registration_form_valid():
    form_data = {
        'email': 'testuser@example.com',
        'password1': 'TestPassword123',
        'password2': 'TestPassword123',
        'role': 'candidate'
    }
    form = UserRegistrationForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
def test_user_registration_form_invalid():
    form_data = {
        'email': 'invalid-email',
        'password1': 'password',
        'password2': 'password',
        'role': 'candidate'
    }
    form = UserRegistrationForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_candidate_profile_form_valid():
    user = User.objects.create_user(email='candidate@example.com', password='testpassword', role='candidate')
    form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+123456789',
        'location': 'Test Location',
        'bio': 'Test Bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Test Skills'
    }
    form = CandidateProfileForm(data=form_data, instance=CandidateProfile(user=user))
    assert form.is_valid()

@pytest.mark.django_db
def test_candidate_profile_form_invalid():
    form_data = {
        'first_name': '',
        'last_name': 'Doe',
        'phone_number': '123456789',
        'location': 'Test Location',
        'bio': 'Test Bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Test Skills'
    }
    form = CandidateProfileForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_client_profile_form_valid():
    user = User.objects.create_user(email='client@example.com', password='testpassword', role='client')
    form_data = {
        'phone_number': '+123456789',
        'location': 'Test Location',
        'bio': 'Test Bio',
        'company_name': 'Test Company',
        'industry': 'Test Industry'
    }
    form = ClientProfileForm(data=form_data, instance=ClientProfile(user=user))
    assert form.is_valid()

@pytest.mark.django_db
def test_client_profile_form_invalid():
    form_data = {
        'phone_number': '123456789',
        'location': '',
        'bio': 'Test Bio',
        'company_name': 'Test Company',
        'industry': 'Test Industry'
    }
    form = ClientProfileForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_recruiter_profile_form_valid():
    user = User.objects.create_user(email='recruiter@example.com', password='testpassword', role='recruiter')
    form_data = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'phone_number': '+123456789',
        'location': 'Test Location',
        'bio': 'Test Bio'
    }
    form = RecruiterProfileForm(data=form_data, instance=RecruiterProfile(user=user))
    assert form.is_valid()

@pytest.mark.django_db
def test_recruiter_profile_form_invalid():
    form_data = {
        'first_name': '',
        'last_name': 'Doe',
        'phone_number': '123456789',
        'location': 'Test Location',
        'bio': 'Test Bio'
    }
    form = RecruiterProfileForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_user_login_form_valid():
    user = User.objects.create_user(email='testuser@example.com', password='testpassword', is_active=True)
    form_data = {
        'username': 'testuser@example.com',  # Поле 'username', хотя это email
        'password': 'testpassword'
    }
    form = UserLoginForm(data=form_data)
    assert form.is_valid(), form.errors  # Вывод ошибок формы, если она недействительна
    authenticated_user = form.get_user()
    assert authenticated_user is not None
    assert authenticated_user.email == 'testuser@example.com'


@pytest.mark.django_db
def test_user_login_form_invalid():
    form_data = {
        'username': 'invaliduser@example.com',
        'password': 'wrongpassword'
    }
    form = UserLoginForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_task_form_valid():
    user = User.objects.create_user(email='recruiter@example.com', password='testpassword', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=user,
        first_name='Jane',
        last_name='Doe',
        phone_number='+123456789',
        location='Test Location',
        bio='Test Bio'
    )
    form_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'medium',
        'due_date': date.today(),
        'status': 'open'
    }
    form = TaskForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
def test_task_form_invalid():
    form_data = {
        'title': '',
        'description': 'Test Description',
        'priority': 'invalid_priority',
        'due_date': date.today(),
        'status': 'open'
    }
    form = TaskForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_admin_user_creation_form_valid():
    form_data = {
        'email': 'adminuser@example.com',
        'password1': 'TestPassword123',
        'password2': 'TestPassword123',
        'role': 'recruiter'
    }
    form = AdminUserCreationForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
def test_password_change_form_valid():
    form_data = {
        'new_password': 'NewTestPassword123',
        'new_password_confirm': 'NewTestPassword123'
    }
    form = PasswordChangeForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
def test_password_change_form_invalid():
    form_data = {
        'new_password': 'NewTestPassword123',
        'new_password_confirm': 'DifferentPassword123'
    }
    form = PasswordChangeForm(data=form_data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_admin_user_change_form_valid():
    user = User.objects.create_user(email='changetest@example.com', password='testpassword', role='candidate')
    form_data = {
        'email': user.email,
        'password': user.password,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'role': user.role
    }
    form = AdminUserChangeForm(instance=user, data=form_data)
    assert form.is_valid()
