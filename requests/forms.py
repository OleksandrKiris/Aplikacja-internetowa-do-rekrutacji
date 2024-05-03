from django import forms
from .models import JobRequest, JobRequestStatusUpdate


class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = ['title', 'description', 'requirements', 'status', 'recruiter']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'recruiter': forms.Select(attrs={'class': 'form-control'}),
        }


class JobRequestStatusUpdateForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = JobRequestStatusUpdate
        fields = ['new_status', 'message']
