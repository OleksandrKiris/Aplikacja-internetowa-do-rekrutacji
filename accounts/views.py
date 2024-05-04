from django.contrib.auth import logout, login  # Funkcje Django do obsługi wylogowywania i logowania użytkowników
from django.contrib.auth.decorators import \
    login_required  # Dekorator sprawdzający, czy użytkownik jest zalogowany, i wymagający zalogowania
from django.http import Http404  # Wyjątek używany do zgłaszania błędów 404
from django.shortcuts import redirect, render, \
    get_object_or_404  # Funkcje Django do przekierowania, renderowania szablonów i pobierania obiektów
from django.urls import reverse_lazy, reverse  # Funkcje do wygodnego tworzenia odwołań URL w Django
from django.views.generic import TemplateView, ListView  # Generyczne widoki zdefiniowane przez Django
from accounts.forms import (RecruiterProfileForm, TaskForm, ClientProfileForm, CandidateProfileForm,
                            UserLoginForm,
                            UserRegistrationForm)  # Importowanie formularzy używanych w aplikacji do obsługi danych
from accounts.models import RecruiterProfile, Task, ClientProfile, \
    CandidateProfile  # Importowanie modeli danych aplikacji
from jobs.models import Job  # Importowanie modelu Job, definiującego dane ofert pracy
from news.models import News

"---------------------------------------------------STRONA GŁÓWNA------------------------------------------------------"


# Klasa HomeView rozszerza TemplateView i obsługuje widok strony głównej
class HomeView(TemplateView):
    template_name = 'home/base.html'  # Ustawienie szablonu HTML, który ma być używany w widoku

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Pobiera istniejący kontekst danych
        # Filtruje oferty pracy na podstawie statusu (tylko otwarte oferty)
        context['jobs'] = Job.objects.filter(status=Job.JobStatus.OPEN)
        return context  # Zwraca kontekst zawierający dane do wyświetlenia w szablonie


# Klasa AboutView rozszerza TemplateView i obsługuje widok strony "O nas"
class AboutView(TemplateView):
    template_name = 'home/about_us.html'  # Ustawienie szablonu HTML


# Klasa ContactView rozszerza TemplateView i obsługuje widok strony kontaktowej
class ContactView(TemplateView):
    template_name = 'home/contact.html'  # Ustawienie szablonu HTML


"-------------------------------REJESTRACJA, LOGOWANIE, TWORZENIE PROFILU, WYLOGOWANIE---------------------------------"


# Klasa RecruiterListView rozszerza ListView i obsługuje widok listy rekruterów
class RecruiterListView(ListView):
    model = RecruiterProfile  # Określenie modelu danych reprezentującego rekruterów
    template_name = 'home/recruiters.html'  # Ustawienie szablonu HTML
    context_object_name = 'recruiters'  # Nazwa zmiennej w szablonie zawierającej dane rekruterów


# Klasa ClientListView rozszerza ListView i obsługuje widok listy klientów
class ClientListView(ListView):
    model = ClientProfile  # Określenie modelu danych reprezentującego klientów
    template_name = 'home/client_list.html'  # Ustawienie szablonu HTML
    context_object_name = 'clients'  # Nazwa zmiennej w szablonie zawierającej dane klientów


# Funkcja do obsługi rejestracji użytkowników
def register_user(request):
    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane rejestracji
        form = UserRegistrationForm(request.POST)  # Tworzymy formularz rejestracji z danymi POST
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            user = form.save()  # Zapisuje nowego użytkownika w bazie danych
            # Przekierowuje użytkownika do widoku tworzenia profilu
            return redirect(reverse_lazy('accounts:create_profile'))
    else:  # Jeśli żądanie to GET, wyświetlamy pusty formularz rejestracji
        form = UserRegistrationForm()
    # Renderuje szablon strony rejestracji z formularzem
    return render(request, 'registration/register.html', {'form': form})


