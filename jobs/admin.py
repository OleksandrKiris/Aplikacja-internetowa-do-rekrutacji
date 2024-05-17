from django.contrib import admin
from .models import Job, Application, GuestFeedback, TempGuestFeedback, Like, Favorite

"""
Importy:
- from django.contrib import admin: Importuje moduł administracyjny Django, który umożliwia tworzenie panelu administracyjnego dla modeli.
- from .models import Job, Application, GuestFeedback, TempGuestFeedback, Like, Favorite: Importuje modele, które będą zarządzane przez panel administracyjny.
"""


# --------------------------------------------ADMINISTRACJA MODELI------------------------------------------------------

class JobAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu Job.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
        fields (tuple): Pola wyświetlane w formularzu edycji.
    """
    list_display = ('title', 'recruiter', 'created_at', 'status')
    search_fields = ('title', 'recruiter__email')
    list_filter = ('status', 'created_at')
    ordering = ('created_at',)
    fields = ('title', 'recruiter', 'description', 'requirements', 'salary', 'status')


class ApplicationAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu Application.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
        fields (tuple): Pola wyświetlane w formularzu edycji.
    """
    list_display = ('job', 'applicant', 'created_at', 'status')
    search_fields = ('job__title', 'applicant__email')
    list_filter = ('status', 'created_at')
    ordering = ('created_at',)
    fields = ('job', 'applicant', 'cover_letter', 'status')


class GuestFeedbackAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu GuestFeedback.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
        fields (tuple): Pola wyświetlane w formularzu edycji.
    """
    list_display = ('job', 'email', 'created_at', 'is_verified')
    search_fields = ('job__title', 'email')
    list_filter = ('is_verified', 'created_at')
    ordering = ('created_at',)
    fields = ('job', 'email', 'message', 'phone_number', 'is_verified')


class TempGuestFeedbackAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu TempGuestFeedback.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
        fields (tuple): Pola wyświetlane w formularzu edycji.
    """
    list_display = ('job', 'email', 'created_at')
    search_fields = ('job__title', 'email')
    list_filter = ('created_at',)
    ordering = ('created_at',)
    fields = ('job', 'email', 'message', 'phone_number')


class LikeAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu Like.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
    """
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__email', 'job__title')
    list_filter = ('created_at',)
    ordering = ('created_at',)


class FavoriteAdmin(admin.ModelAdmin):
    """
    Konfiguracja administracyjna dla modelu Favorite.

    Atrybuty:
        list_display (tuple): Pola wyświetlane w widoku listy.
        search_fields (tuple): Pola, które można przeszukiwać.
        list_filter (tuple): Pola, według których można filtrować.
        ordering (tuple): Kolejność sortowania w widoku listy.
    """
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__email', 'job__title')
    list_filter = ('created_at',)
    ordering = ('created_at',)


# Rejestracja modeli i ich konfiguracji w panelu administracyjnym
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(GuestFeedback, GuestFeedbackAdmin)
admin.site.register(TempGuestFeedback, TempGuestFeedbackAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
