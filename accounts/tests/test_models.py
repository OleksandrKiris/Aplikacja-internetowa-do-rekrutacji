import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="validemail@example.com", password="password123")
    assert user.email == "validemail@example.com"
    assert user.is_active

@pytest.mark.django_db
def test_create_user_invalid_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="password123")

@pytest.mark.django_db
def test_create_user_invalid_email_format():
    with pytest.raises(ValueError):
        User.objects.create_user(email="invalidemail", password="password123")

@pytest.mark.django_db
def test_create_superuser():
    superuser = User.objects.create_superuser(email="superuser@example.com", password="password123")
    assert superuser.is_superuser
    assert superuser.is_staff

@pytest.mark.django_db
def test_candidate_profile():
    user = User.objects.create_user(email="candidate@example.com", password="password", role='candidate')
    candidate = CandidateProfile.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="+1234567890",
        location="New York",
        bio="Sample bio",
        date_of_birth="1990-01-01"
    )
    assert str(candidate) == "Profil kandydata: John Doe"
    assert candidate.bio == "Sample bio"

@pytest.mark.django_db
def test_client_profile():
    user = User.objects.create_user(email="client@example.com", password="password", role='client')
    client = ClientProfile.objects.create(
        user=user,
        phone_number="+1234567890",
        photo="path/to/photo.jpg",
        location="Los Angeles",
        bio="Client bio",
        company_name="Company Inc",
        industry="Technology"
    )
    assert str(client) == "Profil pracodawcy Company Inc"
    assert client.industry == "Technology"

@pytest.mark.django_db
def test_recruiter_profile():
    user = User.objects.create_user(email="recruiter@example.com", password="password", role='recruiter')
    recruiter = RecruiterProfile.objects.create(
        user=user,
        first_name="Alice",
        last_name="Smith",
        phone_number="+1234567890",
        photo="path/to/photo.jpg",
        location="Chicago",
        bio="Recruiter bio"
    )
    assert str(recruiter) == "Profil rekrutera: Alice Smith"
    assert recruiter.location == "Chicago"

def test_phone_number_validator():
    with pytest.raises(ValidationError):
        CandidateProfile(phone_number="incorrect").full_clean()
    with pytest.raises(ValidationError):
        ClientProfile(phone_number="incorrect").full_clean()
    with pytest.raises(ValidationError):
        RecruiterProfile(phone_number="incorrect").full_clean()

@pytest.mark.django_db
def test_task_creation_and_status_change_by_recruiter():
    user = User.objects.create_user(email="recruiter@example.com", password="password", role='recruiter')
    RecruiterProfile.objects.create(
        user=user,
        first_name="Alice",
        last_name="Smith",
        phone_number="+1234567890"
    )
    task = Task.objects.create(
        created_by=user,
        title="Recruiter Task",
        description="Task for recruiter",
        priority="medium",
        due_date="2023-01-01"
    )
    assert task.status == "open"
    task.change_status("completed")
    task.refresh_from_db()
    assert task.status == "completed"

@pytest.mark.django_db
def test_task_creation_by_non_recruiter():
    user = User.objects.create_user(email="user@example.com", password="password", role='candidate')
    with pytest.raises(ValidationError):
        Task.objects.create(
            created_by=user,
            title="Unauthorized Task",
            description="Should not be created",
            priority="low",
            due_date="2023-02-01"
        )
