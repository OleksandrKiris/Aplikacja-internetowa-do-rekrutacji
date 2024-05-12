from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class MyUserManager(BaseUserManager):
    """
    Menedżer użytkowników, który dostarcza metody do tworzenia użytkowników i superużytkowników.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email format')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        role = extra_fields.get('role')
        if role:  # Проверяем наличие роли только если она есть
            valid_roles = [choice[0] for choice in self.model.ROLE_CHOICES]
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}. Valid roles are {valid_roles}.")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Tworzy superużytkownika z podanym adresem email i hasłem.

        Parametry:
            email (str): Adres email superużytkownika.
            password (str, optional): Hasło superużytkownika.
            **extra_fields: Dodatkowe pola przekazywane do modelu superużytkownika.

        Zwraca:
            User: Obiekt utworzonego superużytkownika.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superużytkownik musi mieć is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superużytkownik musi mieć is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Niestandardowy model użytkownika rozszerzający AbstractBaseUser.
    """
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
        Zwraca pełne imię i nazwisko użytkownika na podstawie jego roli.
        Zwraca adres email, jeśli profil nie istnieje.
        """
        if self.role == 'candidate' and hasattr(self, 'candidate_profile'):
            profile = self.candidate_profile
        elif self.role == 'client' and hasattr(self, 'client_profile'):
            profile = self.client_profile
        elif self.role == 'recruiter' and hasattr(self, 'recruiter_profile'):
            profile = self.recruiter_profile
        else:
            return self.email

        return f"{profile.first_name} {profile.last_name}"


# Walidator numeru telefonu
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Podaj poprawny numer telefonu"
)

# Walidator minimalnej długości
min_length_validator_2 = MinLengthValidator(2)


class CandidateProfile(models.Model):
    """
    Model profilu kandydata, który jest powiązany z modelem użytkownika.
    """
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
    date_of_birth = models.DateField(null=True, verbose_name="Data urodzenia")
    skills = models.TextField(verbose_name="Umiejętności")

    def __str__(self):
        """
        Zwraca reprezentację tekstową profilu kandydata.

        Zwraca:
            str.: Opis profilu kandydata.
        """
        return f"Profil kandydata: {self.first_name} {self.last_name}"


class ClientProfile(models.Model):
    """
    Model profilu klienta, który jest powiązany z modelem użytkownika.
    """
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
        """
        Zwraca reprezentację tekstową profilu klienta.

        Zwraca:
            str.: Opis profilu klienta.
        """
        return f"Profil pracodawcy {self.company_name}"


class RecruiterProfile(models.Model):
    """
    Model profilu rekrutera, który jest powiązany z modelem użytkownika.
    """
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
        """
        Zwraca reprezentację tekstową profilu rekrutera.

        Zwraca:
            str: Opis profilu rekrutera.
        """
        return f"Profil rekrutera: {self.first_name} {self.last_name}"


class Task(models.Model):
    """
    Model zadania przypisanego użytkownikom.
    """
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open', verbose_name='Status')

    def save(self, *args, **kwargs):
        if not hasattr(self.created_by, 'recruiter_profile'):
            raise ValidationError(_("Only recruiters can create tasks."))
        super().save(*args, **kwargs)

    def change_status(self, new_status):
        """
        Zmienia status zadania.

        Parametry:
            new_status (str): Nowy status zadania.
        """
        self.status = new_status
        self.save()

    def __str__(self):
        """
        Zwraca reprezentację tekstową zadania.

        Zwraca:
            str: Tytuł zadania.
        """
        return self.title
