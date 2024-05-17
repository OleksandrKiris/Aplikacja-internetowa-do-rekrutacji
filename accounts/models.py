from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import hashlib
import time


class MyUserManager(BaseUserManager):
    """
    Menedżer użytkowników dla niestandardowego modelu użytkownika.

    Zapewnia metody tworzenia użytkowników i superużytkowników z adresem e-mail jako unikalnym identyfikatorem.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Tworzy i zapisuje użytkownika z podanym adresem e-mail i hasłem.

        Args:
            email (str): Adres e-mail użytkownika.
            password (str, opcjonalnie): Hasło użytkownika.
            extra_fields (dict): Dodatkowe pola do ustawienia na użytkowniku.

        Returns:
            User: Utworzony użytkownik.

        Raises:
            ValueError: Jeśli adres e-mail jest nieprawidłowy lub nie jest ustawiony.
        """
        if not email:
            raise ValueError(_('Adres e-mail musi być ustawiony'))
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_('Nieprawidłowy format adresu e-mail'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = extra_fields.get('is_active', False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Tworzy i zapisuje superużytkownika z podanym adresem e-mail i hasłem.

        # Args:
        #  email (str): Adres e-mail superużytkownika.
        # password (str, opcjonalnie): Hasło superużytkownika.
        #  extra_fields (dict): Dodatkowe pola do ustawienia na superużytkowniku.

        # Returns:
        # User: Utworzony superużytkownik.

        # Raises:
        #     ValueError: Jeśli is_staff lub is_superuser nie są ustawione na True.

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields['is_staff']:
            raise ValueError(_('Superużytkownik musi mieć is_staff=True.'))
        if not extra_fields['is_superuser']:
            raise ValueError(_('Superużytkownik musi mieć is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Niestandardowy model użytkownika używający adresu e-mail jako unikalnego identyfikatora zamiast nazwy użytkownika.

    Attributes:
        email (str): Adres e-mail użytkownika.
        is_active (bool): Czy konto użytkownika jest aktywne.
        last_login (datetime): Data ostatniego logowania użytkownika.
        is_staff (bool): Czy użytkownik jest członkiem personelu.
        is_superuser (bool): Czy użytkownik jest superużytkownikiem.
        is_verified (bool): Czy adres e-mail użytkownika został zweryfikowany.
        verification_token (str): Token weryfikacyjny adresu e-mail użytkownika.
        role (str): Rola użytkownika (kandydat, klient, rekruter).
    """
    email = models.EmailField(verbose_name='adres e-mail', max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    ROLE_CHOICES = (
        ('candidate', _('Kandydat')),
        ('client', _('Klient')),
        ('recruiter', _('Rekruter')),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_("Rola"))
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('użytkownik')
        verbose_name_plural = _('użytkownicy')
        permissions = [
            ('can_view_dashboard', _('Może przeglądać pulpit nawigacyjny')),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Zwraca pełne imię i nazwisko użytkownika w zależności od jego roli.

        Returns:
            str: Pełne imię i nazwisko lub nazwa firmy użytkownika.
        """
        if self.role == 'candidate' and hasattr(self, 'candidate_profile'):
            profile = self.candidate_profile
            return f"{profile.first_name} {profile.last_name}"
        elif self.role == 'client' and hasattr(self, 'client_profile'):
            profile = self.client_profile
            return profile.company_name
        elif self.role == 'recruiter' and hasattr(self, 'recruiter_profile'):
            profile = self.recruiter_profile
            return f"{profile.first_name} {profile.last_name}"
        else:
            return self.email

    def generate_verification_token(self):
        """
        Generuje token weryfikacyjny dla adresu e-mail użytkownika.

        Returns:
            str: Wygenerowany token.
        """
        timestamp = int(time.time())
        token_string = f"{self.email}{timestamp}"
        return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

    def change_password(self, new_password):
        """
        Zmienia hasło użytkownika.

        Args:
            new_password (str): Nowe hasło użytkownika.
        """
        self.set_password(new_password)
        self.save()


phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Podaj poprawny numer telefonu")
)

min_length_validator_2 = MinLengthValidator(2)


class CandidateProfile(models.Model):
    """
    Profil kandydata zawierający dodatkowe informacje o kandydacie.

    Attributes:
        user (User): Użytkownik powiązany z tym profilem.
        first_name (str): Imię kandydata.
        last_name (str): Nazwisko kandydata.
        phone_number (str): Numer telefonu kandydata.
        photo (ImageField): Zdjęcie kandydata.
        location (str): Lokalizacja kandydata.
        bio (str): Biografia kandydata.
        date_of_birth (date): Data urodzenia kandydata.
        skills (str): Umiejętności kandydata.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='candidate_profile')
    first_name = models.CharField(max_length=100, verbose_name=_("Imię"), validators=[min_length_validator_2])
    last_name = models.CharField(max_length=100, verbose_name=_("Nazwisko"), validators=[min_length_validator_2])
    phone_number = models.CharField(max_length=15, verbose_name=_("Numer telefonu"), validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name=_("Zdjęcie"))
    location = models.CharField(max_length=100, verbose_name=_("Lokalizacja"))
    bio = models.TextField(verbose_name=_("Biografia"))
    date_of_birth = models.DateField(null=True, verbose_name=_("Data urodzenia"))
    skills = models.TextField(verbose_name=_("Umiejętności"))

    def __str__(self):
        return f"Profil kandydata: {self.first_name} {self.last_name}"


class ClientProfile(models.Model):
    """
    Profil klienta (pracodawcy) zawierający dodatkowe informacje o kliencie.

    Attributes:
        user (User): Użytkownik powiązany z tym profilem.
        phone_number (str): Numer telefonu klienta.
        photo (ImageField): Zdjęcie klienta.
        location (str): Lokalizacja klienta.
        bio (str): Biografia klienta.
        company_name (str): Nazwa firmy klienta.
        industry (str): Branża firmy klienta.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='client_profile')
    phone_number = models.CharField(max_length=15, verbose_name=_("Numer telefonu"), validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name=_("Zdjęcie"))
    location = models.CharField(max_length=100, verbose_name=_("Lokalizacja"))
    bio = models.TextField(verbose_name=_("Biografia"))
    company_name = models.CharField(max_length=100, verbose_name=_("Nazwa firmy"))
    industry = models.CharField(max_length=50, verbose_name=_("Branża"))

    def __str__(self):
        return f"Profil pracodawcy {self.company_name}"


class RecruiterProfile(models.Model):
    """
    Profil rekrutera zawierający dodatkowe informacje o rekruterze.

    Attributes:
        user (User): Użytkownik powiązany z tym profilem.
        first_name (str): Imię rekrutera.
        last_name (str): Nazwisko rekrutera.
        phone_number (str): Numer telefonu rekrutera.
        photo (ImageField): Zdjęcie rekrutera.
        location (str): Lokalizacja rekrutera.
        bio (str): Biografia rekrutera.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,
                                related_name='recruiter_profile')
    first_name = models.CharField(max_length=100, verbose_name=_("Imię"), validators=[min_length_validator_2])
    last_name = models.CharField(max_length=100, verbose_name=_("Nazwisko"), validators=[min_length_validator_2])
    phone_number = models.CharField(max_length=15, verbose_name=_("Numer telefonu"), validators=[phone_validator])
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name=_("Zdjęcie"))
    location = models.CharField(max_length=100, verbose_name=_("Lokalizacja"))
    bio = models.TextField(verbose_name=_("Biografia"))

    def __str__(self):
        return f"Profil rekrutera: {self.first_name} {self.last_name}"


class Task(models.Model):
    """
    Zadanie tworzone przez rekrutera.

    Attributes:
        created_by (User): Użytkownik, który utworzył zadanie.
        title (str): Tytuł zadania.
        description (str): Opis zadania.
        priority (str): Priorytet zadania (niski, średni, wysoki).
        due_date (date): Termin wykonania zadania.
        status (str): Status zadania (otwarte, w trakcie realizacji, zakończone).
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE,
                                   verbose_name=_('Utworzone przez'))
    title = models.CharField(max_length=200, verbose_name=_('Tytuł'))
    description = models.TextField(verbose_name=_('Opis'))
    PRIORITY_CHOICES = [
        ('low', _('Niski')),
        ('medium', _('Średni')),
        ('high', _('Wysoki')),
    ]
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, verbose_name=_('Priorytet'))
    due_date = models.DateField(verbose_name=_('Termin wykonania'))
    STATUS_CHOICES = [
        ('open', _('Otwarte')),
        ('in_progress', _('W trakcie realizacji')),
        ('completed', _('Zakończone')),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open', verbose_name=_('Status'))

    def save(self, *args, **kwargs):
        """
        Zapisuje zadanie do bazy danych.

        Raises:
            ValidationError: Jeśli użytkownik nie jest rekruterem lub priorytet jest nieprawidłowy.
        """
        if not hasattr(self.created_by, 'recruiter_profile'):
            raise ValidationError(_("Tylko rekruterzy mogą tworzyć zadania."))
        if self.priority not in ['low', 'medium', 'high']:
            raise ValidationError(_("Invalid priority value"))
        super().save(*args, **kwargs)

    def change_status(self, new_status):
        """
        Zmienia status zadania i zapisuje zmiany w bazie danych.

        Args:
            new_status (str): Nowy status zadania.
        """
        self.status = new_status
        self.save()

    def __str__(self):
        return self.title
