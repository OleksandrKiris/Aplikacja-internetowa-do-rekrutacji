import json
import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import RecruiterProfile, ClientProfile, CandidateProfile, Task
from jobs.models import Job

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        recruiter = User.objects.create_user(email='recruiter@example.com', password='pass123')
        # Create jobs with a linked recruiter
        self.open_job1 = Job.objects.create(title="Software Developer", status=Job.JobStatus.OPEN, recruiter=recruiter)
        self.open_job2 = Job.objects.create(title="Product Manager", status=Job.JobStatus.OPEN, recruiter=recruiter)
        self.closed_job = Job.objects.create(title="Test Engineer", status=Job.JobStatus.CLOSED, recruiter=recruiter)

    def test_home_view(self):
        """
        Test the home view to ensure it only displays open jobs.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/base.html')
        jobs_in_context = response.context['jobs']
        self.assertIn(self.open_job1, jobs_in_context)
        self.assertIn(self.open_job2, jobs_in_context)
        self.assertNotIn(self.closed_job, jobs_in_context)

    def test_about_view(self):
        """
        Test the about view to ensure the about page loads properly.
        """
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/about_us.html')

    def test_contact_view(self):
        """
        Test the contact view to ensure the contact page loads properly.
        """
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/contact.html')


@pytest.fixture
def job(db):
    recruiter = User.objects.create_user(email='jobrecruiter@example.com', password='pass123')
    return Job.objects.create(title="Open Job", status=Job.JobStatus.OPEN, recruiter=recruiter)


@pytest.mark.django_db
def test_home_view_context(client, job):
    """
    Function-based test for the home view context, specifically focusing on the correct retrieval of open jobs.
    """
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert job in response.context['jobs']


class RecruiterListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовых пользователей и профили рекрутеров
        for i in range(10):
            user = User.objects.create_user(email=f'user{i}@example.com', password='password')
            RecruiterProfile.objects.create(user=user, first_name=f'John{i}', last_name=f'Doe{i}')

    def test_recruiter_list_view_pagination(self):
        response = self.client.get(reverse('accounts:recruiters'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/recruiters.html')
        # Проверка количества рекрутеров на странице
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_recruiter_list_ajax_request(self):
        response = self.client.get(reverse('accounts:recruiters'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        # Проверяем, что получен JSON и содержит нужные ключи
        self.assertIn('recruiters', response_json)
        self.assertIn('pagination', response_json)


class ClientListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовых пользователей и профили клиентов
        for i in range(10):
            user = User.objects.create_user(email=f'client{i}@example.com', password='password')
            ClientProfile.objects.create(user=user, company_name=f'Company{i}')

    def test_client_list_view_pagination(self):
        response = self.client.get(reverse('accounts:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/client_list.html')
        # Проверка количества клиентов на странице
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_client_list_ajax_request(self):
        response = self.client.get(reverse('accounts:client_list'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        # Проверяем, что получен JSON и содержит нужные ключи
        self.assertIn('clients', response_json)
        self.assertIn('pagination', response_json)


@pytest.fixture
def user(db):
    User = get_user_model()
    # Убедитесь, что используете правильные поля и параметры при создании пользователя
    return User.objects.create_user(email='user@example.com', password='password', role='candidate')


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_login_view(client, user):
    url = reverse('accounts:login')
    # Используйте ключ 'username', если это ожидает форма
    response = client.post(url, {
        'username': 'user@example.com',
        'password': 'password'
    })

    if response.status_code != 302:
        print("Form errors:", response.context['form'].errors)
        print("Response content:", response.content.decode('utf-8'))

    assert response.status_code == 302, f"Expected redirect after login, got {response.status_code}"


@pytest.mark.django_db
def test_logout_view(client, user):
    client.login(username='user@example.com', password='password')
    url = reverse('accounts:logout')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('home')


@pytest.mark.django_db
def test_dashboard_view_authenticated(client, user):
    client.login(username='user@example.com', password='password')
    url = reverse('accounts:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert 'dashboard/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_profile(client, user):
    client.login(username='user@example.com', password='password')
    url = reverse('accounts:create_profile')
    response = client.get(url)
    assert response.status_code == 200  # Проверяем, что форма доступна после аутентификации


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(email='user@example.com', password='password', role='candidate')


@pytest.fixture
def client_authenticated(client, user):
    client.login(email='user@example.com', password='password')
    return client


@pytest.fixture
def profile(db, user):
    return CandidateProfile.objects.create(user=user, first_name="John", last_name="Doe")


@pytest.mark.django_db
def test_profile_edit_view_access_and_edit(client_authenticated, profile):
    url = reverse('accounts:profile_edit')
    response = client_authenticated.get(url)
    assert response.status_code == 200, "Should be accessible for logged-in users"

    # Убедитесь, что передаете все необходимые поля, которые ожидает ваша форма
    form_data = {
        'first_name': 'New',
        'last_name': 'Name',
        'phone_number': '1234567890',
        'photo': '',  # Указываем пустую строку, если поле необязательно
        'location': 'Some location',  # Предоставляем значение для обязательного поля
        'bio': 'Some bio',  # Предоставляем значение для обязательного поля
        'date_of_birth': '1990-01-01',  # Добавляем дату рождения, если это обязательное поле
        'skills': 'Skill1, Skill2'  # Предоставляем некоторые навыки, если это обязательное поле
    }
    response_post = client_authenticated.post(url, form_data)
    if response_post.status_code != 302:
        print("Form errors:", response_post.context['form'].errors)  # Вывод ошибок формы для диагностики

    assert response_post.status_code == 302, "Should redirect after form submission"
    assert response_post.url == reverse('accounts:dashboard'), "Should redirect to dashboard"


@pytest.fixture
def recruiter_client(db):
    # Создаем пользователя с ролью 'recruiter'
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    client = Client()
    client.login(email='recruiter@example.com', password='password')
    return client


@pytest.mark.django_db
def test_task_list_view(recruiter_client):
    url = reverse('accounts:task_list')
    response = recruiter_client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_list.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_task_create_view(recruiter_client):
    url = reverse('accounts:task_create')
    response = recruiter_client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_task_update_view(recruiter_client):
    # Допустим, task_id уже создана в другом месте или используется fixture для создания задачи
    task_id = 1  # Заглушка для примера
    url = reverse('accounts:task_update', args=[task_id])
    response = recruiter_client.get(url)
    assert response.status_code == 200
    assert 'tasks/task_form.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_task_delete_view(recruiter_client):
    # Аналогично, предполагаем, что task_id известен
    task_id = 1  # Заглушка для примера
    url = reverse('accounts::task_delete', args=[task_id])
    response = recruiter_client.post(url)
    assert response.status_code == 302  # После удаления должно произойти перенаправление
