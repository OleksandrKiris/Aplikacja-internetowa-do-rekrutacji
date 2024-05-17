from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from accounts.forms import (
    RecruiterProfileForm, TaskForm, ClientProfileForm,
    CandidateProfileForm, UserLoginForm, UserRegistrationForm, PasswordChangeForm
)
from accounts.models import RecruiterProfile, Task, ClientProfile, CandidateProfile, User
from jobs.models import Job
from kirismor import settings
from news.models import News
from django.utils import translation
from accounts.utils import send_verification_email
from django.conf import settings
from django.utils.translation import gettext as _

"""
Imports explanation:

1. from django.contrib import messages
   - messages: Framework Django umożliwiający dodawanie wiadomości informacyjnych do sesji.

2. from django.contrib.auth import logout, login, update_session_auth_hash
   - logout: Funkcja Django umożliwiająca wylogowanie użytkownika.
   - login: Funkcja Django umożliwiająca zalogowanie użytkownika.
   - update_session_auth_hash: Funkcja Django służąca do aktualizacji sesji po zmianie hasła, aby zapobiec wylogowaniu użytkownika.

3. from django.contrib.auth.decorators import login_required
   - login_required: Dekorator sprawdzający, czy użytkownik jest zalogowany przed udostępnieniem określonego widoku.

4. from django.contrib.auth.mixins import LoginRequiredMixin
   - LoginRequiredMixin: Mixin używany w klasach opartych na widokach, wymagający zalogowania użytkownika do dostępu do widoku.

5. from django.core.serializers import serialize
   - serialize: Funkcja służąca do serializacji danych modelu do formatu JSON.

6. from django.db.models import Q
   - Q: Narzędzie do tworzenia złożonych zapytań SQL za pomocą operatorów OR i NOT.

7. from django.http import Http404, JsonResponse, HttpResponseRedirect
   - Http404: Wyjątek rzucany, gdy żądany zasób nie istnieje.
   - JsonResponse: Funkcja Django do zwracania odpowiedzi w formacie JSON.
   - HttpResponseRedirect: Funkcja Django do przekierowywania na inny adres URL.

8. from django.shortcuts import redirect, render, get_object_or_404
   - redirect: Funkcja do przekierowywania na inny adres URL.
   - render: Funkcja do renderowania szablonów HTML.
   - get_object_or_404: Funkcja do pobierania obiektów z bazy danych, rzucająca wyjątek 404, jeśli obiekt nie istnieje.

9. from django.urls import reverse_lazy
   - reverse_lazy: Funkcja do odwracania adresów URL, używana do generowania adresów URL na podstawie nazw wzorców.

10. from django.views.generic import TemplateView, ListView
    - TemplateView: Klasa bazowa dla widoków generycznych, używana do wyświetlania prostych stron.
    - ListView: Klasa bazowa dla widoków generycznych, używana do wyświetlania listy elementów.

11. from accounts.forms import (
        RecruiterProfileForm, TaskForm, ClientProfileForm, 
        CandidateProfileForm, UserLoginForm, UserRegistrationForm, PasswordChangeForm
    )
    - RecruiterProfileForm: Formularz do tworzenia i edytowania profilu rekrutera.
    - TaskForm: Formularz do tworzenia i edytowania zadań.
    - ClientProfileForm: Formularz do tworzenia i edytowania profilu klienta.
    - CandidateProfileForm: Formularz do tworzenia i edytowania profilu kandydata.
    - UserLoginForm: Formularz do logowania użytkowników.
    - UserRegistrationForm: Formularz do rejestracji użytkowników.
    - PasswordChangeForm: Formularz do zmiany hasła użytkownika.

12. from accounts.models import RecruiterProfile, Task, ClientProfile, CandidateProfile, User
    - RecruiterProfile: Model danych dla profilu rekrutera.
    - Task: Model danych dla zadań.
    - ClientProfile: Model danych dla profilu klienta.
    - CandidateProfile: Model danych dla profilu kandydata.
    - User: Model danych dla użytkownika.

13. from jobs.models import Job
    - Job: Model danych dla ofert pracy.

14. from kirismor import settings
    - settings: Moduł ustawień projektu kirismor.

15. from news.models import News
    - News: Model danych dla aktualności i informacji.

16. from django.utils import translation
    - translation: Moduł Django do zarządzania tłumaczeniami.

17. from accounts.utils import send_verification_email
    - send_verification_email: Funkcja użytkowa do wysyłania emaili weryfikacyjnych.

18. from django.conf import settings
    - settings: Moduł ustawień Django.

19. from django.utils.translation import gettext as _
    - gettext as _: Funkcja Django do tłumaczenia tekstu, używana do internacjonalizacji.
"""

