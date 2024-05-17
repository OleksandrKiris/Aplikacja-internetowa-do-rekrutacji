# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import User, CandidateProfile, ClientProfile, RecruiterProfile, Task
from .forms import AdminUserCreationForm, AdminUserChangeForm, CandidateProfileForm, ClientProfileForm, \
    RecruiterProfileForm, TaskForm

"""
Imports explanation:

1. from django.contrib import admin
   - admin: Moduł Django używany do rejestracji modeli w panelu administracyjnym. Umożliwia tworzenie i edycję rekordów w bazie danych za pomocą interfejsu administratora.

2. from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
   - UserAdmin: Wbudowana klasa Django do zarządzania użytkownikami w panelu administracyjnym. BaseUserAdmin jest podstawową klasą, którą rozszerzamy, aby dostosować zarządzanie użytkownikami.

3. from django.utils.translation import gettext_lazy as _
   - gettext_lazy: Funkcja używana do oznaczania ciągów znaków jako przeznaczonych do tłumaczenia. Używana do internacjonalizacji tekstu w aplikacjach Django.

4. from django.core.exceptions import ValidationError
   - ValidationError: Wyjątek podnoszony, gdy dane nie przechodzą walidacji. Używany do sygnalizowania błędów walidacji w formularzach i modelach.

5. from .models import User, CandidateProfile, ClientProfile, RecruiterProfile, Task
   - User: Model reprezentujący użytkownika w systemie.
   - CandidateProfile: Model reprezentujący profil kandydata.
   - ClientProfile: Model reprezentujący profil klienta.
   - RecruiterProfile: Model reprezentujący profil rekrutera.
   - Task: Model reprezentujący zadanie.

6. from .forms import AdminUserCreationForm, AdminUserChangeForm, CandidateProfileForm, ClientProfileForm, RecruiterProfileForm, TaskForm
   - AdminUserCreationForm: Formularz tworzenia użytkownika przez administratora.
   - AdminUserChangeForm: Formularz zmiany użytkownika przez administratora.
   - CandidateProfileForm: Formularz profilu kandydata.
   - ClientProfileForm: Formularz profilu klienta.
   - RecruiterProfileForm: Formularz profilu rekrutera.
   - TaskForm: Formularz zadania.
"""


class CustomUserAdmin(BaseUserAdmin):
    """
    Niestandardowy panel administracyjny dla modelu użytkownika.

    Umożliwia zarządzanie użytkownikami w panelu administracyjnym, w tym tworzenie, edycję i usuwanie użytkowników.
    """
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'role')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        (_('Role'), {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'role'),
        }),
    )
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm

    def save_model(self, request, obj, form, change):
        """
        Zapisuje model użytkownika, automatycznie tworząc profil w zależności od roli użytkownika.

        Args:
            request (HttpRequest): Obiekt żądania HTTP.
            obj (User): Obiekt użytkownika.
            form (ModelForm): Formularz modelu.
            change (bool): Czy obiekt jest aktualizowany, a nie tworzony.

        Raises:
            ValidationError: Jeśli nie-superużytkownik próbuje stworzyć rekrutera.
        """
        if not change and obj.role == 'recruiter' and not request.user.is_superuser:
            raise ValidationError(_("Only superusers can create recruiters."))
        super().save_model(request, obj, form, change)

        # Automatyczne tworzenie profilu w zależności od roli użytkownika
        if not change:  # Oznacza to, że użytkownik jest tworzony, a nie aktualizowany
            if obj.role == 'candidate':
                CandidateProfile.objects.create(user=obj)
            elif obj.role == 'client':
                ClientProfile.objects.create(user=obj)
            elif obj.role == 'recruiter':
                RecruiterProfile.objects.create(user=obj)


class CandidateProfileAdmin(admin.ModelAdmin):
    """
    Panel administracyjny dla profilu kandydata.

    Umożliwia zarządzanie profilami kandydatów w panelu administracyjnym.
    """
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')
    ordering = ('user',)
    form = CandidateProfileForm


class ClientProfileAdmin(admin.ModelAdmin):
    """
    Panel administracyjny dla profilu klienta.

    Umożliwia zarządzanie profilami klientów w panelu administracyjnym.
    """
    list_display = ('user', 'company_name', 'industry', 'phone_number', 'location')
    search_fields = ('user__email', 'company_name')
    ordering = ('company_name',)
    form = ClientProfileForm


class RecruiterProfileAdmin(admin.ModelAdmin):
    """
    Panel administracyjny dla profilu rekrutera.

    Umożliwia zarządzanie profilami rekruterów w panelu administracyjnym.
    """
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')
    ordering = ('user',)
    form = RecruiterProfileForm


class TaskAdmin(admin.ModelAdmin):
    """
    Panel administracyjny dla zadań.

    Umożliwia zarządzanie zadaniami w panelu administracyjnym.
    """
    list_display = ('title', 'priority', 'status', 'due_date', 'created_by')
    search_fields = ('title', 'created_by__email')
    list_filter = ('priority', 'status', 'due_date')
    ordering = ('due_date',)
    form = TaskForm


# Rejestracja modeli w panelu administracyjnym
admin.site.register(User, CustomUserAdmin)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(RecruiterProfile, RecruiterProfileAdmin)
admin.site.register(Task, TaskAdmin)
