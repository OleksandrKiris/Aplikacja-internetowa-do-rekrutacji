from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class JobRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'pending', _('Oczekujące')
        PROCESSING = 'processing', _('W trakcie realizacji')
        COMPLETED = 'completed', _('Zakończone')

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_requests',
        verbose_name=_('Pracodawca')
    )
    title = models.CharField(max_length=200, verbose_name=_('Tytuł'))
    description = models.TextField(max_length=500, verbose_name=_('Opis'))
    requirements = models.TextField(max_length=300, verbose_name=_('Wymagania'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data utworzenia'))
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        verbose_name=_('Status')
    )
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='recruited_jobs',
        blank=True, null=True,
        verbose_name=_('Rekruter')
    )

    class Meta:
        verbose_name = _('Zapotrzebowanie na pracę')
        verbose_name_plural = _('Zapotrzebowania na pracę')

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'


class JobRequestStatusUpdate(models.Model):
    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name='status_updates',
        verbose_name=_('Aktualizacja statusu zapotrzebowania na pracę')
    )
    new_status = models.CharField(
        max_length=20,
        choices=JobRequest.RequestStatus.choices,
        verbose_name=_('Nowy status')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Zaktualizowane przez')
    )
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data aktualizacji'))
    message = models.TextField(blank=True, null=True, verbose_name=_('Wiadomość'))

    class Meta:
        verbose_name = _('Aktualizacja statusu zapotrzebowania')
        verbose_name_plural = _('Aktualizacje statusów zapotrzebowania')


class FavoriteRecruiter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_recruiters',
        verbose_name=_('Użytkownik')
    )
    recruiter = models.ForeignKey(
        'accounts.RecruiterProfile',  # используйте 'app_name.ModelName'
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Ulubiony rekruter')
    )

    class Meta:
        unique_together = ('user', 'recruiter')
        verbose_name = _('Ulubiony rekruter')
        verbose_name_plural = _('Ulubieni rekruterzy')

    def __str__(self):
        return f"{self.user.email} favorites {self.recruiter.user.email}"