from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


# Custom user manager
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Adres e-mail musi być podany')
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Nieprawidłowy adres e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        self._set_password(user, password)
        user.save(using=self._db)
        return user

    def _set_password(self, user, password):
        if not password:
            raise ValueError('Hasło musi być podane')
        if len(password) < 8:
            raise ValueError('Hasło musi zawierać co najmniej 8 znaków')
        user.set_password(password)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superużytkownik musi mieć is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superużytkownik musi mieć is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom User model
class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='adres email', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ('candidate', _('Kandydat')),
        ('client', _('Klient')),
        ('recruiter', _('Rekruter')),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_("Rola"))

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser or perm in self.get_all_permissions()

    def has_module_perms(self, app_label):
        return self.is_superuser or app_label in self.get_module_permissions()

    def get_all_permissions(self):
        return set()

    def get_module_permissions(self):
        return set()

    class Meta:
        verbose_name = _('użytkownik')
        verbose_name_plural = _('użytkownicy')
        permissions = [
            ('can_view_dashboard', 'Może przeglądać pulpit nawigacyjny'),
        ]


phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Podaj poprawny numer telefonu"
)
min_length_validator_2 = MinLengthValidator(2)


# Candidate profile model
class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='candidate_profile')
    first_name = models.CharField(max_length=100, verbose_name="Imię",
                                  validators=[min_length_validator_2])
    last_name = models.CharField(max_length=100, verbose_name="Nazwisko",
                                 validators=[min_length_validator_2])
    phone_number = models.CharField(max_length=15, verbose_name="Numer telefonu",
                                    validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Zdjęcie")
    location = models.CharField(max_length=100, verbose_name="Lokalizacja")
    bio = models.TextField(verbose_name="Biografia")
    date_of_birth = models.DateField(verbose_name="Data urodzenia")
    skills = models.TextField(verbose_name="Umiejętności")

    def age(self):
        return timezone.now().year - self.date_of_birth.year if self.date_of_birth else None

    def __str__(self):
        return f"Profil kandydata: {self.first_name} {self.last_name}"


# Client profile model
class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='client_profile')
    phone_number = models.CharField(max_length=15, verbose_name="Numer telefonu",
                                    validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Zdjęcie")
    location = models.CharField(max_length=100, verbose_name="Lokalizacja")
    bio = models.TextField(verbose_name="Biografia")
    company_name = models.CharField(max_length=100, verbose_name="Nazwa firmy")
    industry = models.CharField(max_length=50, verbose_name="Branża")

    def __str__(self):
        return f"Profil pracodawcy {self.company_name}"


# Recruiter profile model
class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='recruiter_profile')
    first_name = models.CharField(max_length=100, verbose_name="Imię",
                                  validators=[min_length_validator_2])
    last_name = models.CharField(max_length=100, verbose_name="Nazwisko",
                                 validators=[min_length_validator_2])
    phone_number = models.CharField(max_length=15, verbose_name="Numer telefonu",
                                    validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Zdjęcie")
    location = models.CharField(max_length=100, verbose_name="Lokalizacja")
    bio = models.TextField(verbose_name="Biografia")

    def __str__(self):
        return f"Profil rekrutera: {self.first_name} {self.last_name}"


# Task model
class Task(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE,
                                   verbose_name='Utworzone przez')
    title = models.CharField(max_length=200, verbose_name='Tytuł')
    description = models.TextField(verbose_name='Opis')
    PRIORITY_CHOICES = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
    ]
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, verbose_name='Priorytet')
    due_date = models.DateField(verbose_name='Termin wykonania')
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
