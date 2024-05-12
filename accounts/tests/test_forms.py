import pytest
from django.contrib.auth import get_user_model
from accounts.forms import UserRegistrationForm, CandidateProfileForm, ClientProfileForm, RecruiterProfileForm, UserLoginForm, TaskForm
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task

User = get_user_model()

@pytest.mark.django_db
def test_user_registration_form():
    form_data = {
        'email': 'test@example.com',
        'password1': 'validpassword123',
        'password2': 'validpassword123',
        'role': 'candidate'
    }
    form = UserRegistrationForm(data=form_data)
    assert form.is_valid(), form.errors
    user = form.save()
    assert user.email == 'test@example.com'
    assert user.role == 'candidate'

@pytest.mark.django_db
def test_candidate_profile_form():
    user = User.objects.create_user(email='candidate@example.com', password='password123', role='candidate')
    form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+1234567890',
        'location': 'New York',
        'bio': 'Sample bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Communication'
    }
    form = CandidateProfileForm(data=form_data, instance=CandidateProfile(user=user))
    assert form.is_valid(), form.errors
    profile = form.save()
    assert profile.first_name == 'John'
    assert profile.bio == 'Sample bio'

@pytest.mark.django_db
def test_client_profile_form():
    user = User.objects.create_user(email='client@example.com', password='password123', role='client')
    form_data = {
        'phone_number': '+1234567890',
        'location': 'Los Angeles',
        'bio': 'Client bio',
        'company_name': 'Company Inc',
        'industry': 'Technology'
    }
    form = ClientProfileForm(data=form_data, instance=ClientProfile(user=user))
    assert form.is_valid(), form.errors
    profile = form.save()
    assert profile.company_name == 'Company Inc'

@pytest.mark.django_db
def test_recruiter_profile_form():
    user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    form_data = {
        'first_name': 'Alice',
        'last_name': 'Smith',
        'phone_number': '+1234567890',
        'location': 'Chicago',
        'bio': 'Recruiter bio'
    }
    form = RecruiterProfileForm(data=form_data, instance=RecruiterProfile(user=user))
    assert form.is_valid(), form.errors
    profile = form.save()
    assert profile.first_name == 'Alice'

@pytest.mark.django_db
def test_user_login_form():
    user = User.objects.create_user(email='user@example.com', password='testpassword', role='candidate')
    form_data = {
        'username': 'user@example.com',
        'password': 'testpassword'
    }
    form = UserLoginForm(data=form_data)
    assert form.is_valid(), form.errors
    authenticated_user = form.get_user()
    assert authenticated_user == user

@pytest.mark.django_db
def test_task_form():
    user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    RecruiterProfile.objects.create(user=user)  # Ensure the user is a recruiter
    form_data = {
        'title': 'New Task',
        'description': 'Task description',
        'priority': 'medium',
        'due_date': '2023-01-01',
        'status': 'open'
    }
    form = TaskForm(data=form_data)
    assert form.is_valid(), form.errors
    task = form.save(commit=False)
    task.created_by = user
    task.save()
    assert Task.objects.filter(title='New Task').exists()
