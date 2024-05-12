from django.contrib.auth import logout, \
    login  # Funkcje Django umożliwiające odpowiednio wylogowanie i zalogowanie użytkownika.
from django.contrib.auth.decorators import \
    login_required  # Dekorator sprawdzający, czy użytkownik jest zalogowany przed udostępnieniem określonego widoku.
from django.contrib.auth.mixins import \
    LoginRequiredMixin  # Mixin używany w klasach opartych na widokach, wymagający zalogowania użytkownika do dostępu do widoku.
from django.core.serializers import serialize  # Funkcja służąca do serializacji danych modelu do formatu JSON.
from django.db.models import Q  # Narzędzie do tworzenia złożonych zapytań SQL za pomocą operatorów OR i NOT.
from django.http import Http404, \
    JsonResponse  # Http404 rzuca wyjątek, gdy żądany zasób nie istnieje; JsonResponse służy do zwracania odpowiedzi JSON.
from django.shortcuts import redirect, render, \
    get_object_or_404  # Zestaw pomocniczych funkcji do przekierowań, renderowania szablonów i pobierania obiektów z DB z obsługą wyjątków 404.
from django.urls import reverse_lazy, \
    reverse  # Funkcje do odwracania adresów URL, używane do generowania adresów URL na podstawie nazw wzorców.
from django.views.generic import TemplateView, \
    ListView  # Klasa bazowa dla widoków generycznych, TemplateView dla prostych stron, ListView dla list elementów.
from accounts.forms import RecruiterProfileForm, TaskForm, ClientProfileForm, CandidateProfileForm, UserLoginForm, \
    UserRegistrationForm  # Import formularzy używanych do obsługi danych użytkowników i profilów.
from accounts.models import RecruiterProfile, Task, ClientProfile, \
    CandidateProfile  # Modele danych dla różnych typów profilów użytkowników.
from jobs.models import Job  # Model danych dla ofert pracy.
from news.models import News  # Model dla aktualności i informacji.


#---------------------------------------------------STRONA GŁÓWNA------------------------------------------------------

class HomeView(TemplateView):
    """
    Widok strony głównej serwisu. Wyświetla główną stronę aplikacji.
    Używa szablonu 'home/base.html' do renderowania strony.
    """
    template_name = 'polish/home/base.html'

    def get_context_data(self, **kwargs):
        """
        Przygotowuje i zwraca kontekst danych dla szablonu.
        W kontekście zwracane są oferty pracy, które mają status 'OPEN', co oznacza, że są aktualnie otwarte.
        """
        context = super().get_context_data(**kwargs)
        context['jobs'] = Job.objects.filter(status=Job.JobStatus.OPEN)
        return context


class AboutView(TemplateView):
    """
    Widok strony 'O nas'. Służy do przedstawienia informacji o firmie lub organizacji.
    Używa szablonu 'home/about_us.html' do renderowania strony.
    """
    template_name = 'polish/home/about_us.html'


class ContactView(TemplateView):
    """
    Widok strony kontaktowej. Umożliwia użytkownikom znajdowanie sposobów kontaktu z firmą lub organizacją.
    Używa szablonu 'home/contact.html' do renderowania strony.
    """
    template_name = 'polish/home/contact.html'


#-----------------------------------------NASI KLIENCI  I NASI REKRUTERZY-----------------------------------------------