# Funkcja do obsługi logowania użytkowników
def login_view(request):
    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane logowania
        form = UserLoginForm(data=request.POST)  # Tworzymy formularz logowania z danymi POST
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            user = form.get_user()  # Pobiera użytkownika na podstawie danych logowania
            login(request, user)  # Loguje użytkownika, ustanawiając sesję

            # Zapisuje rolę użytkownika w sesji
            request.session['role'] = user.role

            # Po pomyślnym logowaniu przekierowuje użytkownika do panelu kontrolnego
            return redirect(reverse_lazy('accounts:dashboard'))
        else:  # Jeśli dane logowania są niepoprawne, wyświetlamy komunikat o błędzie
            return render(request, 'registration/login.html', {
                'form': form,  # Ponownie przekazuje formularz do wyświetlenia
                'error': 'Nieprawidłowa nazwa użytkownika lub hasło'  # Komunikat błędu w języku polskim
            })
    else:  # Jeśli żądanie to GET, wyświetlamy pusty formularz logowania
        form = UserLoginForm()

    # Renderuje szablon strony logowania z formularzem
    return render(request, 'registration/login.html', {'form': form})


# Funkcja do obsługi wylogowywania użytkowników
def logout_view(request):
    logout(request)  # Wylogowuje użytkownika i usuwa sesję
    return redirect(reverse_lazy('home'))  # Przekierowuje na stronę główną


# Funkcja do tworzenia profilu użytkownika, dostępna tylko dla zalogowanych użytkowników
@login_required
def create_profile(request):
    form_classes = {  # Słownik mapujący role użytkowników na odpowiednie formularze profilu
        'candidate': CandidateProfileForm,  # Formularz dla kandydatów
        'client': ClientProfileForm,  # Formularz dla klientów
    }
    # Pobiera odpowiedni formularz na podstawie roli użytkownika
    form_class = form_classes.get(request.user.role)
    if not form_class:  # Jeśli nie znaleziono formularza dla roli, zgłaszamy wyjątek 404
        raise Http404("Ten typ roli nie jest dozwolony do tworzenia profilu.")

    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane profilu
        form = form_class(request.POST, request.FILES)  # Tworzy formularz na podstawie danych POST i plików
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            profile = form.save(commit=False)  # Tworzy obiekt profilu, ale nie zapisuje go jeszcze
            profile.user = request.user  # Ustawia bieżącego użytkownika jako właściciela profilu
            profile.save()  # Zapisuje profil w bazie danych
            return redirect('accounts:dashboard')  # Przekierowuje do panelu kontrolnego
    else:  # Jeśli żądanie to GET, tworzy pusty formularz
        form = form_class()

    # Renderuje szablon strony tworzenia profilu z formularzem
    return render(request, 'registration/create_profile.html', {'form': form})


#@login_required
def dashboard_view(request):
    role = request.user.role
    news_list = News.objects.filter(role=role).order_by('-date_posted')

    return render(request, 'dashboard/dashboard.html', {
        'role': role,
        'news_list': news_list
    })


"------------------------------------------SZCZEGÓŁY PROFILU, ZMIANA DANYCH--------------------------------------------"


# Widok szczegółów profilu, dostępny tylko dla zalogowanych użytkowników
@login_required
def profile_detail_view(request):
    user = request.user  # Pobiera bieżącego użytkownika z sesji
    profile_model = {  # Słownik mapujący role użytkownika na odpowiednie modele profilu
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)  # Pobiera model profilu na podstawie roli użytkownika

    if not profile_model:  # Jeśli nie znaleziono modelu, zgłaszamy wyjątek 404
        raise Http404("Profil nie został znaleziony dla bieżącego użytkownika.")

    try:
        # Próbuje pobrać profil użytkownika z bazy danych
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:  # Jeśli profil nie istnieje, przekierowuje do tworzenia profilu
        return redirect(reverse_lazy('accounts:create_profile'))

    # Przygotowuje kontekst z danymi profilu do wyświetlenia w szablonie
    context = {
        'profile': profile,
        'profile_type': user.role  # Typ profilu na podstawie roli użytkownika
    }
    # Renderuje szablon szczegółów profilu z danymi w kontekście
    return render(request, 'profiles/universal_profile_detail.html', context)


