from django.contrib import admin
from .models import News

"""
Importy:
- from django.contrib import admin: Importuje moduł administracyjny Django, który umożliwia zarządzanie modelami w panelu administracyjnym.
- from .models import News: Importuje model News z bieżącego modułu, aby zarejestrować go w panelu administracyjnym.
"""

class NewsAdmin(admin.ModelAdmin):
    """
    Klasa definiująca ustawienia wyświetlania modelu News w panelu administracyjnym.

    Atrybuty:
        list_display (tuple): Pola, które będą wyświetlane na liście wiadomości.
        search_fields (tuple): Pola, w których będzie można wyszukiwać wiadomości.
        list_filter (tuple): Pola, według których można filtrować listę wiadomości.
        ordering (tuple): Kolejność wyświetlania wiadomości.
    """
    list_display = ('title', 'date_posted', 'role')
    search_fields = ('title', 'content')
    list_filter = ('role', 'date_posted')
    ordering = ('-date_posted',)

admin.site.register(News, NewsAdmin)
"""
Rejestruje model News w panelu administracyjnym, korzystając z klasy NewsAdmin do konfiguracji wyświetlania.
"""