class PaginationMixin:
    """
    Mixin do paginacji. Umożliwia generowanie linków do paginacji na listach, takich jak lista użytkowników.
    """

    def generate_pagination_html(self, page_obj):
        """
        Generuje HTML dla linków paginacji. Tworzy linki do poprzedniej, aktualnych i następnej strony, jeśli istnieją.
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
    template_name = 'polish/home/recruiters.html'
    context_object_name = 'recruiters'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca uporządkowaną listę rekruterów po imieniu i nazwisku.
        """
        return RecruiterProfile.objects.order_by('first_name', 'last_name')

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane rekruterów w formacie JSON.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            page_obj = context['page_obj']
            recruiters = serialize('json', page_obj.object_list)
            pagination_html = self.generate_pagination_html(page_obj)
            return JsonResponse({'recruiters': recruiters, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)


class ClientListView(PaginationMixin, ListView):
    """
    Widok listy klientów. Wyświetla stronę z listą klientów, z możliwością paginacji.
    Używa szablonu 'home/client_list.html' i modelu ClientProfile.
    """
    model = ClientProfile
    template_name = 'polish/home/client_list.html'
    context_object_name = 'clients'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca uporządkowaną listę klientów po nazwie firmy.
        """
        return ClientProfile.objects.order_by('company_name')

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane klientów w formacie JSON.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            page_obj = context['page_obj']
            clients = serialize('json', page_obj.object_list)
            pagination_html = self.generate_pagination_html(page_obj)
            return JsonResponse({'clients': clients, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)


# Rejestracja, logowanie, tworzenie profilu, wylogowanie

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)  # Automatyczne logowanie po rejestracji
            return redirect(reverse_lazy('accounts:create_profile'))
    else:
        form = UserRegistrationForm()
    return render(request, 'polish/registration/register.html', {'form': form})


def login_view(request):
    """
    Obsługuje proces logowania użytkownika. Jeśli metoda żądania to POST, przetwarza formularz logowania.
    Po pomyślnej walidacji formularza loguje użytkownika i przekierowuje do panelu kontrolnego.
    W przypadku nieudanej walidacji wyświetla formularz logowania wraz z komunikatem o błędzie.
    W przypadku metody GET wyświetla pusty formularz logowania.
    """
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['role'] = user.role
            return redirect(reverse_lazy('accounts:dashboard'))
        else:
            return render(request, 'polish/registration/login.html',
                          {'form': form, 'error': 'Nieprawidłowa nazwa użytkownika lub hasło'})
    else:
        form = UserLoginForm()
    return render(request, 'polish/registration/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Obsługuje proces wylogowania. Jeśli metoda żądania to POST, wylogowuje użytkownika i przekierowuje na stronę główną.
    """
    if request.method == 'POST':
        logout(request)
        return redirect(reverse_lazy('home'))
    return render(request, 'polish/registration/logout_confirmation.html', {'user': request.user})


@login_required
def create_profile(request):
    """
    Obsługuje tworzenie profilu użytkownika dla zalogowanych użytkowników.
    Dostępne tylko po zalogowaniu. Użytkownik może utworzyć profil w zależności od swojej roli.
    W przypadku braku formularza dla danej roli, zgłaszany jest błąd 404.
    """
    form_classes = {'candidate': CandidateProfileForm, 'client': ClientProfileForm}
    form_class = form_classes.get(request.user.role)
    if not form_class:
        raise Http404("Ten typ roli nie jest dozwolony do tworzenia profilu.")
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('accounts:login')
    else:
        form = form_class()
    return render(request, 'polish/registration/create_profile.html', {'form': form})


def dashboard_view(request):
    """
    Wyświetla panel kontrolny dla zalogowanych użytkowników.
    Panel zawiera specyficzne dla roli użytkownika informacje, takie jak aktualności związane z rolą.
    """
    role = request.user.role
    news_list = News.objects.filter(role=role).order_by('-date_posted')
    return render(request, 'polish/dashboard/dashboard.html', {'role': role, 'news_list': news_list})


#------------------------------------------SZCZEGÓŁY PROFILU, ZMIANA DANYCH-------------------------------------------

@login_required
def profile_detail_view(request):
    """
    Wyświetla szczegółowe informacje o profilu użytkownika. Dostępny tylko dla zalogowanych użytkowników.
    Wybiera model profilu na podstawie roli użytkownika i próbuje pobrać odpowiedni profil z bazy danych.
    W przypadku braku profilu przekierowuje do strony tworzenia profilu.
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
    return render(request, 'polish/profiles/universal_profile_detail.html', context)


@login_required
def profile_edit_view(request):
    """
    Umożliwia edycję istniejącego profilu użytkownika. Dostępny tylko dla zalogowanych użytkowników.
    Wybiera model i formularz edycji na podstawie roli użytkownika. W przypadku braku modelu, zgłasza błąd 404.
    Obsługuje zarówno metodę GET, jak i POST, pozwalając na wyświetlenie formularza i jego przetwarzanie.
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

    return render(request, 'polish/profiles/universal_profile_edit.html', {'form': form})


#------------------------------------------ZADANIA REKRUTERA-----------------------------------------------------------

class TaskListView(LoginRequiredMixin, ListView):
    """
    Klasa odpowiadająca za wyświetlanie listy zadań stworzonych przez zalogowanego użytkownika.
    Umożliwia paginację oraz filtrowanie zadań na podstawie zapytań przekazywanych w URL.
    """
    model = Task
    template_name = 'polish/tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        """
        Zwraca zbiór zadań filtrowanych na podstawie zapytania użytkownika w pasku adresu.
        Umożliwia wyszukiwanie zadań po tytule lub opisie.
        """
        search_query = self.request.GET.get('q', '')
        queryset = Task.objects.filter(created_by=self.request.user)
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        return queryset

    def render_to_response(self, context, **response_kwargs):
        """
        Obsługuje odpowiedzi AJAX, zwracając dane w formacie JSON, w tym listę zadań oraz linki do paginacji.
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
            if page_obj.has_previous():
                pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}">Previous</a>'
            for num in paginator.page_range:
                pagination_html += f'<a class="pagination-link" href="?page={num}">{num}</a>'
            if page_obj.has_next():
                pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}">Next</a>'
            return JsonResponse({'tasks': tasks, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)


@login_required
def task_create_view(request):
    """
    Obsługuje tworzenie nowego zadania przez zalogowanego użytkownika.
    Formularz do tworzenia zadania jest przetwarzany. Po pomyślnym utworzeniu zadania użytkownik jest przekierowywany do listy zadań.
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
    return render(request, 'polish/tasks/task_form.html', {'form': form})


@login_required
def task_update_view(request, task_id):
    """
    Obsługuje proces aktualizacji istniejącego zadania, sprawdzając czy zadanie należy do zalogowanego użytkownika.
    Po pomyślnej walidacji formularza zmiany są zapisywane i użytkownik jest przekierowywany do listy zadań.
    """
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('accounts:task_list'))
    else:
        form = TaskForm(instance=task)
    return render(request, 'polish/tasks/task_form.html', {'form': form})


@login_required
def task_delete_view(request, task_id):
    """
    Obsługuje proces usuwania zadania. Usunięcie jest możliwe tylko jeśli zadanie należy do zalogowanego użytkownika.
    Po usunięciu użytkownik jest przekierowywany do listy zadań.
    """
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect(reverse_lazy('accounts:task_list'))
    return render(request, 'polish/tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_detail_view(request, pk):
    """
    Wyświetla szczegółowe informacje o konkretnym zadaniu. Dostępne tylko dla zalogowanych użytkowników i tylko dla zadań, które do nich należą.
    """
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'polish/tasks/task_detail.html', {'task': task})
