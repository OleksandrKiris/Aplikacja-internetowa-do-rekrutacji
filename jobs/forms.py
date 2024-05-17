from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Job, Application, GuestFeedback

"""
Importy:
- from django import forms: Importuje moduł formularzy Django, który umożliwia tworzenie i zarządzanie formularzami.
- from django.utils.translation import gettext_lazy as _: Importuje funkcję tłumaczenia, która umożliwia międzynarodowe tłumaczenie tekstów.
- from .models import Job, Application, GuestFeedback: Importuje modele, które będą używane w formularzach.
"""


class JobForm(forms.ModelForm):
    """
    Formularz do tworzenia i edycji obiektów Job.

    Meta klasa:
        model (Job): Model, który formularz reprezentuje.
        fields (list): Lista pól modelu, które będą uwzględnione w formularzu.
        labels (dict): Słownik mapujący nazwy pól na etykiety do wyświetlenia w formularzu.
        widgets (dict): Słownik określający widgety formularza dla poszczególnych pól.
    """

    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'salary', 'status']
        labels = {
            'title': _('Tytuł'),
            'description': _('Opis'),
            'requirements': _('Wymagania'),
            'salary': _('Wynagrodzenie'),
            'status': _('Status'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Wprowadź tytuł')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Wprowadź opis stanowiska')
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Wprowadź wymagania stanowiska')
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Wprowadź wynagrodzenie')
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class ApplicationForm(forms.ModelForm):
    """
    Formularz do tworzenia i edycji obiektów Application.

    Meta klasa:
        model (Application): Model, który formularz reprezentuje.
        fields (list): Lista pól modelu, które będą uwzględnione w formularzu.
        labels (dict): Słownik mapujący nazwy pól na etykiety do wyświetlenia w formularzu.
        widgets (dict): Słownik określający widgety formularza dla poszczególnych pól.
    """

    class Meta:
        model = Application
        fields = ['cover_letter']
        labels = {
            'cover_letter': _('List Motywacyjny')
        }
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Wprowadź list motywacyjny')
            })
        }


class GuestFeedbackForm(forms.ModelForm):
    """
    Formularz do tworzenia i edycji obiektów GuestFeedback.

    Meta klasa:
        model (GuestFeedback): Model, który formularz reprezentuje.
        fields (list): Lista pól modelu, które będą uwzględnione w formularzu.
        labels (dict): Słownik mapujący nazwy pól na etykiety do wyświetlenia w formularzu.
        widgets (dict): Słownik określający widgety formularza dla poszczególnych pól.
    """

    class Meta:
        model = GuestFeedback
        fields = ['email', 'message', 'phone_number']
        labels = {
            'email': _('Email'),
            'message': _('Wiadomość'),
            'phone_number': _('Numer Telefonu (opcjonalnie)')
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Wprowadź email')
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Wprowadź opinię')
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Wprowadź numer telefonu')
            }),
        }
