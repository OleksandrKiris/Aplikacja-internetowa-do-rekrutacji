from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task

# Pobieranie aktualnie aktywnego modelu użytkownika zdefiniowanego w ustawieniach Django.
# Jest to zalecane podejście w przypadku, gdy model użytkownika może być dostosowywany
# i zmieniany w przyszłości. Funkcja `get_user_model()` zawsze zwróci aktualny model.
User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Formularz rejestracji użytkownika, który rozszerza standardowy formularz Django o możliwość wyboru roli.
    Dodanie pola 'role' pozwala na zdefiniowanie, czy użytkownik rejestruje się jako kandydat czy klient.
    """
    ROLE_CHOICES = [
        ('candidate', 'Kandydat'),
        ('client', 'Klient')
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
            'email': 'Email',
            'password1': 'Hasło',
            'password2': 'Potwierdź hasło',
            'role': 'Rola'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź hasło'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Potwierdź hasło'})
        }


class CandidateProfileForm(forms.ModelForm):
    """
    Formularz do tworzenia i edycji profilu kandydata zawiera pola umożliwiające wprowadzenie imienia, nazwiska,
    numeru telefonu, zdjęcia, lokalizacji, biografii, daty urodzenia oraz umiejętności.
    """

    class Meta:
        model = CandidateProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio', 'date_of_birth', 'skills']
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'phone_number': 'Numer telefonu',
            'photo': 'Zdjęcie',
            'location': 'Lokalizacja',
            'bio': 'Biografia',
            'date_of_birth': 'Data urodzenia',
            'skills': 'Umiejętności'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź imię'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź nazwisko'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź numer telefonu'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź lokalizację'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Wprowadź biografię'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Wprowadź umiejętności'})
        }


class ClientProfileForm(forms.ModelForm):
    """
    Formularz dla profilu klienta zawiera pola do wprowadzenia danych takich jak numer telefonu,
    zdjęcie, lokalizacja, biografia, nazwa firmy i branża.
    """

    class Meta:
        model = ClientProfile
        fields = ['phone_number', 'photo', 'location', 'bio', 'company_name', 'industry']
        labels = {
            'phone_number': 'Numer telefonu',
            'photo': 'Zdjęcie',
            'location': 'Lokalizacja',
            'bio': 'Biografia',
            'company_name': 'Nazwa firmy',
            'industry': 'Branża'
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź numer telefonu'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź lokalizację'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Wprowadź biografię'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź nazwę firmy'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź branżę'})
        }


class RecruiterProfileForm(forms.ModelForm):
    """
    Formularz do tworzenia i edycji profilu rekrutera umożliwia wprowadzenie informacji takich jak imię, nazwisko,
    numer telefonu, zdjęcie, lokalizacja oraz biografia.
    """

    class Meta:
        model = RecruiterProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio']
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'phone_number': 'Numer telefonu',
            'photo': 'Zdjęcie',
            'location': 'Lokalizacja',
            'bio': 'Biografia'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź imię'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź nazwisko'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź numer telefonu'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź lokalizację'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Wprowadź biografię'})
        }


class UserLoginForm(AuthenticationForm):
    """
    Formularz logowania dla użytkowników używa adresu email jako nazwy użytkownika oraz hasła.
    """
    username = forms.EmailField(label="Email",
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Wprowadź email'}))
    password = forms.CharField(label="Hasło",
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': 'Wprowadź hasło'}))


class TaskForm(forms.ModelForm):
    """
    Formularz do zarządzania zadaniami, umożliwiający definiowanie tytułu, opisu, priorytetu,
    terminu wykonania oraz statusu zadania.
    """

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'status']
        labels = {
            'title': 'Tytuł',
            'description': 'Opis',
            'priority': 'Priorytet',
            'due_date': 'Termin wykonania',
            'status': 'Status'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź tytuł'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Wprowadź opis'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }
