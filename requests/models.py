from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

"""
Importy:
- from django.db import models: Importuje moduł modeli Django, który pozwala na tworzenie struktur baz danych w Django.
- from django.conf import settings: Importuje ustawienia projektu Django, które mogą być używane w modelach.
- from django.utils.translation import gettext_lazy as _: Importuje funkcję tłumaczenia, umożliwiającą międzynarodowe tłumaczenie tekstów.
"""

class JobRequest(models.Model):
    """
    Model reprezentujący zapotrzebowanie na pracę.

    Atrybuty:
        employer (ForeignKey): Pracodawca odpowiedzialny za zapotrzebowanie na pracę.
        title (str): Tytuł zapotrzebowania.
        description (str): Opis zapotrzebowania.
        requirements (str): Wymagania stanowiska.
        created_at (DateTime): Data utworzenia zapotrzebowania.
        status (str): Status zapotrzebowania (oczekujące/w trakcie realizacji/zakończone).
        recruiter (ForeignKey): Rekruter odpowiedzialny za zapotrzebowanie.
    """
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
    """
    Atrybut employer:
    - settings.AUTH_USER_MODEL: Używa modelu użytkownika zdefiniowanego w ustawieniach Django.
    - on_delete=models.CASCADE: Usuwa powiązane zapotrzebowanie, gdy pracodawca zostanie usunięty.
    - related_name='job_requests': Nazwa odwrotnej relacji od pracodawcy do zapotrzebowań.
    - verbose_name=_('Pracodawca'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    title = models.CharField(max_length=200, verbose_name=_('Tytuł'))
    """
    Atrybut title:
    - models.CharField: Pole znakowe o maksymalnej długości 200 znaków.
    - verbose_name=_('Tytuł'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    description = models.TextField(max_length=500, verbose_name=_('Opis'))
    """
    Atrybut description:
    - models.TextField: Pole tekstowe o maksymalnej długości 500 znaków.
    - verbose_name=_('Opis'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    requirements = models.TextField(max_length=300, verbose_name=_('Wymagania'))
    """
    Atrybut requirements:
    - models.TextField: Pole tekstowe o maksymalnej długości 300 znaków.
    - verbose_name=_('Wymagania'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data utworzenia'))
    """
    Atrybut created_at:
    - models.DateTimeField: Pole daty i czasu.
    - auto_now_add=True: Automatycznie ustawia bieżącą datę i czas podczas tworzenia zapotrzebowania.
    - verbose_name=_('Data utworzenia'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        verbose_name=_('Status')
    )
    """
    Atrybut status:
    - models.CharField: Pole znakowe o maksymalnej długości 20 znaków.
    - choices=RequestStatus.choices: Używa klasy TextChoices do zdefiniowania dostępnych opcji statusu.
    - default=RequestStatus.PENDING: Ustawia domyślną wartość na 'pending'.
    - verbose_name=_('Status'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruited_jobs',
        verbose_name=_('Rekruter')
    )
    """
    Atrybut recruiter:
    - settings.AUTH_USER_MODEL: Używa modelu użytkownika zdefiniowanego w ustawieniach Django.
    - on_delete=models.CASCADE: Usuwa powiązane zapotrzebowanie, gdy rekruter zostanie usunięty.
    - related_name='recruited_jobs': Nazwa odwrotnej relacji od rekrutera do zapotrzebowań.
    - verbose_name=_('Rekruter'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    class Meta:
        verbose_name = _('Zapotrzebowanie na pracę')
        verbose_name_plural = _('Zapotrzebowania na pracę')
        """
        Meta:
        - verbose_name: Tłumaczenie nazwy pojedynczej.
        - verbose_name_plural: Tłumaczenie nazwy mnogiej.
        """

    def __str__(self):
        """
        Zwraca reprezentację tekstową modelu.

        Returns:
            str: Tytuł zapotrzebowania i jego status.
        """
        return f'{self.title} - {self.get_status_display()}'


class JobRequestStatusUpdate(models.Model):
    """
    Model reprezentujący aktualizację statusu zapotrzebowania na pracę.

    Atrybuty:
        job_request (ForeignKey): Powiązanie z zapotrzebowaniem na pracę.
        new_status (str): Nowy status zapotrzebowania.
        updated_by (ForeignKey): Użytkownik, który dokonał aktualizacji.
        updated_at (DateTime): Data aktualizacji statusu.
        message (str): Wiadomość związana z aktualizacją statusu.
    """
    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name='status_updates',
        verbose_name=_('Aktualizacja statusu zapotrzebowania na pracę')
    )
    """
    Atrybut job_request:
    - models.ForeignKey: Powiązanie z modelem JobRequest.
    - on_delete=models.CASCADE: Usuwa powiązane aktualizacje, gdy zapotrzebowanie zostanie usunięte.
    - related_name='status_updates': Nazwa odwrotnej relacji od zapotrzebowania do aktualizacji statusów.
    - verbose_name=_('Aktualizacja statusu zapotrzebowania na pracę'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    new_status = models.CharField(
        max_length=20,
        choices=JobRequest.RequestStatus.choices,
        verbose_name=_('Nowy status')
    )
    """
    Atrybut new_status:
    - models.CharField: Pole znakowe o maksymalnej długości 20 znaków.
    - choices=JobRequest.RequestStatus.choices: Używa klasy TextChoices do zdefiniowania dostępnych opcji statusu.
    - verbose_name=_('Nowy status'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Zaktualizowane przez')
    )
    """
    Atrybut updated_by:
    - models.ForeignKey: Powiązanie z modelem użytkownika.
    - on_delete=models.CASCADE: Usuwa powiązane aktualizacje, gdy użytkownik zostanie usunięty.
    - verbose_name=_('Zaktualizowane przez'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    updated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Data aktualizacji'))
    """
    Atrybut updated_at:
    - models.DateTimeField: Pole daty i czasu.
    - auto_now_add=True: Automatycznie ustawia bieżącą datę i czas podczas aktualizacji statusu.
    - verbose_name=_('Data aktualizacji'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    message = models.TextField(blank=True, null=True, verbose_name=_('Wiadomość'))
    """
    Atrybut message:
    - models.TextField: Pole tekstowe na wiadomość.
    - blank=True: Pozwala na pozostawienie pola pustym.
    - null=True: Pozwala na przechowywanie wartości NULL w bazie danych.
    - verbose_name=_('Wiadomość'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    class Meta:
        verbose_name = _('Aktualizacja statusu zapotrzebowania')
        verbose_name_plural = _('Aktualizacje statusów zapotrzebowania')
        """
        Meta:
        - verbose_name: Tłumaczenie nazwy pojedynczej.
        - verbose_name_plural: Tłumaczenie nazwy mnogiej.
        """

    def __str__(self):
        """
        Zwraca reprezentację tekstową modelu.

        Returns:
            str: Tytuł zapotrzebowania i jego nowy status.
        """
        return f'{self.job_request.title} - {self.get_new_status_display()}'


class FavoriteRecruiter(models.Model):
    """
    Model reprezentujący ulubionego rekrutera użytkownika.

    Atrybuty:
        user (ForeignKey): Użytkownik, który dodał rekrutera do ulubionych.
        recruiter (ForeignKey): Rekruter dodany do ulubionych.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_recruiters',
        verbose_name=_('Użytkownik')
    )
    """
    Atrybut user:
    - models.ForeignKey: Powiązanie z modelem użytkownika.
    - on_delete=models.CASCADE: Usuwa powiązane ulubione rekruterzy, gdy użytkownik zostanie usunięty.
    - related_name='favorite_recruiters': Nazwa odwrotnej relacji od użytkownika do ulubionych rekruterów.
    - verbose_name=_('Użytkownik'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    recruiter = models.ForeignKey(
        'accounts.RecruiterProfile',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Ulubiony rekruter')
    )
    """
    Atrybut recruiter:
    - models.ForeignKey: Powiązanie z modelem RecruiterProfile.
    - on_delete=models.CASCADE: Usuwa powiązane ulubione rekruterzy, gdy rekruter zostanie usunięty.
    - related_name='favorited_by': Nazwa odwrotnej relacji od rekrutera do użytkowników, którzy dodali go do ulubionych.
    - verbose_name=_('Ulubiony rekruter'): Używa tłumaczenia do wyświetlenia etykiety pola.
    """

    class Meta:
        unique_together = ('user', 'recruiter')
        verbose_name = _('Ulubiony rekruter')
        verbose_name_plural = _('Ulubieni rekruterzy')
        """
        Meta:
        - unique_together: Definiuje unikalność kombinacji pól 'user' i 'recruiter'.
        - verbose_name: Tłumaczenie nazwy pojedynczej.
        - verbose_name_plural: Tłumaczenie nazwy mnogiej.
        """

    def __str__(self):
        """
        Zwraca reprezentację tekstową modelu.

        Returns:
            str: Email użytkownika i email rekrutera.
        """
        return f"{self.user.email} favorites {self.recruiter.user.email}"
