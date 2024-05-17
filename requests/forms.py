from django import forms
from django.utils.translation import gettext_lazy as _
from .models import JobRequest, JobRequestStatusUpdate

"""
Importy:
- from django import forms: Importuje moduł formularzy Django, który pozwala na tworzenie i zarządzanie formularzami.
- from django.utils.translation import gettext_lazy as _: Importuje funkcję tłumaczenia, umożliwiającą międzynarodowe tłumaczenie tekstów.
- from .models import JobRequest, JobRequestStatusUpdate: Importuje modele JobRequest i JobRequestStatusUpdate z bieżącego modułu, aby wykorzystać je w formularzach.
"""


class JobRequestForm(forms.ModelForm):
    """
    Formularz dla modelu JobRequest.

    Meta:
        model: Model, dla którego tworzony jest formularz.
        fields (list): Pola modelu, które będą w formularzu.
        labels (dict): Etykiety pól w formularzu, używane do tłumaczeń.
        widgets (dict): Widżety formularza, które definiują wygląd i zachowanie pól.
    """

    class Meta:
        model = JobRequest
        fields = ['title', 'description', 'requirements', 'status', 'recruiter']
        labels = {
            'title': _('Tytuł'),
            'description': _('Opis'),
            'requirements': _('Wymagania'),
            'status': _('Status'),
            'recruiter': _('Rekruter')
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Wprowadź tytuł')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Podaj opis')}),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Podaj wymagania')}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recruiter': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicjalizuje formularz z dodatkowymi ustawieniami.

        Args:
            *args: Argumenty pozycyjne.
            **kwargs: Argumenty słownikowe.
        """
        super().__init__(*args, **kwargs)
        """
        Krok 1: Wywołanie konstruktora klasy nadrzędnej, aby zapewnić, że formularz jest prawidłowo zainicjalizowany 
        z przekazanymi argumentami.
        """

        if self.instance and self.instance.pk and self.instance.recruiter:
            """
            Krok 2: Sprawdzenie, czy instancja formularza istnieje (self.instance), 
            czy ma przypisany klucz główny (self.instance.pk) i czy ma przypisanego rekrutera (self.instance.recruiter).
            """

            self.fields['recruiter'].widget.attrs['readonly'] = True
            """
            Krok 3: Jeśli wszystkie warunki są spełnione, ustawienie atrybutu 'readonly' dla pola 'recruiter' 
            w formularzu, co sprawia, że pole staje się tylko do odczytu.
            """

    def clean(self):
        """
        Waliduje dane w formularzu.

        Returns:
            dict: Zwalidowane dane.
        """
        cleaned_data = super().clean()
        """
        Krok 1: Wywołanie metody 'clean' klasy nadrzędnej, aby uzyskać zwalidowane dane z formularza.
        """

        recruiter = cleaned_data.get('recruiter')
        """
        Krok 2: Pobranie wartości pola 'recruiter' z danych po walidacji.
        """

        if self.instance and self.instance.pk and self.instance.recruiter and recruiter != self.instance.recruiter:
            """
            Krok 3: Sprawdzenie, czy instancja formularza istnieje, ma przypisany klucz główny, 
            ma przypisanego rekrutera oraz czy obecny rekruter różni się od pierwotnie przypisanego rekrutera.
            """

            self.add_error('recruiter', _('Recruiter nie może być zmieniony po przypisaniu.'))
            """
            Krok 4: Jeśli warunki są spełnione, dodanie błędu walidacji do pola 'recruiter' z odpowiednim komunikatem.
            """

        return cleaned_data
    # Krok 5: Zwrócenie zwalidowanych danych.


class JobRequestStatusUpdateForm(forms.ModelForm):
    """
    Formularz dla modelu JobRequestStatusUpdate.

    Atrybuty:
        new_status (ChoiceField): Pole wyboru dla nowego statusu zgłoszenia pracy.
        message (CharField): Pole tekstowe dla wiadomości związanej z aktualizacją statusu.
    """
    new_status = forms.ChoiceField(
        choices=JobRequest.RequestStatus.choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_new_status'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Wprowadź swoją wiadomość...'),
                   'id': 'id_message'})
    )

    class Meta:
        model = JobRequestStatusUpdate
        fields = ['new_status', 'message']
        """
        Meta:
            model: Model, dla którego tworzony jest formularz.
            fields (list): Pola modelu, które będą w formularzu.
        """
