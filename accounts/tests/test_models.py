import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import User, CandidateProfile, ClientProfile, RecruiterProfile, Task
from datetime import date

User = get_user_model()

# User model tests
@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email='test@example.com', password='password123')
    assert user.email == 'test@example.com'
    assert user.is_active is False
    assert user.check_password('password123')

@pytest.mark.django_db
def test_create_superuser():
    superuser = User.objects.create_superuser(email='super@example.com', password='password123')
    assert superuser.email == 'super@example.com'
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True


@pytest.mark.django_db
def test_user_email_validation():
    with pytest.raises(ValueError):
        User.objects.create_user(email='invalid-email', password='password123')

@pytest.mark.django_db
def test_user_string_representation():
    user = User.objects.create_user(email='user@example.com', password='password123')
    assert str(user) == 'user@example.com'

@pytest.mark.django_db
def test_user_full_name_candidate():
    user = User.objects.create_user(email='candidate@example.com', password='password123', role='candidate')
    profile = CandidateProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        date_of_birth=date(1990, 1, 1),
        skills='Python, Django'
    )
    assert user.get_full_name() == 'John Doe'

@pytest.mark.django_db
def test_user_full_name_client():
    user = User.objects.create_user(email='client@example.com', password='password123', role='client')
    profile = ClientProfile.objects.create(
        user=user,
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        company_name='Company',
        industry='IT'
    )
    assert user.get_full_name() == 'Company'  # Изменено для отображения имени компании

@pytest.mark.django_db
def test_user_full_name_recruiter():
    user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    assert user.get_full_name() == 'John Doe'

@pytest.mark.django_db
def test_user_verification_token_generation():
    user = User.objects.create_user(email='user@example.com', password='password123')
    token = user.generate_verification_token()
    assert len(token) == 64

@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email='', password='password123')

# CandidateProfile model tests
@pytest.mark.django_db
def test_candidate_profile_creation():
    user = User.objects.create_user(email='candidate@example.com', password='password123', role='candidate')
    profile = CandidateProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        date_of_birth=date(1990, 1, 1),
        skills='Python, Django'
    )
    assert profile.user == user
    assert profile.first_name == 'John'
    assert profile.last_name == 'Doe'

@pytest.mark.django_db
def test_candidate_profile_string_representation():
    user = User.objects.create_user(email='candidate@example.com', password='password123', role='candidate')
    profile = CandidateProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        date_of_birth=date(1990, 1, 1),
        skills='Python, Django'
    )
    assert str(profile) == 'Profil kandydata: John Doe'

# ClientProfile model tests
@pytest.mark.django_db
def test_client_profile_creation():
    user = User.objects.create_user(email='client@example.com', password='password123', role='client')
    profile = ClientProfile.objects.create(
        user=user,
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        company_name='Company',
        industry='IT'
    )
    assert profile.user == user
    assert profile.company_name == 'Company'

@pytest.mark.django_db
def test_client_profile_string_representation():
    user = User.objects.create_user(email='client@example.com', password='password123', role='client')
    profile = ClientProfile.objects.create(
        user=user,
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        company_name='Company',
        industry='IT'
    )
    assert str(profile) == 'Profil pracodawcy Company'

# RecruiterProfile model tests
@pytest.mark.django_db
def test_recruiter_profile_creation():
    user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    assert profile.user == user
    assert profile.first_name == 'John'

@pytest.mark.django_db
def test_recruiter_profile_string_representation():
    user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    assert str(profile) == 'Profil rekrutera: John Doe'

# Task model tests
@pytest.mark.django_db
def test_task_creation_by_recruiter():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=recruiter,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    task = Task.objects.create(
        created_by=recruiter,
        title='Task Title',
        description='Task Description',
        priority='high',
        due_date=date(2023, 12, 31)
    )
    assert task.created_by == recruiter
    assert task.title == 'Task Title'
    assert task.priority == 'high'

@pytest.mark.django_db
def test_task_creation_by_non_recruiter():
    non_recruiter = User.objects.create_user(email='nonrecruiter@example.com', password='password123', role='client')
    with pytest.raises(ValidationError):
        Task.objects.create(
            created_by=non_recruiter,
            title='Task Title',
            description='Task Description',
            priority='high',
            due_date=date(2023, 12, 31)
        )

@pytest.mark.django_db
def test_task_status_change():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=recruiter,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    task = Task.objects.create(
        created_by=recruiter,
        title='Task Title',
        description='Task Description',
        priority='high',
        due_date=date(2023, 12, 31)
    )
    task.change_status('completed')
    assert task.status == 'completed'

@pytest.mark.django_db
def test_task_string_representation():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=recruiter,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    task = Task.objects.create(
        created_by=recruiter,
        title='Task Title',
        description='Task Description',
        priority='high',
        due_date=date(2023, 12, 31)
    )
    assert str(task) == 'Task Title'

@pytest.mark.django_db
def test_task_priority_validation():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    profile = RecruiterProfile.objects.create(
        user=recruiter,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    with pytest.raises(ValidationError):
        Task.objects.create(
            created_by=recruiter,
            title='Task Title',
            description='Task Description',
            priority='invalid_priority',  # Invalid priority
            due_date=date(2023, 12, 31)
        )

@pytest.mark.django_db
def test_user_roles_and_profiles_association():
    candidate_user = User.objects.create_user(email='candidate@example.com', password='password123', role='candidate')
    candidate_profile = CandidateProfile.objects.create(
        user=candidate_user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        date_of_birth=date(1990, 1, 1),
        skills='Python, Django'
    )
    assert candidate_user.candidate_profile == candidate_profile

    client_user = User.objects.create_user(email='client@example.com', password='password123', role='client')
    client_profile = ClientProfile.objects.create(
        user=client_user,
        phone_number='+1234567890',
        location='City',
        bio='Bio',
        company_name='Company',
        industry='IT'
    )
    assert client_user.client_profile == client_profile

    recruiter_user = User.objects.create_user(email='recruiter@example.com', password='password123', role='recruiter')
    recruiter_profile = RecruiterProfile.objects.create(
        user=recruiter_user,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        location='City',
        bio='Bio'
    )
    assert recruiter_user.recruiter_profile == recruiter_profile
