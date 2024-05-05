from django import forms
from .models import Job, Application, GuestFeedback


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'salary', 'status']
        labels = {
            'title': 'Tytuł',
            'description': 'Opis',
            'requirements': 'Wymagania',
            'salary': 'Wynagrodzenie',
            'status': 'Status',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wprowadź tytuł'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Wprowadź opis stanowiska'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Wprowadź wymagania stanowiska'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wprowadź wynagrodzenie'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        labels = {
            'cover_letter': 'List Motywacyjny'
        }
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Wprowadź list motywacyjny'
            })
        }


class GuestFeedbackForm(forms.ModelForm):
    class Meta:
        model = GuestFeedback
        fields = ['email', 'message', 'phone_number']
        labels = {
            'email': 'Email',
            'message': 'Wiadomość',
            'phone_number': 'Numer Telefonu (opcjonalnie)'
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wprowadź email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Wprowadź opinię'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wprowadź numer telefonu'
            }),
        }
