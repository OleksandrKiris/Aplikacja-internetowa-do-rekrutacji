from django.db import models
from django.utils.translation import gettext_lazy as _


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Tytuł"))
    content = models.TextField(verbose_name=_("Zawartość"))
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name=_("Data dodania"))
    role = models.CharField(max_length=50, choices=[
        ('candidate', _('Kandydat')),
        ('client', _('Klient')),
        ('recruiter', _('Rekruter'))
    ], verbose_name=_("Rola"))

    def __str__(self):
        return self.title
