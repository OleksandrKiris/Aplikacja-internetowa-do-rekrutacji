import pytest
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from accounts.admin import CustomUserAdmin, CandidateProfileAdmin, ClientProfileAdmin, RecruiterProfileAdmin, TaskAdmin
from accounts.forms import AdminUserCreationForm
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from django.contrib.auth import get_user_model

User = get_user_model()


class MockRequest:
    def __init__(self, user):
        self.user = user


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(email='admin@example.com', password='password')


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(email='user@example.com', password='password', role='client')


@pytest.fixture
def candidate_user(db):
    return User.objects.create_user(email='candidate@example.com', password='password', role='candidate')


@pytest.fixture
def client_user(db):
    return User.objects.create_user(email='client@example.com', password='password', role='client')


@pytest.fixture
def recruiter_user(db):
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    RecruiterProfile.objects.get_or_create(user=user, defaults={'first_name': 'First', 'last_name': 'Last',
                                                                'phone_number': '+123456789', 'location': 'Location',
                                                                'bio': 'Bio'})
    return user


@pytest.fixture
def candidate_profile(candidate_user, db):
    return CandidateProfile.objects.create(user=candidate_user, first_name='First', last_name='Last',
                                           phone_number='+123456789', location='Location', bio='Bio',
                                           date_of_birth='1990-01-01', skills='Skills')


@pytest.fixture
def client_profile(client_user, db):
    return ClientProfile.objects.create(user=client_user, phone_number='+123456789', location='Location', bio='Bio',
                                        company_name='Company', industry='Industry')


@pytest.fixture
def recruiter_profile(recruiter_user, db):
    return RecruiterProfile.objects.get_or_create(user=recruiter_user,
                                                  defaults={'first_name': 'First', 'last_name': 'Last',
                                                            'phone_number': '+123456789', 'location': 'Location',
                                                            'bio': 'Bio'})[0]


@pytest.fixture
def task(recruiter_user, db):
    print(f"Creating task with recruiter_user: {recruiter_user.email}")
    assert hasattr(recruiter_user, 'recruiter_profile'), "recruiter_user does not have a recruiter profile"
    return Task.objects.create(created_by=recruiter_user, title='Task', description='Description', priority='medium',
                               due_date='2023-12-31', status='open')


@pytest.fixture
def site():
    return AdminSite()


@pytest.mark.django_db
def test_custom_user_admin(admin_user, site):
    ma = CustomUserAdmin(User, site)
    assert ma.list_display == ('email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'role')
    assert ma.search_fields == ('email',)
    assert ma.list_filter == ('is_active', 'is_staff', 'is_superuser', 'role')


@pytest.mark.django_db
def test_candidate_profile_admin(candidate_profile, site):
    ma = CandidateProfileAdmin(CandidateProfile, site)
    assert ma.list_display == ('user', 'first_name', 'last_name', 'phone_number', 'location')
    assert ma.search_fields == ('user__email', 'first_name', 'last_name')
    assert ma.ordering == ('user',)


@pytest.mark.django_db
def test_client_profile_admin(client_profile, site):
    ma = ClientProfileAdmin(ClientProfile, site)
    assert ma.list_display == ('user', 'company_name', 'industry', 'phone_number', 'location')
    assert ma.search_fields == ('user__email', 'company_name')
    assert ma.ordering == ('company_name',)


@pytest.mark.django_db
def test_recruiter_profile_admin(recruiter_profile, site):
    ma = RecruiterProfileAdmin(RecruiterProfile, site)
    assert ma.list_display == ('user', 'first_name', 'last_name', 'phone_number', 'location')
    assert ma.search_fields == ('user__email', 'first_name', 'last_name')
    assert ma.ordering == ('user',)


@pytest.mark.django_db
def test_task_admin(task, site):
    ma = TaskAdmin(Task, site)
    assert ma.list_display == ('title', 'priority', 'status', 'due_date', 'created_by')
    assert ma.search_fields == ('title', 'created_by__email')
    assert ma.list_filter == ('priority', 'status', 'due_date')
    assert ma.ordering == ('due_date',)


@pytest.mark.django_db
def test_create_recruiter_by_non_superuser_raises_error(normal_user, site):
    ma = CustomUserAdmin(User, site)
    request = MockRequest(user=normal_user)
    new_user = User(email='newrecruiter@example.com', role='recruiter')
    form = AdminUserCreationForm(
        data={'email': 'newrecruiter@example.com', 'role': 'recruiter', 'password1': 'password',
              'password2': 'password'})
    with pytest.raises(ValidationError):
        ma.save_model(request, new_user, form, change=False)


@pytest.mark.django_db
def test_create_user_creates_profile(admin_user, site):
    ma = CustomUserAdmin(User, site)
    request = MockRequest(user=admin_user)
    new_user = User(email='newcandidate@example.com', role='candidate')
    form = AdminUserCreationForm(
        data={'email': 'newcandidate@example.com', 'role': 'candidate', 'password1': 'password',
              'password2': 'password'})
    ma.save_model(request, new_user, form, change=False)
    assert CandidateProfile.objects.filter(user=new_user).exists()
