from django.contrib import admin
from .models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter

"""
Importy:
- from django.contrib import admin: Importuje moduł administracyjny Django, który umożliwia zarządzanie modelami w panelu administracyjnym.
- from .models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter: Importuje modele JobRequest, JobRequestStatusUpdate i FavoriteRecruiter z bieżącego modułu, aby zarejestrować je w panelu administracyjnym.
"""


class JobRequestAdmin(admin.ModelAdmin):
    """
    Klasa definiująca ustawienia wyświetlania modelu JobRequest w panelu administracyjnym.

    Atrybuty:
        list_display (tuple): Pola, które będą wyświetlane na liście zgłoszeń pracy.
        search_fields (tuple): Pola, w których będzie można wyszukiwać zgłoszenia pracy.
        list_filter (tuple): Pola, według których można filtrować listę zgłoszeń pracy.
        ordering (tuple): Kolejność wyświetlania zgłoszeń pracy.
    """
    list_display = ('title', 'employer', 'status', 'created_at', 'recruiter')
    search_fields = ('title', 'description', 'employer__email', 'recruiter__email')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


class JobRequestStatusUpdateAdmin(admin.ModelAdmin):
    """
    Klasa definiująca ustawienia wyświetlania modelu JobRequestStatusUpdate w panelu administracyjnym.

    Atrybuty:
        list_display (tuple): Pola, które będą wyświetlane na liście aktualizacji statusu zgłoszeń pracy.
        search_fields (tuple): Pola, w których będzie można wyszukiwać aktualizacje statusu zgłoszeń pracy.
        list_filter (tuple): Pola, według których można filtrować listę aktualizacji statusu zgłoszeń pracy.
        ordering (tuple): Kolejność wyświetlania aktualizacji statusu zgłoszeń pracy.
    """
    list_display = ('job_request', 'new_status', 'updated_by', 'updated_at')
    search_fields = ('job_request__title', 'updated_by__email', 'message')
    list_filter = ('new_status', 'updated_at')
    ordering = ('-updated_at',)


class FavoriteRecruiterAdmin(admin.ModelAdmin):
    """
    Klasa definiująca ustawienia wyświetlania modelu FavoriteRecruiter w panelu administracyjnym.

    Atrybuty:
        list_display (tuple): Pola, które będą wyświetlane na liście ulubionych rekruterów.
        search_fields (tuple): Pola, w których będzie można wyszukiwać ulubionych rekruterów.
        ordering (tuple): Kolejność wyświetlania ulubionych rekruterów.
    """
    list_display = ('user', 'recruiter')
    search_fields = ('user__email', 'recruiter__user__email')
    ordering = ('user',)


admin.site.register(JobRequest, JobRequestAdmin)
"""
Rejestruje model JobRequest w panelu administracyjnym, korzystając z klasy JobRequestAdmin do konfiguracji wyświetlania.
"""
admin.site.register(JobRequestStatusUpdate, JobRequestStatusUpdateAdmin)
"""
Rejestruje model JobRequestStatusUpdate w panelu administracyjnym, korzystając z klasy JobRequestStatusUpdateAdmin do konfiguracji wyświetlania.
"""
admin.site.register(FavoriteRecruiter, FavoriteRecruiterAdmin)
"""
Rejestruje model FavoriteRecruiter w panelu administracyjnym, korzystając z klasy FavoriteRecruiterAdmin do konfiguracji wyświetlania.
"""
