from django import forms
from .models import JobRequest

class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = ['title', 'description', 'requirements', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
