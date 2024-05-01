from django.contrib import admin
from .models import JobRequest


class JobRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'status', 'recruiter', 'created_at')
    search_fields = ('title', 'employer__username', 'recruiter__username')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


admin.site.register(JobRequest, JobRequestAdmin)
