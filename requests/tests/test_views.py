import pytest
from django.urls import reverse
from accounts.models import User  # Импорт кастомной модели пользователя
from requests.models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter
from accounts.models import RecruiterProfile


@pytest.fixture
def user_client(db):
    user = User.objects.create_user(email='client@example.com', password='password')
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def user_recruiter(db):
    user = User.objects.create_user(email='recruiter@example.com', password='password')
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def recruiter_profile(db, user_recruiter):
    return RecruiterProfile.objects.create(user=user_recruiter, first_name="Test", last_name="Recruiter")


@pytest.fixture
def job_request(db, user_client, user_recruiter):
    return JobRequest.objects.create(
        employer=user_client,
        title="Test Job",
        description="Test Description",
        requirements="Test Requirements",
        status="pending",
        recruiter=user_recruiter
    )


@pytest.mark.django_db
def test_create_job_request_with_missing_fields(client, user_client):
    client.force_login(user_client)
    response = client.post(reverse('requests:client_job_request_create'), {
        'description': 'Job Description',
        'requirements': 'Job Requirements',
        'status': 'pending'
    })
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.django_db
def test_create_job_request_status_update_with_valid_data(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.post(reverse('requests:recruiter_job_request_update', args=[job_request.pk]), {
        'new_status': 'completed',
        'message': 'Job completed successfully'
    })
    assert response.status_code == 302
    assert JobRequestStatusUpdate.objects.filter(job_request=job_request, new_status='completed').exists()


@pytest.mark.django_db
def test_create_job_request_status_update_with_missing_fields(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.post(reverse('requests:recruiter_job_request_update', args=[job_request.pk]), {
        'message': 'Job update without status'
    })
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.django_db
def test_create_favorite_recruiter_with_valid_data(client, user_client, recruiter_profile):
    client.force_login(user_client)
    response = client.post(reverse('requests:add_to_favorites', args=[recruiter_profile.pk]))
    assert response.status_code == 302
    assert FavoriteRecruiter.objects.filter(user=user_client, recruiter=recruiter_profile).exists()


@pytest.mark.django_db
def test_create_favorite_recruiter_with_missing_fields(client, user_client):
    client.force_login(user_client)
    response = client.post(reverse('requests:add_to_favorites', args=[999]))  # Несуществующий рекрутер
    assert response.status_code == 404


@pytest.mark.django_db
def test_display_client_job_request_list(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:client_job_request_list'))
    assert response.status_code == 200
    assert 'job_requests' in response.context


@pytest.mark.django_db
def test_client_create_job_request_view(client, user_client, recruiter_profile):
    client.force_login(user_client)
    response = client.get(reverse('requests:client_job_request_create'))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_client_delete_job_request_view(client, user_client, job_request):
    client.force_login(user_client)
    response = client.post(reverse('requests:client_job_request_delete', args=[job_request.pk]))
    assert response.status_code == 302
    assert not JobRequest.objects.filter(pk=job_request.pk).exists()


@pytest.mark.django_db
def test_display_recruiter_job_request_list(client, user_recruiter):
    client.force_login(user_recruiter)
    response = client.get(reverse('requests:recruiter_job_request_list'))
    assert response.status_code == 200
    assert 'job_requests' in response.context


@pytest.mark.django_db
def test_client_add_favorite_recruiter(client, user_client, recruiter_profile):
    client.force_login(user_client)
    response = client.post(reverse('requests:add_to_favorites', args=[recruiter_profile.pk]))
    assert response.status_code == 302
    assert FavoriteRecruiter.objects.filter(user=user_client, recruiter=recruiter_profile).exists()


@pytest.mark.django_db
def test_display_recruiter_list(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'))
    assert response.status_code == 200
    assert 'page_obj' in response.context


@pytest.mark.django_db
def test_display_recruiter_detail(client, user_client, recruiter_profile):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_detail_view', args=[recruiter_profile.pk]))
    assert response.status_code == 200
    assert 'recruiter' in response.context


@pytest.mark.django_db
def test_display_create_job_request_form(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:client_job_request_create'))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_display_update_job_request_status_form(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.get(reverse('requests:recruiter_job_request_update', args=[job_request.pk]))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_validate_create_job_request_form_with_valid_data(client, user_client, recruiter_profile):
    client.force_login(user_client)
    response = client.post(reverse('requests:client_job_request_create'), {
        'title': 'New Job',
        'description': 'Job Description',
        'requirements': 'Job Requirements',
        'status': 'pending',
        'recruiter': recruiter_profile.user.id
    })
    assert response.status_code == 302
    assert JobRequest.objects.filter(title='New Job').exists()


@pytest.mark.django_db
def test_validate_create_job_request_form_with_invalid_data(client, user_client):
    client.force_login(user_client)
    response = client.post(reverse('requests:client_job_request_create'), {
        'title': '',
        'description': 'Job Description',
        'requirements': 'Job Requirements',
        'status': 'pending',
        'recruiter': 1
    })
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.django_db
def test_validate_update_job_request_status_form_with_valid_data(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.post(reverse('requests:recruiter_job_request_update', args=[job_request.pk]), {
        'new_status': 'completed',
        'message': 'Job Completed'
    })
    assert response.status_code == 302
    assert JobRequestStatusUpdate.objects.filter(job_request=job_request, new_status='completed').exists()


@pytest.mark.django_db
def test_validate_update_job_request_status_form_with_invalid_data(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.post(reverse('requests:recruiter_job_request_update', args=[job_request.pk]), {
        'new_status': '',
        'message': 'Job Completed'
    })
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors


@pytest.mark.django_db
def test_display_client_job_request_detail(client, user_client, job_request):
    client.force_login(user_client)
    response = client.get(reverse('requests:client_job_request_detail', args=[job_request.pk]))
    assert response.status_code == 200
    assert 'job_request' in response.context


@pytest.mark.django_db
def test_display_recruiter_job_request_detail(client, user_recruiter, job_request):
    client.force_login(user_recruiter)
    response = client.get(reverse('requests:recruiter_job_request_detail', args=[job_request.pk]))
    assert response.status_code == 200
    assert 'job_request' in response.context


@pytest.mark.django_db
def test_filter_recruiters(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'), {'q': 'Test'})
    assert response.status_code == 200
    assert 'page_obj' in response.context


@pytest.mark.django_db
def test_recruiter_list_pagination(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'), {'page': 2})
    assert response.status_code == 200
    assert 'page_obj' in response.context


@pytest.mark.django_db
def test_recruiter_list_pagination_buttons(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'))
    assert response.status_code == 200
    assert 'page_obj' in response.context
    assert 'pagination' in response.content.decode()


@pytest.mark.django_db
def test_ajax_recruiter_list(client, user_client):
    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json().get('recruiters') is not None

@pytest.mark.django_db
def test_recruiter_list_pagination_buttons(client, user_client):
    # Создаем несколько профилей рекрутеров для теста пагинации
    for i in range(20):
        RecruiterProfile.objects.create(
            user=User.objects.create_user(email=f'recruiter{i}@example.com', password='password'),
            first_name=f'Test{i}',
            last_name=f'Recruiter{i}'
        )

    client.force_login(user_client)
    response = client.get(reverse('requests:recruiter_list'))
    assert response.status_code == 200
    assert 'page_obj' in response.context
    pagination_content = response.content.decode()
    assert 'Poprzednia' in pagination_content or 'Następna' in pagination_content, "Pagination buttons not found in response."
