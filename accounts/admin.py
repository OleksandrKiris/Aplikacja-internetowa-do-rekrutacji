from django.contrib import admin
from .models import User, CandidateProfile, ClientProfile, RecruiterProfile, Task


# Создание классов admin для более подробного отображения данных в админке
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_admin', 'last_login')
    search_fields = ('email',)
    list_filter = ('is_admin',)


class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')


class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone_number', 'location')
    search_fields = ('user__email', 'company_name')


class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'location')
    search_fields = ('user__email', 'first_name', 'last_name')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'due_date', 'status', 'created_by')
    search_fields = ('title', 'created_by__email')
    list_filter = ('priority', 'status', 'due_date')


# Регистрируем модели в админке
admin.site.register(User, UserAdmin)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(RecruiterProfile, RecruiterProfileAdmin)
admin.site.register(Task, TaskAdmin)
