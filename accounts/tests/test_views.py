import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Task, CandidateProfile, RecruiterProfile

User = get_user_model()


@pytest.fixture
def create_test_user(db):
    user = User.objects.create_user(email='testuser@example.com', password='strongpassword123', role='candidate')
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def create_recruiter_user(db):
    user = User.objects.create_user(email='recruiter@example.com', password='strongpassword123', role='recruiter')
    user.is_active = True
    user.save()
    RecruiterProfile.objects.create(
        user=user,
        first_name='Recruiter',
        last_name='User',
        phone_number='+1234567890',
        location='Test Location',
        bio='Test bio'
    )
    return user


@pytest.mark.django_db
def test_register_user_view(client):
    url = reverse('accounts:register')
    response = client.get(url)
    assert response.status_code == 200
    assert 'registration/register.html' in [t.name for t in response.templates]

    user_data = {
        'email': 'testuser@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123',
        'role': 'candidate'
    }
    response = client.post(url, data=user_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:create_profile')
    user = User.objects.get(email='testuser@example.com')
    assert user is not None
    assert not user.is_active  # User should not be active until email verification


@pytest.mark.django_db
def test_register_user_view_invalid_data(client):
    url = reverse('accounts:register')
    user_data = {
        'email': 'testuser@example',  # Invalid email
        'password1': 'password123',
        'password2': 'password123',
        'role': 'candidate'
    }
    response = client.post(url, data=user_data)
    assert response.status_code == 200
    assert 'registration/register.html' in [t.name for t in response.templates]
    assert User.objects.filter(email='testuser@example').count() == 0  # User should not be created


@pytest.mark.django_db
def test_create_profile_view(client):
    register_url = reverse('accounts:register')
    user_data = {
        'email': 'testuser@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123',
        'role': 'candidate'
    }
    client.post(register_url, data=user_data)
    user = User.objects.get(email='testuser@example.com')
    client.session['user_id'] = user.id
    client.session.save()

    url = reverse('accounts:create_profile')
    response = client.get(url)
    assert response.status_code == 200
    assert 'registration/create_profile.html' in [t.name for t in response.templates]

    profile_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '+1234567890',
        'location': 'Test Location',
        'bio': 'Test bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Testing'
    }
    response = client.post(url, data=profile_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:registration_complete')
    assert CandidateProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_create_profile_view_invalid_data(client):
    register_url = reverse('accounts:register')
    user_data = {
        'email': 'testuser@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123',
        'role': 'candidate'
    }
    client.post(register_url, data=user_data)
    user = User.objects.get(email='testuser@example.com')
    client.session['user_id'] = user.id
    client.session.save()

    url = reverse('accounts:create_profile')
    profile_data = {
        'first_name': '',  # Missing required field
        'last_name': 'User',
        'phone_number': '+1234567890',
        'location': 'Test Location',
        'bio': 'Test bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Testing'
    }
    response = client.post(url, data=profile_data)
    assert response.status_code == 200
    assert 'registration/create_profile.html' in [t.name for t in response.templates]
    assert CandidateProfile.objects.filter(user=user).count() == 0  # Profile should not be created


@pytest.mark.django_db
def test_verify_email_view(client, create_test_user):
    create_test_user.verification_token = create_test_user.generate_verification_token()
    create_test_user.save()

    url = reverse('accounts:verify_email', kwargs={'token': create_test_user.verification_token})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('accounts:verified')
    create_test_user.refresh_from_db()
    assert create_test_user.is_verified
    assert create_test_user.verification_token is None
    assert create_test_user.is_active


@pytest.mark.django_db
def test_login_view(client, create_test_user):
    url = reverse('accounts:login')
    response = client.get(url)
    assert response.status_code == 200
    assert 'registration/login.html' in [t.name for t in response.templates]

    login_data = {
        'username': 'testuser@example.com',
        'password': 'strongpassword123'
    }
    response = client.post(url, data=login_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:dashboard')
    assert '_auth_user_id' in client.session


@pytest.mark.django_db
def test_login_view_invalid_credentials(client):
    url = reverse('accounts:login')
    login_data = {
        'username': 'testuser@example.com',
        'password': 'wrongpassword'
    }
    response = client.post(url, data=login_data)
    assert response.status_code == 200
    assert 'registration/login.html' in [t.name for t in response.templates]
    assert 'error' in response.context  # Check for error message in context


@pytest.mark.django_db
def test_dashboard_view(client, create_test_user):
    client.force_login(create_test_user)
    url = reverse('accounts:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert 'dashboard/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_dashboard_view_not_logged_in(client):
    url = reverse('accounts:dashboard')
    response = client.get(url)
    assert response.status_code == 302  # Redirect to login
    assert response.url.startswith(reverse('accounts:login'))


@pytest.mark.django_db
def test_profile_detail_view(client, create_test_user):
    profile = CandidateProfile.objects.create(
        user=create_test_user,
        first_name='Test',
        last_name='User',
        phone_number='+1234567890',
        location='Test Location',
        bio='Test bio',
        date_of_birth='1990-01-01',
        skills='Testing'
    )
    client.force_login(create_test_user)
    url = reverse('accounts:profile_detail')
    response = client.get(url)
    assert response.status_code == 200
    assert 'profiles/universal_profile_detail.html' in [t.name for t in response.templates]
    assert response.context['profile'] == profile


@pytest.mark.django_db
def test_profile_detail_view_not_logged_in(client):
    url = reverse('accounts:profile_detail')
    response = client.get(url)
    assert response.status_code == 302  # Redirect to login
    assert response.url.startswith(reverse('accounts:login'))


@pytest.mark.django_db
def test_profile_edit_view(client, create_test_user):
    profile = CandidateProfile.objects.create(
        user=create_test_user,
        first_name='Test',
        last_name='User',
        phone_number='+1234567890',
        location='Test Location',
        bio='Test bio',
        date_of_birth='1990-01-01',
        skills='Testing'
    )
    client.force_login(create_test_user)
    url = reverse('accounts:profile_edit')
    response = client.get(url)
    assert response.status_code == 200
    assert 'profiles/universal_profile_edit.html' in [t.name for t in response.templates]

    updated_profile_data = {
        'first_name': 'Updated',
        'last_name': 'User',
        'phone_number': '+1234567890',
        'location': 'Updated Location',
        'bio': 'Updated bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Updated skills'
    }
    response = client.post(url, data=updated_profile_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:dashboard')
    profile.refresh_from_db()
    assert profile.first_name == 'Updated'
    assert profile.location == 'Updated Location'


@pytest.mark.django_db
def test_profile_edit_view_invalid_data(client, create_test_user):
    profile = CandidateProfile.objects.create(
        user=create_test_user,
        first_name='Test',
        last_name='User',
        phone_number='+1234567890',
        location='Test Location',
        bio='Test bio',
        date_of_birth='1990-01-01',
        skills='Testing'
    )
    client.force_login(create_test_user)
    url = reverse('accounts:profile_edit')
    updated_profile_data = {
        'first_name': '',  # Invalid data
        'last_name': 'User',
        'phone_number': '+1234567890',
        'location': 'Updated Location',
        'bio': 'Updated bio',
        'date_of_birth': '1990-01-01',
        'skills': 'Updated skills'
    }
    response = client.post(url, data=updated_profile_data)
    assert response.status_code == 200
    assert 'profiles/universal_profile_edit.html' in [t.name for t in response.templates]
    profile.refresh_from_db()
    assert profile.first_name == 'Test'  # Ensure the profile was not updated


@pytest.mark.django_db
def test_task_create_view(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    url = reverse('accounts:task_create')
    response = client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]

    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'medium',
        'due_date': '2024-12-31',
        'status': 'open'
    }
    response = client.post(url, data=task_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:task_list')
    task = Task.objects.get(title='Test Task')
    assert task is not None
    assert task.created_by == create_recruiter_user


@pytest.mark.django_db
def test_task_create_view_invalid_data(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    url = reverse('accounts:task_create')
    task_data = {
        'title': '',  # Invalid data
        'description': 'Test Description',
        'priority': 'medium',
        'due_date': '2024-12-31',
        'status': 'open'
    }
    response = client.post(url, data=task_data)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]
    assert Task.objects.filter(title='').count() == 0  # Task should not be created


@pytest.mark.django_db
def test_task_update_view(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    task = Task.objects.create(
        title='Old Task',
        description='Old Description',
        priority='low',
        due_date='2024-12-31',
        status='open',
        created_by=create_recruiter_user
    )
    url = reverse('accounts:task_update', kwargs={'task_id': task.id})
    response = client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]

    updated_task_data = {
        'title': 'Updated Task',
        'description': 'Updated Description',
        'priority': 'high',
        'due_date': '2024-12-31',
        'status': 'in_progress'
    }
    response = client.post(url, data=updated_task_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:task_list')
    task.refresh_from_db()
    assert task.title == 'Updated Task'
    assert task.description == 'Updated Description'
    assert task.priority == 'high'
    assert task.status == 'in_progress'


@pytest.mark.django_db
def test_task_update_view_invalid_data(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    task = Task.objects.create(
        title='Old Task',
        description='Old Description',
        priority='low',
        due_date='2024-12-31',
        status='open',
        created_by=create_recruiter_user
    )
    url = reverse('accounts:task_update', kwargs={'task_id': task.id})
    updated_task_data = {
        'title': '',  # Invalid data
        'description': 'Updated Description',
        'priority': 'high',
        'due_date': '2024-12-31',
        'status': 'in_progress'
    }
    response = client.post(url, data=updated_task_data)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]
    task.refresh_from_db()
    assert task.title == 'Old Task'  # Ensure the task was not updated


@pytest.mark.django_db
def test_task_delete_view(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    task = Task.objects.create(
        title='Task to Delete',
        description='Task Description',
        priority='medium',
        due_date='2024-12-31',
        status='open',
        created_by=create_recruiter_user
    )
    url = reverse('accounts:task_delete', kwargs={'task_id': task.id})
    response = client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_confirm_delete.html' in [t.name for t in response.templates]

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('accounts:task_list')
    with pytest.raises(Task.DoesNotExist):
        task.refresh_from_db()


@pytest.mark.django_db
def test_task_detail_view(client, create_recruiter_user):
    client.force_login(create_recruiter_user)
    task = Task.objects.create(
        title='Task Detail',
        description='Task Description',
        priority='medium',
        due_date='2024-12-31',
        status='open',
        created_by=create_recruiter_user
    )
    url = reverse('accounts:task_detail', kwargs={'pk': task.id})
    response = client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_detail.html' in [t.name for t in response.templates]
    assert response.context['task'] == task


@pytest.mark.django_db
def test_task_detail_view_not_logged_in(client):
    recruiter = User.objects.create_user(email='recruiter@example.com', password='strongpassword123', role='recruiter')
    RecruiterProfile.objects.create(
        user=recruiter,
        first_name='Recruiter',
        last_name='User',
        phone_number='+1234567890',
        location='Test Location',
        bio='Test bio'
    )
    task = Task.objects.create(
        title='Task Detail',
        description='Task Description',
        priority='medium',
        due_date='2024-12-31',
        status='open',
        created_by=recruiter
    )
    url = reverse('accounts:task_detail', kwargs={'pk': task.id})
    response = client.get(url)
    assert response.status_code == 302  # Redirect to login
    assert response.url.startswith(reverse('accounts:login'))


@pytest.mark.django_db
def test_change_password_view(client, create_test_user):
    client.force_login(create_test_user)
    url = reverse('accounts:change_password')
    response = client.get(url)
    assert response.status_code == 200
    assert 'registration/change_password.html' in [t.name for t in response.templates]

    password_data = {
        'new_password': 'newstrongpassword123',
        'new_password_confirm': 'newstrongpassword123'
    }
    response = client.post(url, data=password_data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:profile_detail')
    create_test_user.refresh_from_db()
    assert create_test_user.check_password('newstrongpassword123')


@pytest.mark.django_db
def test_change_password_view_invalid_data(client, create_test_user):
    client.force_login(create_test_user)
    url = reverse('accounts:change_password')
    password_data = {
        'new_password': 'newstrongpassword123',
        'new_password_confirm': 'differentpassword'  # Invalid confirmation
    }
    response = client.post(url, data=password_data)
    assert response.status_code == 200
    assert 'registration/change_password.html' in [t.name for t in response.templates]
    assert not create_test_user.check_password('newstrongpassword123')  # Password should not be changed
