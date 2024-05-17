from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import hashlib
import time
from django.contrib.auth import get_user_model

"""
Importy:
- from django.db import models: Importuje moduł modeli Django, który pozwala na tworzenie struktur baz danych w Django.
- from django.conf import settings: Importuje ustawienia projektu Django, które mogą być używane w modelach.
- from django.utils.translation import gettext_lazy as _: Importuje funkcję tłumaczenia, umożliwiającą międzynarodowe tłumaczenie tekstów.
- from django.core.exceptions import ValidationError: Importuje wyjątek walidacji, używany do walidowania danych w modelach.
- import hashlib: Importuje moduł hashlib do generowania skrótów (hash) z danych, takich jak tokeny weryfikacyjne.
- import time: Importuje moduł time, używany do generowania znaczników czasu.
- from django.contrib.auth import get_user_model: Importuje funkcję, która zwraca bieżący model użytkownika Django.
"""

User = get_user_model()  # Pobiera bieżący model użytkownika


class Job(models.Model):
    """
    Model reprezentujący ofertę pracy.

    Atrybuty:
        title (str): Tytuł oferty pracy.
        recruiter (ForeignKey): Rekruter odpowiedzialny za ofertę pracy.
        description (str): Opis oferty pracy.
        requirements (str): Wymagania stanowiska.
        salary (Decimal): Wynagrodzenie oferowane za pracę.
        created_at (DateTime): Data utworzenia oferty pracy.
        status (str): Status oferty pracy (otwarta/zamknięta).
    """

    class JobStatus(models.TextChoices):
        OPEN = 'open', _('Otwarta')
        CLOSED = 'closed', _('Zamknięta')

    title = models.CharField(max_length=200)
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_managed')
    description = models.TextField(max_length=2000)
    requirements = models.TextField(max_length=2000)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='open', choices=JobStatus.choices)

    def __str__(self):
        return self.title

    def is_open(self):
        """
        Sprawdza, czy oferta pracy jest otwarta.

        Returns:
            bool: True, jeśli oferta jest otwarta, False w przeciwnym razie.
        """
        return self.status == self.JobStatus.OPEN

    def close_job(self):
        """
        Zamienia status oferty pracy na zamkniętą.
        """
        self.status = self.JobStatus.CLOSED
        self.save()

    def application_count(self):
        """
        Zwraca liczbę aplikacji na ofertę pracy.

        Returns:
            int: Liczba aplikacji.
        """
        return self.applications.count()

    def clean(self):
        """
        Waliduje status oferty pracy.
        """
        if self.status not in [choice[0] for choice in self.JobStatus.choices]:
            raise ValidationError(f"Invalid status: {self.status}")

    def save(self, *args, **kwargs):
        """
        Zapisuje ofertę pracy po walidacji.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class Application(models.Model):
    """
    Model reprezentujący aplikację na ofertę pracy.

    Atrybuty:
        job (ForeignKey): Powiązanie z ofertą pracy.
        applicant (ForeignKey): Powiązanie z aplikującym użytkownikiem.
        cover_letter (str): List motywacyjny aplikującego.
        created_at (DateTime): Data utworzenia aplikacji.
        status (str): Status aplikacji (złożona/przejrzana/zaakceptowana/odrzucona).
    """

    class ApplicationStatus(models.TextChoices):
        SUBMITTED = 'submitted', _('Złożone')
        REVIEWED = 'reviewed', _('Przejrzane')
        ACCEPTED = 'accepted', _('Zaakceptowane')
        REJECTED = 'rejected', _('Odrzucone')

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications',
                                  blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='submitted', choices=ApplicationStatus.choices)

    def is_accepted(self):
        """
        Sprawdza, czy aplikacja została zaakceptowana.

        Returns:
            bool: True, jeśli aplikacja jest zaakceptowana, False w przeciwnym razie.
        """
        return self.status == self.ApplicationStatus.ACCEPTED

    def update_status(self, new_status):
        """
        Aktualizuje status aplikacji, jeśli nowy status jest poprawny.

        Args:
            new_status (str): Nowy status aplikacji.

        Returns:
            bool: True, jeśli status został zaktualizowany, False w przeciwnym razie.
        """
        if new_status in [choice[0] for choice in self.ApplicationStatus.choices]:
            self.status = new_status
            self.save()
            return True
        return False

    def get_applicant_full_name(self):
        """
        Zwraca pełne imię i nazwisko aplikującego, jeśli dostępne, lub email, jeśli profil nie jest kompletny.

        Returns:
            str: Pełne imię i nazwisko lub email aplikującego.
        """
        if hasattr(self.applicant, 'candidate_profile'):
            return f'{self.applicant.candidate_profile.first_name} {self.applicant.candidate_profile.last_name}'
        else:
            return self.applicant.email

    def __str__(self):
        return f'{self.job.title} - {self.applicant.email}'


class GuestFeedback(models.Model):
    """
    Model reprezentujący opinię gościa.

    Atrybuty:
        job (ForeignKey): Powiązanie z ofertą pracy.
        email (EmailField): Email gościa.
        message (TextField): Wiadomość gościa.
        created_at (DateTime): Data utworzenia opinii.
        phone_number (str): Numer telefonu gościa.
        is_verified (bool): Czy opinia została zweryfikowana.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='guest_feedbacks')
    email = models.EmailField()
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'Feedback from {self.email} for {self.job.title}'


class TempGuestFeedback(models.Model):
    """
    Model reprezentujący tymczasową opinię gościa.

    Atrybuty:
        job (ForeignKey): Powiązanie z ofertą pracy.
        email (EmailField): Email gościa.
        message (TextField): Wiadomość gościa.
        created_at (DateTime): Data utworzenia opinii.
        phone_number (str): Numer telefonu gościa.
        verification_token (str): Token weryfikacyjny.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='temp_guest_feedbacks')
    email = models.EmailField(unique=True)
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True)
    verification_token = models.CharField(max_length=64)

    def generate_verification_token(self):
        """
        Generuje token weryfikacyjny oparty na emailu i znaczniku czasu.

        Returns:
            str: Wygenerowany token weryfikacyjny.
        """
        timestamp = int(time.time())
        token_string = f"{self.email}{timestamp}"
        return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

    def __str__(self):
        return f'Temporary Feedback from {self.email} for {self.job.title}'


class Like(models.Model):
    """
    Model reprezentujący polubienie oferty pracy przez użytkownika.

    Atrybuty:
        user (ForeignKey): Użytkownik, który polubił ofertę pracy.
        job (ForeignKey): Polubiona oferta pracy.
        created_at (DateTime): Data utworzenia polubienia.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.email} likes {self.job.title}"


class Favorite(models.Model):
    """
    Model reprezentujący dodanie oferty pracy do ulubionych przez użytkownika.

    Atrybuty:
        user (ForeignKey): Użytkownik, który dodał ofertę do ulubionych.
        job (ForeignKey): Ulubiona oferta pracy.
        created_at (DateTime): Data dodania do ulubionych.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.email} favorited {self.job.title}"