# Widok edycji profilu, dostępny tylko dla zalogowanych użytkowników
@login_required
def profile_edit_view(request):
    user = request.user  # Pobiera bieżącego użytkownika z sesji
    profile_model = {  # Słownik mapujący role użytkownika na odpowiednie modele profilu
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)  # Pobiera model profilu na podstawie roli użytkownika

    if not profile_model:  # Jeśli nie znaleziono modelu, zgłaszamy wyjątek 404
        raise Http404("Profil nie został znaleziony dla bieżącego użytkownika.")

    try:
        # Próbuje pobrać profil użytkownika z bazy danych
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:  # Jeśli profil nie istnieje, przekierowuje do tworzenia profilu
        return redirect(reverse_lazy('accounts:create_profile'))

    # Słownik mapujący role użytkownika na odpowiednie formularze edycji profilu
    form_class = {
        'candidate': CandidateProfileForm,
        'client': ClientProfileForm,
        'recruiter': RecruiterProfileForm
    }.get(user.role)  # Pobiera odpowiedni formularz na podstawie roli użytkownika

    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane edycji profilu
        # Tworzy formularz z istniejącymi danymi profilu i danymi POST
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            form.save()  # Zapisuje zmiany w profilu w bazie danych
            return redirect(reverse_lazy('accounts:dashboard'))  # Przekierowuje do panelu kontrolnego
    else:  # Jeśli żądanie to GET, tworzy formularz z istniejącymi danymi profilu
        form = form_class(instance=profile)

    # Renderuje szablon edycji profilu z formularzem
    return render(request, 'profiles/universal_profile_edit.html', {'form': form})


"------------------------------------------ZADANIA REKRUTERA------------------------------------------------------------"


# Widok listy zadań, dostępny tylko dla zalogowanych użytkowników
@login_required
def task_list_view(request):
    tasks = Task.objects.filter(created_by=request.user)  # Pobiera zadania utworzone przez bieżącego użytkownika
    # Renderuje szablon z listą zadań i przekazuje zadania do wyświetlenia
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


# Widok tworzenia zadania, dostępny tylko dla zalogowanych użytkowników
@login_required
def task_create_view(request):
    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane zadania
        form = TaskForm(request.POST)  # Tworzy formularz tworzenia zadania z danymi POST
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            # Tworzy obiekt zadania, ale nie zapisuje go jeszcze
            task = form.save(commit=False)
            task.created_by = request.user  # Ustawia bieżącego użytkownika jako twórcę zadania
            task.save()  # Zapisuje zadanie w bazie danych
            return redirect(reverse_lazy('accounts:task_list'))  # Przekierowuje do listy zadań
    else:  # Jeśli żądanie to GET, tworzy pusty formularz
        form = TaskForm()

    # Renderuje szablon tworzenia zadania z formularzem
    return render(request, 'tasks/task_form.html', {'form': form})


# Widok edycji zadania, dostępny tylko dla zalogowanych użytkowników
@login_required
def task_update_view(request, task_id):
    # Pobiera zadanie na podstawie ID i sprawdza, czy zostało utworzone przez bieżącego użytkownika
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy dane edycji zadania
        form = TaskForm(request.POST, instance=task)  # Tworzy formularz edycji zadania z danymi POST
        if form.is_valid():  # Sprawdza, czy formularz jest poprawny
            form.save()  # Zapisuje zmiany w zadaniu w bazie danych
            return redirect(reverse_lazy('accounts:task_list'))  # Przekierowuje do listy zadań
    else:  # Jeśli żądanie to GET, tworzy formularz z istniejącymi danymi zadania
        form = TaskForm(instance=task)

    # Renderuje szablon edycji zadania z formularzem
    return render(request, 'tasks/task_form.html', {'form': form})


# Widok usuwania zadania, dostępny tylko dla zalogowanych użytkowników
@login_required
def task_delete_view(request, task_id):
    # Pobiera zadanie na podstawie ID i sprawdza, czy zostało utworzone przez bieżącego użytkownika
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':  # Jeśli żądanie to POST, przetwarzamy żądanie usunięcia zadania
        task.delete()  # Usuwa zadanie z bazy danych
        return redirect(reverse_lazy('accounts:task_list'))  # Przekierowuje do listy zadań

    # Renderuje szablon potwierdzenia usunięcia zadania
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