'---------------------------------------------------STRONA GŁÓWNA------------------------------------------------------'


class HomeView(TemplateView):
    """
    Widok strony głównej serwisu. Wyświetla główną stronę aplikacji.
    Używa szablonu 'home/base.html' do renderowania strony.
    """
    template_name = 'home/base.html'

    def get_context_data(self, **kwargs):
        """
        Przygotowuje i zwraca kontekst danych dla szablonu.
        W kontekście zwracane są oferty pracy, które mają status 'OPEN', co oznacza, że są aktualnie otwarte.

        Args:
            **kwargs: Parametry kontekstowe przekazywane do widoku.

        Returns:
            dict: Słownik z danymi kontekstowymi dla szablonu.
        """
        context = super().get_context_data(**kwargs)
        """
        Wywołanie metody get_context_data z klasy bazowej TemplateView.
        Używa super() do odwołania się do metody klasy rodzica.
        """
        context['jobs'] = Job.objects.filter(status=Job.JobStatus.OPEN)
        return context


class AboutView(TemplateView):
    """
    Widok strony 'O nas'. Służy do przedstawienia informacji o firmie lub organizacji.
    Używa szablonu 'home/about_us.html' do renderowania strony.
    """
    template_name = 'home/about_us.html'


class ContactView(TemplateView):
    """
    Widok strony kontaktowej. Umożliwia użytkownikom znajdowanie sposobów kontaktu z firmą lub organizacją.
    Używa szablonu 'home/contact.html' do renderowania strony.
    """
    template_name = 'home/contact.html'


'-----------------------------------------NASI KLIENCI I NASI REKRUTERZY-----------------------------------------------'


class PaginationMixin:
    """
    Mixin do paginacji. Umożliwia generowanie linków do paginacji na listach, takich jak lista użytkowników.
    """

    def generate_pagination_html(self, page_obj):
        """
        Generuje HTML dla linków paginacji. Tworzy linki do poprzedniej, aktualnych i następnej strony, jeśli istnieją.

        Args:
            page_obj (Page): Obiekt strony zawierający informacje o bieżącej stronie.

        Returns:
            str: HTML zawierający linki do paginacji.
        """
        paginator = page_obj.paginator
        pagination_html = ''
        if page_obj.has_previous():
            pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}">Previous</a>'
        for num in paginator.page_range:
            pagination_html += f'<a class="pagination-link" href="?page={num}">{num}</a>'
        if page_obj.has_next():
            pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}">Next</a>'
        return pagination_html


class RecruiterListView(PaginationMixin, ListView):
    """
    Widok listy rekruterów. Wyświetla stronę z listą rekruterów, z możliwością paginacji.
    Używa szablonu 'home/recruiters.html' i modelu RecruiterProfile.
    """
    model = RecruiterProfile
    template_name = 'home/recruiters.html'
    context_object_name = 'recruiters'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca uporządkowaną listę rekruterów po imieniu i nazwisku.

        Returns:
            QuerySet: Lista obiektów RecruiterProfile uporządkowanych po imieniu i nazwisku.
        """
        return RecruiterProfile.objects.order_by('first_name', 'last_name')

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane rekruterów w formacie JSON.

        Args:
            context (dict): Kontekst danych dla szablonu.
            **response_kwargs: Dodatkowe parametry odpowiedzi.

        Returns:
            HttpResponse: Odpowiedź zawierająca dane rekruterów i linki do paginacji w formacie JSON lub HTML.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            page_obj = context['page_obj']
            recruiters = serialize('json', page_obj.object_list)
            pagination_html = self.generate_pagination_html(page_obj)
            return JsonResponse({'recruiters': recruiters, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)
    # Wywołanie metody render_to_response z klasy bazowej ListView.
    # Używa super() do odwołania się do metody klasy rodzica.


class ClientListView(PaginationMixin, ListView):
    """
    Widok listy klientów. Wyświetla stronę z listą klientów, z możliwością paginacji.
    Używa szablonu 'home/client_list.html' i modelu ClientProfile.
    """
    model = ClientProfile
    template_name = 'home/client_list.html'
    context_object_name = 'clients'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca uporządkowaną listę klientów po nazwie firmy.

        Returns:
            QuerySet: Lista obiektów ClientProfile uporządkowanych po nazwie firmy.
        """
        return ClientProfile.objects.order_by('company_name')

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane klientów w formacie JSON.

        Args:
            context (dict): Kontekst danych dla szablonu.
            **response_kwargs: Dodatkowe parametry odpowiedzi.

        Returns:
            HttpResponse: Odpowiedź zawierająca dane klientów i linki do paginacji w formacie JSON lub HTML.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            page_obj = context['page_obj']
            clients = serialize('json', page_obj.object_list)
            pagination_html = self.generate_pagination_html(page_obj)
            return JsonResponse({'clients': clients, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)
    # 'Wywołanie metody render_to_response z klasy bazowej ListView.'
    # 'Używa super() do odwołania się do metody klasy rodzica.'


'-------------------Rejestracja, logowanie, tworzenie profilu, wylogowanie, potw.email, daszboard----------------------'


def register_user(request):
    """
    Obsługuje proces rejestracji użytkownika.

    Jeśli metoda żądania to POST:
        1. Przetwarza dane z formularza rejestracyjnego (UserRegistrationForm).
        2. Jeśli formularz jest prawidłowy:
            - Tworzy nowego użytkownika, ale ustawia jego status jako nieaktywny do momentu weryfikacji email.
            - Zapisuje nowego użytkownika w bazie danych.
            - Przechowuje ID nowego użytkownika w sesji.
            - Przekierowuje użytkownika na stronę tworzenia profilu.

    Jeśli metoda żądania to GET:
        - Wyświetla pusty formularz rejestracyjny.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną rejestracji lub przekierowanie do strony tworzenia profilu.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = False  # Ustawia użytkownika jako nieaktywnego do momentu weryfikacji email.
            new_user.save()
            request.session['user_id'] = new_user.id  # Przechowuje ID użytkownika w sesji.
            return redirect('accounts:create_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def create_profile(request):
    """
    Obsługuje proces tworzenia profilu użytkownika.

    - Pobiera ID użytkownika z sesji. Jeśli ID nie istnieje, przekierowuje na stronę rejestracji.
    - Pobiera użytkownika z bazy danych na podstawie ID.
    - Wybiera odpowiedni formularz tworzenia profilu w zależności od roli użytkownika.
    - Jeśli metoda żądania to POST:
        1. Przetwarza dane z formularza tworzenia profilu.
        2. Jeśli formularz jest prawidłowy:
            - Tworzy i zapisuje nowy profil użytkownika.
            - Wysyła email weryfikacyjny.
            - Usuwa ID użytkownika z sesji.
            - Przekierowuje na stronę informującą o zakończeniu rejestracji.
    - Jeśli metoda żądania to GET:
        - Wyświetla pusty formularz tworzenia profilu.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną tworzenia profilu lub przekierowanie do innej strony.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('accounts:register')

    user = get_object_or_404(User, id=user_id)

    form_classes = {'candidate': CandidateProfileForm, 'client': ClientProfileForm}
    form_class = form_classes.get(user.role)
    if not form_class:
        raise Http404("Ten typ roli nie jest dozwolony do tworzenia profilu.")

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            send_verification_email(user)  # Wysyła email weryfikacyjny.
            request.session.pop('user_id', None)  # Usuwa ID użytkownika z sesji.
            return redirect('accounts:registration_complete')
    else:
        form = form_class()

    return render(request, 'registration/create_profile.html', {'form': form})


def verify_email_view(request, token):
    """
    Obsługuje proces weryfikacji email.

    - Pobiera użytkownika na podstawie tokena weryfikacyjnego.
    - Ustawia użytkownika jako zweryfikowanego i aktywnego.
    - Usuwa token weryfikacyjny i zapisuje zmiany w bazie danych.
    - Przekierowuje na stronę potwierdzenia weryfikacji.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        token (str): Token weryfikacyjny.

    Returns:
        HttpResponse: Przekierowanie do strony potwierdzenia weryfikacji.
    """
    user = get_object_or_404(User, verification_token=token)
    user.is_verified = True
    user.verification_token = None
    user.is_active = True  # Aktywuje użytkownika po weryfikacji email.
    user.save()
    return redirect('accounts:verified')


def registration_complete_view(request):
    """
    Wyświetla stronę informującą o zakończeniu procesu rejestracji.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną informującą o zakończeniu rejestracji.
    """
    return render(request, 'registration/registration_complete.html')


def verified_view(request):
    """
    Wyświetla stronę informującą o pomyślnej weryfikacji email.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną informującą o pomyślnej weryfikacji email.
    """
    return render(request, 'registration/verified.html')


def login_view(request):
    """
    Obsługuje proces logowania użytkownika.

    Jeśli metoda żądania to POST:
        1. Przetwarza dane z formularza logowania (UserLoginForm).
        2. Jeśli formularz jest prawidłowy:
            - Loguje użytkownika.
            - Przechowuje rolę użytkownika w sesji.
            - Przekierowuje użytkownika do panelu kontrolnego.
        3. Jeśli formularz jest nieprawidłowy:
            - Wyświetla formularz logowania z komunikatem o błędzie.

    Jeśli metoda żądania to GET:
        - Wyświetla pusty formularz logowania.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną logowania lub przekierowanie do panelu kontrolnego.
    """
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['role'] = user.role
            return redirect(reverse_lazy('accounts:dashboard'))
        else:
            return render(request, 'registration/login.html',
                          {'form': form, 'error': 'Nieprawidłowa nazwa użytkownika lub hasło'})
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Obsługuje proces wylogowania użytkownika.

    Jeśli metoda żądania to POST:
        - Wylogowuje użytkownika.
        - Przekierowuje użytkownika na stronę główną.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Przekierowanie do strony głównej lub renderowana strona potwierdzenia wylogowania.
    """
    if request.method == 'POST':
        logout(request)
        return redirect(reverse_lazy('home'))
    return render(request, 'registration/logout_confirmation.html', {'user': request.user})


@login_required
def dashboard_view(request):
    """
    Wyświetla panel kontrolny użytkownika.

    - Pobiera rolę użytkownika z sesji.
    - Pobiera listę wiadomości odpowiednich dla roli użytkownika, posortowanych według daty dodania (od najnowszych).
    - Renderuje stronę panelu kontrolnego z rolą użytkownika i listą wiadomości.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną panelu kontrolnego.
    """
    role = request.user.role
    news_list = News.objects.filter(role=role).order_by('-date_posted')
    return render(request, 'dashboard/dashboard.html', {'role': role, 'news_list': news_list})


'------------------------------------------SZCZEGÓŁY PROFILU, ZMIANA DANYCH-------------------------------------------'


@login_required
def profile_detail_view(request):
    """
    Wyświetla szczegółowe informacje o profilu użytkownika.

    - Widok dostępny tylko dla zalogowanych użytkowników.
    - Wybiera model profilu na podstawie roli użytkownika i próbuje pobrać odpowiedni profil z bazy danych.
    - W przypadku braku profilu przekierowuje do strony tworzenia profilu.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną szczegółów profilu lub przekierowanie do strony tworzenia profilu.
    """
    user = request.user
    profile_model = {
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)
    if not profile_model:
        raise Http404("Profil nie został znaleziony dla bieżącego użytkownika.")

    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        return redirect(reverse_lazy('accounts:create_profile'))

    context = {
        'profile': profile,
        'profile_type': user.role
    }
    return render(request, 'profiles/universal_profile_detail.html', context)


@login_required
def profile_edit_view(request):
    """
    Umożliwia edycję istniejącego profilu użytkownika.

    - Widok dostępny tylko dla zalogowanych użytkowników.
    - Wybiera model i formularz edycji na podstawie roli użytkownika.
    - W przypadku braku modelu zgłasza błąd 404.
    - Obsługuje zarówno metodę GET, jak i POST, pozwalając na wyświetlenie formularza i jego przetwarzanie.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną edycji profilu lub przekierowanie do panelu kontrolnego.
    """
    user = request.user
    profile_model = {
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)
    if not profile_model:
        raise Http404("Profil nie został znaleziony dla bieżącego użytkownika.")

    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        return redirect(reverse_lazy('accounts:create_profile'))

    form_class = {
        'candidate': CandidateProfileForm,
        'client': ClientProfileForm,
        'recruiter': RecruiterProfileForm
    }.get(user.role)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('accounts:dashboard'))
    else:
        form = form_class(instance=profile)

    return render(request, 'profiles/universal_profile_edit.html', {'form': form})


'-----------------------------------------ZADANIA REKRUTERA-----------------------------------------------------------'


class TaskListView(LoginRequiredMixin, ListView):
    """
    Klasa odpowiadająca za wyświetlanie listy zadań stworzonych przez zalogowanego użytkownika.
    Umożliwia paginację oraz filtrowanie zadań na podstawie zapytań przekazywanych w URL.

    Atrybuty:
        model (Task): Model, którego dotyczy ten widok.
        template_name (str): Nazwa szablonu używanego do renderowania strony.
        context_object_name (str): Nazwa używana do przekazywania listy zadań do szablonu.
        paginate_by (int): Liczba elementów na stronie.
    """
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca przefiltrowany zbiór zadań na podstawie zapytania użytkownika.
        Umożliwia wyszukiwanie zadań po tytule lub opisie.

        Returns:
            QuerySet: Przefiltrowany zbiór zadań.
        """
        search_query = self.request.GET.get('q', '')
        queryset = Task.objects.filter(created_by=self.request.user).order_by('due_date')  # Пример сортировки
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        return queryset

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane w formacie JSON, w tym listę zadań oraz linki do paginacji.

        Args:
            context (dict): Kontekst danych przekazywanych do szablonu.
            **response_kwargs: Dodatkowe argumenty odpowiedzi.

        Returns:
            JsonResponse lub HttpResponse: Odpowiedź zawierająca dane zadań w formacie JSON lub renderowana strona HTML.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tasks = [{
                'id': task.id,
                'title': task.title,
                'description': task.description[:30],
                'priority': task.get_priority_display(),
                'status': task.get_status_display(),
                'due_date': task.due_date.strftime('%d %b %Y') if task.due_date else ''
            } for task in context['tasks']]

            pagination_html = ''
            page_obj = context['page_obj']
            paginator = context['paginator']

            # Dodanie linku do poprzedniej strony, jeśli istnieje
            if page_obj.has_previous():
                pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}">Previous</a>'

            # Dodanie linków do wszystkich stron
            for num in paginator.page_range:
                pagination_html += f'<a class="pagination-link" href="?page={num}">{num}</a>'

            # Dodanie linku do następnej strony, jeśli istnieje
            if page_obj.has_next():
                pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}">Next</a>'

            return JsonResponse({'tasks': tasks, 'pagination': pagination_html})

        return super().render_to_response(context, **response_kwargs)


