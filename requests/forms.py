from django import forms
from .models import JobRequest, JobRequestStatusUpdate


class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = ['title', 'description', 'requirements', 'status', 'recruiter']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź tytuł'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Podaj opis'}),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Podaj wymagania'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recruiter': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.recruiter:
            self.fields['recruiter'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        recruiter = cleaned_data.get('recruiter')
        if self.instance and self.instance.pk and self.instance.recruiter and recruiter != self.instance.recruiter:
            self.add_error('recruiter', 'Recruiter cannot be changed once assigned.')
        return cleaned_data



class JobRequestStatusUpdateForm(forms.ModelForm):
    new_status = forms.ChoiceField(
        choices=JobRequest.RequestStatus.choices,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_new_status'
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Wprowadź swoją wiadomość...',
            'id': 'id_message'
        })
    )

    class Meta:
        model = JobRequestStatusUpdate
        fields = ['new_status', 'message']
