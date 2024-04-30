from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'salary', 'status']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter']
