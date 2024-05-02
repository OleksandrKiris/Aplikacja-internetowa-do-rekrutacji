from django.db import models
from django.conf import settings
from django.shortcuts import render
from django.views import View


class Job(models.Model):
    class JobStatus(models.TextChoices):
        OPEN = 'open', 'Otwarta'
        CLOSED = 'closed', 'Zamknięta'

    title = models.CharField(max_length=200)
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_managed')
    description = models.TextField()
    requirements = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=JobStatus.choices)

    def __str__(self):
        return self.title

    def is_open(self):
        return self.status == self.JobStatus.OPEN

    def close_job(self):
        self.status = self.JobStatus.CLOSED
        self.save()

    def application_count(self):
        return self.applications.count()


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        SUBMITTED = 'submitted', 'Złożone'
        REVIEWED = 'reviewed', 'Przejrzane'
        ACCEPTED = 'accepted', 'Zaakceptowane'
        REJECTED = 'rejected', 'Odrzucone'

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices)

    def __str__(self):
        return f'{self.job.title} - {self.applicant.username}'

    def is_accepted(self):
        return self.status == self.ApplicationStatus.ACCEPTED

    def update_status(self, new_status):
        if new_status in [choice[0] for choice in self.ApplicationStatus.choices]:
            self.status = new_status
            self.save()
            return True
        return False

    def full_details(self):
        return f'Application for {self.job.title} by {self.applicant.username} - Status: {self.status}'


class GuestFeedback(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='guest_feedbacks')
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f'Feedback from {self.email} for {self.job.title}'
