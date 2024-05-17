
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

from accounts import views
from accounts.views import HomeView, AboutView, ContactView
from django.conf import settings
from django.conf.urls.static import static

"""
Importy modułów Django:
- admin: Panel administracyjny Django.
- path, include: Funkcje Django do definiowania tras URL.
- set_language: Widok Django do zmiany języka.
- settings: Konfiguracja ustawień projektu.
- static: Funkcja do obsługi plików statycznych.
"""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('requests/', include('requests.urls')),
    path('', HomeView.as_view(), name='home'),
    path('o-nas/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('set-language/', set_language, name='set_language'),
    path('news/', include('news.urls')),
    path('set_language/<str:language>/', views.set_language, name='set_language'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
Definiowanie tras URL w projekcie Django:
- admin/: Panel administracyjny Django.
- accounts/: Moduł odpowiedzialny za zarządzanie kontami użytkowników.
- jobs/: Moduł odpowiedzialny za zarządzanie ofertami pracy.
- requests/: Moduł odpowiedzialny za obsługę żądań.
- '': Główna strona aplikacji, obsługiwana przez HomeView.
- o-nas/: Strona "O nas", obsługiwana przez AboutView.
- contact/: Strona kontaktowa, obsługiwana przez ContactView.
- set-language/: Widok zmiany języka.
- news/: Moduł odpowiedzialny za zarządzanie aktualnościami.
- set_language/<str:language>/: Widok zmiany języka dla podanego kodu języka.

Do tego dodajemy obsługę plików statycznych za pomocą static(), używając MEDIA_URL i MEDIA_ROOT z ustawień projektu.
"""