@login_required
def task_create_view(request):
    """
    Obsługuje tworzenie nowego zadania przez zalogowanego użytkownika.

    - Formularz do tworzenia zadania jest przetwarzany.
    - Po pomyślnym utworzeniu zadania użytkownik jest przekierowywany do listy zadań.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną formularza tworzenia zadania lub przekierowanie do listy zadań.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect(reverse_lazy('accounts:task_list'))
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_update_view(request, task_id):
    """
    Obsługuje proces aktualizacji istniejącego zadania, sprawdzając czy zadanie należy do zalogowanego użytkownika.

    - Po pomyślnej walidacji formularza zmiany są zapisywane i użytkownik jest przekierowywany do listy zadań.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        task_id (int): ID zadania do aktualizacji.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną formularza edycji zadania lub przekierowanie do listy zadań.
    """
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('accounts:task_list'))
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_delete_view(request, task_id):
    """
    Obsługuje proces usuwania zadania.

    - Usunięcie jest możliwe tylko jeśli zadanie należy do zalogowanego użytkownika.
    - Po usunięciu użytkownik jest przekierowywany do listy zadań.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        task_id (int): ID zadania do usunięcia.

    Returns:
        HttpResponse: Przekierowanie do listy zadań lub renderowana strona potwierdzenia usunięcia zadania.
    """
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect(reverse_lazy('accounts:task_list'))
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_detail_view(request, pk):
    """
    Wyświetla szczegółowe informacje o konkretnym zadaniu.

    - Dostępne tylko dla zalogowanych użytkowników i tylko dla zadań, które do nich należą.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        pk (int): ID zadania do wyświetlenia.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną szczegółów zadania.
    """
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


'--------------------------------------------ZMIANA JEZYKOW-----------------------------------------------------------'


def set_language(request, language):
    """
    Ustawia język aplikacji na podstawie żądania użytkownika.

    - Sprawdza, czy żądany język jest dostępny w ustawieniach.
    - Jeśli język jest dostępny:
        - Aktywuje wybrany język dla bieżącej sesji użytkownika.
        - Ustawia język w sesji użytkownika za pomocą klucza 'django_language'.
        - Ustawia ciasteczko języka dla bieżącej i przyszłych sesji użytkownika.
    - Jeśli język nie jest dostępny:
        - Przekierowuje użytkownika na stronę główną lub stronę referencyjną bez zmiany języka.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        language (str): Kod języka do ustawienia.

    Returns:
        HttpResponse: Przekierowanie do strony referencyjnej lub strony głównej.
    """
    if language in dict(settings.LANGUAGES):
        translation.activate(language)
        request.session['django_language'] = language  # Ustawia język w sesji
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))


'-------------------------------------------ZMIANA HASLA--------------------------------------------------------------'


@login_required
def change_password(request):
    """
    Umożliwia zalogowanemu użytkownikowi zmianę hasła.

    - Jeśli metoda żądania to POST:
        - Przetwarza dane z formularza zmiany hasła.
        - Jeśli formularz jest prawidłowy:
            - Ustawia nowe hasło dla użytkownika.
            - Zapisuje zmiany w bazie danych.
            - Aktualizuje sesję użytkownika, aby uniknąć wylogowania.
            - Wyświetla komunikat o pomyślnej zmianie hasła.
            - Przekierowuje użytkownika do strony szczegółów profilu.
        - Jeśli formularz jest nieprawidłowy:
            - Wyświetla komunikat o błędzie.
    - Jeśli metoda żądania to GET:
        - Wyświetla pusty formularz zmiany hasła.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Odpowiedź HTTP z renderowaną stroną formularza zmiany hasła lub przekierowanie do strony profilu.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)  # Ważne! Utrzymuje sesję użytkownika po zmianie hasła.
            messages.success(request, _('Twoje hasło zostało pomyślnie zaktualizowane!'))
            return redirect('accounts:profile_detail')  # Przekierowuje na stronę profilu
        else:
            messages.error(request, _('Proszę poprawić błąd poniżej.'))
    else:
        form = PasswordChangeForm()
    return render(request, 'registration/change_password.html', {'form': form})
