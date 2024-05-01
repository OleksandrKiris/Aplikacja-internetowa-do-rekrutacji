from datetime import date

from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from kirismor import settings
from django.contrib.auth.models import UserManager


class MyUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='adres email', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    # Ograniczone opcje dla pola roli
    ROLE_CHOICES = (
        ('candidate', _('Kandydat')),
        ('client', _('Klient')),
        ('recruiter', _('Recruiter')),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_("Rola"), blank=True, null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('użytkownik')
        verbose_name_plural = _('użytkownicy')


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='candidate_profile')
    first_name = models.CharField(max_length=100, default="", verbose_name="Imię")
    last_name = models.CharField(max_length=100, default="", verbose_name="Nazwisko")
    phone_number = models.CharField(max_length=15, default="", verbose_name=_("Numer telefonu"))
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name=_("Zdjęcie"))
    location = models.CharField(max_length=100, default="", verbose_name=_("Lokalizacja"))
    bio = models.TextField(default="", verbose_name=_("Biografia"))
    date_of_birth = models.DateField(blank=True, default=date.today, verbose_name=_("Data urodzenia"))
    skills = models.TextField(default="", verbose_name=_("Umiejętności"))

    def age(self):
        return timezone.now().year - self.date_of_birth.year if self.date_of_birth else None

    def __str__(self):
        return f"Profil kandydata: {self.first_name} {self.last_name}"


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='client_profile')
    phone_number = models.CharField(max_length=15, default="", verbose_name="Numer telefonu")
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Zdjęcie")
    location = models.CharField(max_length=100, default="", verbose_name="Lokalizacja")
    bio = models.TextField(default="", verbose_name="Biografia")
    company_name = models.CharField(max_length=100, verbose_name="Nazwa firmy")
    industry = models.CharField(max_length=50, default="", verbose_name="Branża")

    def __str__(self):
        return f"Profil pracodawcy {self.company_name}"


class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='recruiter_profile')
    first_name = models.CharField(max_length=100, default="", verbose_name="Imię")
    last_name = models.CharField(max_length=100, default="", verbose_name="Nazwisko")
    phone_number = models.CharField(max_length=15, default="", verbose_name=_("Numer telefonu"))
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name=_("Zdjęcie"))
    location = models.CharField(max_length=100, default="", verbose_name=_("Lokalizacja"))
    bio = models.TextField(default="", verbose_name=_("Biografia"))

    def __str__(self):
        return f"Profil rekrutera: {self.first_name} {self.last_name}"


class Task(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE, verbose_name='Создано')
    title = models.CharField(max_length=200, verbose_name='Tytuł')
    description = models.TextField(verbose_name='Opis')
    PRIORITY_CHOICES = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
    ]
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, verbose_name='Priorytet')
    due_date = models.DateField(default=timezone.now, verbose_name='Termin wykonania')
    STATUS_CHOICES = [
        ('open', 'Otwarte'),
        ('in_progress', 'W trakcie realizacji'),
        ('completed', 'Zakończone'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='Status')

    def change_status(self, new_status):
        self.status = new_status
        self.save()

    def __str__(self):
        return self.title

