from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from django.utils.translation import gettext as _

# Получение текущей модели пользователя
User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('candidate', _('Kandydat')),
        ('client', _('Klient'))
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'role']
        labels = {
            'email': _('Email'),
            'password1': _('Hasło'),
            'password2': _('Potwierdź hasło'),
            'role': _('Rola')
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź email')}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź hasło')}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Potwierdź hasło')})
        }


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio', 'date_of_birth', 'skills']
        labels = {
            'first_name': _('Imię'),
            'last_name': _('Nazwisko'),
            'phone_number': _('Numer telefonu'),
            'photo': _('Zdjęcie'),
            'location': _('Lokalizacja'),
            'bio': _('Biografia'),
            'date_of_birth': _('Data urodzenia'),
            'skills': _('Umiejętności')
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź imię')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź nazwisko')}),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('Wprowadź numer telefonu')}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź lokalizację')}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Wprowadź biografię')}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'skills': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2, 'placeholder': _('Wprowadź umiejętności')})
        }


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['phone_number', 'photo', 'location', 'bio', 'company_name', 'industry']
        labels = {
            'phone_number': _('Numer telefonu'),
            'photo': _('Zdjęcie'),
            'location': _('Lokalizacja'),
            'bio': _('Biografia'),
            'company_name': _('Nazwa firmy'),
            'industry': _('Branża')
        }
        widgets = {
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('Wprowadź numer telefonu')}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź lokalizację')}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Wprowadź biografię')}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź nazwę firmy')}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź branżę')})
        }


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio']
        labels = {
            'first_name': _('Imię'),
            'last_name': _('Nazwisko'),
            'phone_number': _('Numer telefonu'),
            'photo': _('Zdjęcie'),
            'location': _('Lokalizacja'),
            'bio': _('Biografia')
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź imię')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź nazwisko')}),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('Wprowadź numer telefonu')}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź lokalizację')}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Wprowadź biografię')})
        }


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label=_("Email"),
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'placeholder': _('Wprowadź email')}))
    password = forms.CharField(label=_("Hasło"),
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': _('Wprowadź hasło')}))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'status']
        labels = {
            'title': _('Tytuł'),
            'description': _('Opis'),
            'priority': _('Priorytet'),
            'due_date': _('Termin wykonania'),
            'status': _('Status')
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź tytuł')}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Wprowadź opis')}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }
