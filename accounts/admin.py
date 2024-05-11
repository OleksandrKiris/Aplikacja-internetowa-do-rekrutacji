from django.contrib import admin
from .models import User, CandidateProfile, ClientProfile, RecruiterProfile, Task


class UserAdmin(admin.ModelAdmin):
    """
    Konfiguracja panelu administracyjnego dla modelu użytkownika.
    """
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )


class CandidateProfileAdmin(admin.ModelAdmin):
    """
    Konfiguracja panelu administracyjnego dla profilu kandydata.
    """
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')
    ordering = ('user',)


class ClientProfileAdmin(admin.ModelAdmin):
    """
    Konfiguracja panelu administracyjnego dla profilu klienta.
    """
    list_display = ('user', 'company_name', 'industry', 'phone_number', 'location')
    search_fields = ('user__email', 'company_name')
    ordering = ('company_name',)


class RecruiterProfileAdmin(admin.ModelAdmin):
    """
    Konfiguracja panelu administracyjnego dla profilu rekrutera.
    """
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')
    ordering = ('user',)


class TaskAdmin(admin.ModelAdmin):
    """
    Konfiguracja panelu administracyjnego dla modelu zadań.
    """
    list_display = ('title', 'priority', 'status', 'due_date', 'created_by')
    search_fields = ('title', 'created_by__email')
    list_filter = ('priority', 'status', 'due_date')
    ordering = ('due_date',)


# Rejestracja modeli w panelu administracyjnym Django.
admin.site.register(User, UserAdmin)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(RecruiterProfile, RecruiterProfileAdmin)
admin.site.register(Task, TaskAdmin)
