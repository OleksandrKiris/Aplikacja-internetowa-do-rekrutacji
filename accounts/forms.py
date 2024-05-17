from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, ReadOnlyPasswordHashField
from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

"""
Imports explanation:

1. from django import forms
   - forms: Moduł Django używany do tworzenia i zarządzania formularzami. Zapewnia narzędzia do tworzenia formularzy HTML, ich walidacji i przetwarzania danych.

2. from django.contrib.auth import get_user_model
   - get_user_model: Funkcja Django, która zwraca model użytkownika aktualnie aktywnego w projekcie. Używana do uzyskiwania dostępu do niestandardowego modelu użytkownika.

3. from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, ReadOnlyPasswordHashField
   - UserCreationForm: Wbudowany formularz Django do tworzenia nowych użytkowników. Zapewnia pola do wprowadzania i potwierdzania hasła.
   - AuthenticationForm: Wbudowany formularz Django do uwierzytelniania użytkowników. Zapewnia pola do wprowadzania nazwy użytkownika i hasła.
   - ReadOnlyPasswordHashField: Pole formularza Django do wyświetlania skrótu hasła w formularzu tylko do odczytu. Używane w formularzach administracyjnych.

4. from accounts.models import CandidateProfile, ClientProfile, RecruiterProfile, Task
   - CandidateProfile: Model reprezentujący profil kandydata. Zawiera dodatkowe informacje o kandydacie.
   - ClientProfile: Model reprezentujący profil klienta. Zawiera dodatkowe informacje o kliencie (pracodawcy).
   - RecruiterProfile: Model reprezentujący profil rekrutera. Zawiera dodatkowe informacje o rekruterze.
   - Task: Model reprezentujący zadanie. Zawiera informacje o zadaniach tworzonych przez rekruterów.

5. from django.utils.translation import gettext_lazy as _
   - gettext_lazy: Funkcja używana do oznaczania ciągów znaków jako przeznaczonych do tłumaczenia. Używana do internacjonalizacji tekstu w aplikacjach Django.

6. from django.core.exceptions import ValidationError
   - ValidationError: Wyjątek podnoszony, gdy dane nie przechodzą walidacji. Używany do sygnalizowania błędów walidacji w formularzach i modelach.
"""

User = get_user_model()
"""
Pobiera aktualnie aktywny model użytkownika.

Funkcja get_user_model() jest używana do uzyskiwania dostępu do niestandardowego modelu użytkownika w projekcie Django. 
Zamiast bezpośredniego odniesienia do User, korzystamy z tej funkcji, aby uzyskać model użytkownika, 
który może być różny w zależności od konfiguracji projektu.
"""


class UserRegistrationForm(UserCreationForm):
    """
    Formularz rejestracji użytkownika.

    Umożliwia użytkownikom rejestrację w systemie, wprowadzając adres e-mail, hasło i wybierając rolę.

    Attributes:
        ROLE_CHOICES (list): Lista wyborów ról użytkownika (kandydat, klient).
        role (ChoiceField): Pole wyboru roli użytkownika.
    """

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
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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
    """
    Formularz profilu kandydata.

    Umożliwia użytkownikom wprowadzanie i aktualizowanie informacji w profilu kandydata.

    Attributes:
        Meta (class): Klasa meta zawierająca konfigurację formularza.
    """

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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
    """
    Formularz profilu klienta.

    Umożliwia użytkownikom wprowadzanie i aktualizowanie informacji w profilu klienta (pracodawcy).

    Attributes:
        Meta (class): Klasa meta zawierająca konfigurację formularza.
    """

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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
    """
    Formularz profilu rekrutera.

    Umożliwia użytkownikom wprowadzanie i aktualizowanie informacji w profilu rekrutera.

    Attributes:
        Meta (class): Klasa meta zawierająca konfigurację formularza.
    """

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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
    """
    Formularz logowania użytkownika.

    Umożliwia użytkownikom wprowadzanie danych logowania i uwierzytelnianie się w systemie.

    Attributes:
        username (EmailField): Pole do wprowadzania adresu e-mail.
        password (CharField): Pole do wprowadzania hasła.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _('Wprowadź email')}
        )
    )
    password = forms.CharField(
        label=_("Hasło"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('Wprowadź hasło')}
        )
    )


class TaskForm(forms.ModelForm):
    """
    Formularz zadania.

    Umożliwia rekruterom tworzenie i aktualizowanie zadań.

    Attributes:
        Meta (class): Klasa meta zawierająca konfigurację formularza.
    """

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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


class AdminUserCreationForm(UserCreationForm):
    """
    Formularz tworzenia użytkownika przez administratora.

    Umożliwia administratorom tworzenie nowych użytkowników z określoną rolą.

    Attributes:
        ROLE_CHOICES (list): Lista wyborów ról użytkownika (kandydat, klient, rekruter).
        role (ChoiceField): Pole wyboru roli użytkownika.
    """
    ROLE_CHOICES = [
        ('candidate', _('Kandydat')),
        ('client', _('Klient')),
        ('recruiter', _('Rekruter'))
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
            labels (dict): Słownik etykiet dla pól formularza.
            widgets (dict): Słownik widgetów formularza do niestandardowego renderowania pól.
        """
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


class PasswordChangeForm(forms.Form):
    """
    Formularz zmiany hasła.

    Umożliwia użytkownikom zmianę hasła.

    Attributes:
        new_password (CharField): Pole do wprowadzania nowego hasła.
        new_password_confirm (CharField): Pole do potwierdzenia nowego hasła.
    """
    new_password = forms.CharField(
        label=_('Nowe hasło'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Wprowadź nowe hasło'),
            'required': 'required'
        })
    )
    new_password_confirm = forms.CharField(
        label=_('Potwierdź nowe hasło'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Potwierdź nowe hasło'),
            'required': 'required'
        })
    )

    def clean(self):
        """
        Sprawdza, czy nowe hasło i potwierdzenie hasła są zgodne.

        Raises:
            ValidationError: Jeśli hasła się nie zgadzają.
        """
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValidationError(_("Hasła się nie zgadzają"))

        return cleaned_data


class AdminUserChangeForm(forms.ModelForm):
    """
    Formularz zmiany użytkownika przez administratora.

    Umożliwia administratorom aktualizowanie informacji o użytkownikach.

    Attributes:
        password (ReadOnlyPasswordHashField): Pole do wyświetlania skrótu hasła w formularzu tylko do odczytu.
    """
    password = ReadOnlyPasswordHashField(
        label=_("Hasło"),
        help_text=_("Nie przechowujemy jawnych haseł, więc nie można zobaczyć hasła tego użytkownika, ale możesz "
                    "zmienić hasło używając <a href=\"../password/\">tego formularza</a>.")
    )

    class Meta:
        """
        Klasa meta zawierająca konfigurację formularza.

        Attributes:
            model (Model): Model powiązany z tym formularzem.
            fields (list): Lista pól, które mają być uwzględnione w formularzu.
        """
        model = User
        fields = ('email', 'password', 'is_active', 'is_staff', 'is_superuser', 'role')

    def clean_password(self):
        """
        Zwraca początkową wartość hasła niezależnie od tego, co użytkownik poda.

        Returns:
            str: Początkowa wartość hasła.
        """
        return self.initial["password"]
