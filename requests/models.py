from django.db import models
from django.conf import settings

from accounts.models import RecruiterProfile


class JobRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Oczekujące'
        PROCESSING = 'processing', 'W trakcie realizacji'
        COMPLETED = 'completed', 'Zakończone'

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_requests'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=RequestStatus.choices)
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruited_jobs',
        blank=True, null=True
    )

    def __str__(self):
        return f'{self.title} - {self.status}'


class JobRequestStatusUpdate(models.Model):
    job_request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='status_updates')
    new_status = models.CharField(max_length=20, choices=JobRequest.RequestStatus.choices)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)


class FavoriteRecruiter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_recruiters')
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recruiter')  # Ensure each user can only favorite a recruiter once

    def __str__(self):
        return f"{self.user.email} favorites {self.recruiter}"
