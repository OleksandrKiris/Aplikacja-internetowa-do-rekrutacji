from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import News

User = get_user_model()


class NewsModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            role='candidate'
        )

    def test_news_creation(self):
        news = News.objects.create(
            title="Test News",
            content="This is a test news content.",
            role="candidate"
        )
        self.assertEqual(news.title, "Test News")
        self.assertEqual(news.content, "This is a test news content.")
        self.assertEqual(news.role, "candidate")
        self.assertEqual(str(news), "Test News")

    def test_news_role_choices(self):
        candidate_news = News.objects.create(
            title="Candidate News",
            content="Content for candidates",
            role="candidate"
        )
        client_news = News.objects.create(
            title="Client News",
            content="Content for clients",
            role="client"
        )
        recruiter_news = News.objects.create(
            title="Recruiter News",
            content="Content for recruiters",
            role="recruiter"
        )
        self.assertEqual(candidate_news.role, "candidate")
        self.assertEqual(client_news.role, "client")
        self.assertEqual(recruiter_news.role, "recruiter")

    def test_news_verbose_names(self):
        news = News.objects.create(
            title="Verbose News",
            content="Content with verbose names",
            role="client"
        )
        model_fields = news._meta.fields
        field_names = {field.name: field.verbose_name for field in model_fields}
        self.assertEqual(field_names["title"], "Tytuł")
        self.assertEqual(field_names["content"], "Zawartość")
        self.assertEqual(field_names["date_posted"], "Data dodania")
        self.assertEqual(field_names["role"], "Rola")


