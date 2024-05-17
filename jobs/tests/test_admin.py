from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib import admin
from jobs.models import Job, Application, GuestFeedback, TempGuestFeedback, Like, Favorite
from jobs.admin import JobAdmin, ApplicationAdmin, GuestFeedbackAdmin, TempGuestFeedbackAdmin, LikeAdmin, FavoriteAdmin

User = get_user_model()


class AdminPanelTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.recruiter_user = User.objects.create_user(
            email='recruiter@example.com',
            password='testpass123'
        )
        self.job = Job.objects.create(
            title='Test Job',
            recruiter=self.recruiter_user,
            description='Test description',
            requirements='Test requirements',
            salary=1000,
            status='open'
        )
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.recruiter_user,
            cover_letter='Test cover letter',
            status='submitted'
        )
        self.guest_feedback = GuestFeedback.objects.create(
            job=self.job,
            email='guest@example.com',
            message='Test message',
            phone_number='1234567890',
            is_verified=True
        )
        self.temp_guest_feedback = TempGuestFeedback.objects.create(
            job=self.job,
            email='tempguest@example.com',
            message='Temp test message',
            phone_number='0987654321'
        )
        self.like = Like.objects.create(
            user=self.recruiter_user,
            job=self.job
        )
        self.favorite = Favorite.objects.create(
            user=self.recruiter_user,
            job=self.job
        )

    def test_job_admin_list_display(self):
        model_admin = JobAdmin(model=Job, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('title', 'recruiter', 'created_at', 'status'))

    def test_application_admin_list_display(self):
        model_admin = ApplicationAdmin(model=Application, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('job', 'applicant', 'created_at', 'status'))

    def test_guest_feedback_admin_list_display(self):
        model_admin = GuestFeedbackAdmin(model=GuestFeedback, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('job', 'email', 'created_at', 'is_verified'))

    def test_temp_guest_feedback_admin_list_display(self):
        model_admin = TempGuestFeedbackAdmin(model=TempGuestFeedback, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('job', 'email', 'created_at'))

    def test_like_admin_list_display(self):
        model_admin = LikeAdmin(model=Like, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('user', 'job', 'created_at'))

    def test_favorite_admin_list_display(self):
        model_admin = FavoriteAdmin(model=Favorite, admin_site=admin.site)
        self.assertEqual(model_admin.list_display, ('user', 'job', 'created_at'))

    def test_admin_can_access_job_changelist(self):
        url = reverse('admin:jobs_job_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_application_changelist(self):
        url = reverse('admin:jobs_application_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_guest_feedback_changelist(self):
        url = reverse('admin:jobs_guestfeedback_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_temp_guest_feedback_changelist(self):
        url = reverse('admin:jobs_tempguestfeedback_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_like_changelist(self):
        url = reverse('admin:jobs_like_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_favorite_changelist(self):
        url = reverse('admin:jobs_favorite_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_job_search(self):
        url = reverse('admin:jobs_job_changelist')
        response = self.client.get(url, {'q': 'Test Job'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_application_search(self):
        url = reverse('admin:jobs_application_changelist')
        response = self.client.get(url, {'q': 'Test Job'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_guest_feedback_search(self):
        url = reverse('admin:jobs_guestfeedback_changelist')
        response = self.client.get(url, {'q': 'guest@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'guest@example.com')

    def test_temp_guest_feedback_search(self):
        url = reverse('admin:jobs_tempguestfeedback_changelist')
        response = self.client.get(url, {'q': 'tempguest@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tempguest@example.com')

    def test_like_search(self):
        url = reverse('admin:jobs_like_changelist')
        response = self.client.get(url, {'q': 'recruiter@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recruiter@example.com')

    def test_favorite_search(self):
        url = reverse('admin:jobs_favorite_changelist')
        response = self.client.get(url, {'q': 'recruiter@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recruiter@example.com')
