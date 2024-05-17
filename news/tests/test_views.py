from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import News

User = get_user_model()


class NewsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            role='candidate'
        )
        self.news1 = News.objects.create(
            title='Test News 1',
            content='Content for test news 1',
            role='candidate'
        )
        self.news2 = News.objects.create(
            title='Test News 2',
            content='Content for test news 2',
            role='client'
        )

    def test_dashboard_view_authenticated(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Check if there is a redirect
        self.assertTrue(
            response.url.startswith(reverse('accounts:login')))  # Check if the redirect URL starts with the login URL

    def test_news_list_view_not_authenticated(self):
        response = self.client.get(reverse('news:news_list'))
        self.assertRedirects(response, reverse('news:all_news_view'))

    def test_all_news_view(self):
        response = self.client.get(reverse('news:all_news_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/all_news_list.html')
        self.assertContains(response, '<div class="row justify-content-center" id="news-container">')

    def test_all_news_view_json(self):
        response = self.client.get(reverse('news:all_news_view'), {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn('news', json_response)
        self.assertEqual(len(json_response['news']), 2)

        news_titles = [news['title'] for news in json_response['news']]
        self.assertIn('Test News 1', news_titles)
        self.assertIn('Test News 2', news_titles)

        date_posted_list = [news['date_posted'] for news in json_response['news']]
        self.assertEqual(date_posted_list, sorted(date_posted_list, reverse=True))
