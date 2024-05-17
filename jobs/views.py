from django.conf.urls.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.html import escape
from django.views.generic import ListView
from .models import Job, Application, GuestFeedback, Like, Favorite, TempGuestFeedback
from .forms import JobForm, ApplicationForm, GuestFeedbackForm
from django.contrib import messages
from jobs.utils import send_verification_email
from django.utils.translation import gettext as _

"""
Importy:

1. from django.conf.urls.static import static
   - Importuje funkcję `static`, która jest używana do obsługi plików statycznych w trybie deweloperskim.

2. from django.contrib.auth.mixins import LoginRequiredMixin
   - Importuje mixin `LoginRequiredMixin`, który zapewnia, że widoki oparte na klasach są dostępne tylko dla zalogowanych użytkowników.

3. from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
   - Importuje klasy `Paginator`, `PageNotAnInteger`, `EmptyPage`, które są używane do paginacji wyników w widokach.

4. from django.db.models import Q
   - Importuje klasę `Q`, która umożliwia tworzenie złożonych zapytań bazodanowych z operatorem OR i NOT.

5. from django.http import HttpResponseForbidden, JsonResponse
   - Importuje `HttpResponseForbidden` do zwracania odpowiedzi HTTP 403 (zabronione) oraz `JsonResponse` do zwracania odpowiedzi w formacie JSON.

6. from django.shortcuts import render, redirect, get_object_or_404
   - Importuje funkcje `render`, `redirect`, `get_object_or_404`, które są używane do renderowania szablonów, przekierowywania i pobierania obiektów z bazy danych z obsługą błędów 404.

7. from django.contrib.auth.decorators import login_required
   - Importuje dekorator `login_required`, który zabezpiecza widoki, aby były dostępne tylko dla zalogowanych użytkowników.

8. from django.urls import reverse
   - Importuje funkcję `reverse`, która jest używana do generowania URL na podstawie nazw wzorców.

9. from django.utils.html import escape
   - Importuje funkcję `escape`, która zabezpiecza tekst przed wstrzyknięciem złośliwego kodu HTML.

10. from django.views.generic import ListView
    - Importuje `ListView`, klasę widoku generycznego służącą do wyświetlania listy obiektów.

11. from .models import Job, Application, GuestFeedback, Like, Favorite, TempGuestFeedback
    - Importuje modele `Job`, `Application`, `GuestFeedback`, `Like`, `Favorite`, `TempGuestFeedback` z bieżącego modułu models.

12. from .forms import JobForm, ApplicationForm, GuestFeedbackForm
    - Importuje formularze `JobForm`, `ApplicationForm`, `GuestFeedbackForm` z bieżącego modułu forms.

13. from django.contrib import messages
    - Importuje moduł `messages`, który umożliwia dodawanie komunikatów dla użytkowników.

14. from jobs.utils import send_verification_email
    - Importuje funkcję `send_verification_email` z modułu `jobs.utils`, która jest używana do wysyłania e-maili weryfikacyjnych.

15. from django.utils.translation import gettext as _
    - Importuje funkcję `gettext` jako `_`, która jest używana do tłumaczenia tekstów w aplikacji.
"""


class JobListView(LoginRequiredMixin, ListView):
    """
    Widok listy ofert pracy dla zalogowanych użytkowników.

    Atrybuty klasy:
        - model: Model Job, z którego dane będą pobierane.
        - template_name: Nazwa szablonu używanego do renderowania widoku.
        - context_object_name: Nazwa obiektu kontekstu, który będzie dostępny w szablonie.
        - paginate_by: Liczba elementów na stronę.
    """
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        """
        Pobiera zestaw danych do wyświetlenia w widoku.

        Filtruje oferty pracy na podstawie statusu (tylko otwarte oferty) i opcjonalnie na podstawie zapytania
        wyszukiwania przekazanego w parametrze 'q'.

        Zwraca:
            QuerySet: Posortowany zestaw danych ofert pracy.
        """
        search_query = escape(self.request.GET.get('q', '')[:100])
        queryset = Job.objects.filter(status=Job.JobStatus.OPEN)
        if search_query:
            queryset = queryset.filter(
                Q(salary__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Przygotowuje dane kontekstu dla szablonu.

        Dodaje do kontekstu informacje o polubionych i ulubionych ofertach pracy użytkownika oraz zakres paginacji.

        Zwraca:
            dict: Dane kontekstu dla szablonu.
        """
        context = super().get_context_data(**kwargs)
        context['liked_jobs'] = Like.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        context['favorited_jobs'] = Favorite.objects.filter(user=self.request.user).values_list('job_id', flat=True)

        page_obj = context['page_obj']
        paginator = context['paginator']
        range_size = 2
        start_page = max(1, page_obj.number - range_size)
        end_page = min(paginator.num_pages, page_obj.number + range_size)
        context['page_range'] = range(start_page, end_page + 1)
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Renderuje odpowiedź HTTP.

        Jeśli w parametrze zapytania 'json' przekazano wartość 'true', zwraca dane w formacie JSON, w przeciwnym razie
        renderuje szablon HTML.

        Zwraca:
            HttpResponse: Odpowiedź HTTP.
        """
        if self.request.GET.get('json', '').lower() == 'true':
            jobs = [
                {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:100],
                    'salary': job.salary
                }
                for job in context['jobs']
            ]
            page_obj = context['page_obj']
            pagination_html = self.generate_pagination_html(page_obj, context['page_range'])
            return JsonResponse({'jobs': jobs, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)

    def generate_pagination_html(self, page_obj, page_range):
        """
        Generuje HTML dla paginacji.

        Zwraca:
            str: HTML dla paginacji.
        """
        pagination_html = ''
        query = escape(self.request.GET.get('q', ''))
        if page_obj.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&q={query}">Previous</a></li>'
        for num in page_range:
            if num == page_obj.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&q={query}">{num}</a></li>'
        if page_obj.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&q={query}">Next</a></li>'
        return pagination_html


class PublicJobListView(ListView):
    """
    Widok publicznej listy ofert pracy.

    Atrybuty klasy:
        - model: Model Job, z którego dane będą pobierane.
        - template_name: Nazwa szablonu używanego do renderowania widoku.
        - context_object_name: Nazwa obiektu kontekstu, który będzie dostępny w szablonie.
        - paginate_by: Liczba elementów na stronę.
    """
    model = Job
    template_name = 'home/public_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 7

    def get_queryset(self):
        """
        Pobiera zestaw danych do wyświetlenia w widoku.

        Filtruje oferty pracy na podstawie statusu (tylko otwarte oferty) i opcjonalnie na podstawie zapytania
        wyszukiwania przekazanego w parametrze 'q'.

        Zwraca:
            QuerySet: Posortowany zestaw danych ofert pracy.
        """
        search_query = escape(self.request.GET.get('q', '')[:100])
        queryset = Job.objects.filter(status=Job.JobStatus.OPEN)
        if search_query:
            queryset = queryset.filter(
                Q(salary__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Przygotowuje dane kontekstu dla szablonu.

        Dodaje do kontekstu zakres paginacji.

        Zwraca:
            dict: Dane kontekstu dla szablonu.
        """
        context = super().get_context_data(**kwargs)
        page_obj = context['page_obj']
        paginator = context['paginator']

        # Рассчитаем диапазон страниц вокруг текущей страницы
        range_size = 2
        start_page = max(1, page_obj.number - range_size)
        end_page = min(paginator.num_pages, page_obj.number + range_size)

        context['page_range'] = range(start_page, end_page + 1)
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Renderuje odpowiedź HTTP.

        Jeśli w parametrze zapytania 'json' przekazano wartość 'true', zwraca dane w formacie JSON, w przeciwnym razie
        renderuje szablon HTML.

        Zwraca:
            HttpResponse: Odpowiedź HTTP.
        """
        if self.request.GET.get('json', '').lower() == 'true':
            jobs = [
                {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:100],
                    'salary': job.salary
                }
                for job in context['jobs']
            ]
            page_obj = context['page_obj']
            pagination_html = self.generate_pagination_html(page_obj, context['page_range'])
            return JsonResponse({'jobs': jobs, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)

    def generate_pagination_html(self, page_obj, page_range):
        """
        Generuje HTML dla paginacji.

        Zwraca:
            str: HTML dla paginacji.
        """
        pagination_html = ''
        query = escape(self.request.GET.get('q', ''))
        if page_obj.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&q={query}">Previous</a></li>'
        for num in page_range:
            if num == page_obj.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&q={query}">{num}</a></li>'
        if page_obj.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&q={query}">Next</a></li>'
        return pagination_html


@login_required
def common_create_job_view(request):
    """
    Widok do tworzenia nowych ofert pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Jeśli metoda żądania to POST, przetwarza dane formularza.
    - Jeśli formularz jest poprawny, zapisuje nową ofertę pracy z przypisaniem zalogowanego użytkownika jako rekrutera.
    - Po zapisaniu nowej oferty pracy przekierowuje użytkownika na stronę szczegółów oferty pracy.
    - Jeśli metoda żądania to GET, wyświetla pusty formularz do tworzenia nowej oferty pracy.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z formularzem tworzenia oferty pracy lub przekierowanie po zapisaniu oferty.
    """
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)  # Tworzy obiekt Job, ale nie zapisuje go jeszcze w bazie danych
            job.recruiter = request.user  # Przypisuje zalogowanego użytkownika jako rekrutera
            job.save()  # Zapisuje obiekt Job w bazie danych
            return redirect('jobs:job_detail', job_id=job.pk)  # Przekierowuje na stronę szczegółów oferty pracy
    else:
        form = JobForm()  # Tworzy pusty formularz
    return render(request, 'jobs/create_job.html', {'form': form})  # Renderuje stronę HTML z formularzem


@login_required
def common_job_detail_view(request, job_id):
    """
    Widok szczegółów oferty pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id).
    - Przekazuje dane oferty pracy, rolę użytkownika i bieżącego użytkownika do szablonu.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML ze szczegółami oferty pracy.
    """
    job = get_object_or_404(Job, pk=job_id)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje
    user_role = request.user.role  # Pobiera rolę zalogowanego użytkownika

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_role': user_role,
        'current_user': request.user,  # Przekazuje bieżącego użytkownika do szablonu
    })


@login_required
def application_list_view(request):
    """
    Widok listy aplikacji na oferty pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera zapytanie wyszukiwania z parametrów URL.
    - Filtruje aplikacje na oferty pracy na podstawie zalogowanego użytkownika i zapytania wyszukiwania.
    - Przekazuje przefiltrowane aplikacje, rolę użytkownika i zapytanie wyszukiwania do szablonu.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z listą aplikacji na oferty pracy.
    """
    search_query = request.GET.get('q', '')  # Pobiera zapytanie wyszukiwania
    user_role = request.user.role  # Pobiera rolę zalogowanego użytkownika

    # Filtruje aplikacje na podstawie zapytania wyszukiwania i statusu oferty pracy
    if search_query:
        applications = Application.objects.filter(
            applicant=request.user,
            job__title__icontains=search_query,
            job__status=Job.JobStatus.OPEN  # Filtruje tylko otwarte oferty pracy
        ).select_related('job')
    else:
        applications = Application.objects.filter(
            applicant=request.user,
            job__status=Job.JobStatus.OPEN  # Filtruje tylko otwarte oferty pracy
        ).select_related('job')

    context = {
        'applications': applications,
        'user_role': user_role,
        'search_query': search_query  # Przekazuje zapytanie wyszukiwania do kontekstu
    }
    return render(request, 'jobs/application_list.html', context)  # Renderuje stronę HTML z listą aplikacji


@login_required
def create_application_view(request, job_id):
    """
    Widok do tworzenia nowych aplikacji na oferty pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id).
    - Jeśli metoda żądania to POST, przetwarza dane formularza.
    - Jeśli formularz jest poprawny, zapisuje nową aplikację z przypisaniem zalogowanego użytkownika jako aplikanta oraz
      przypisaniem oferty pracy.
    - Po zapisaniu nowej aplikacji przekierowuje użytkownika na listę aplikacji.
    - Jeśli metoda żądania to GET, wyświetla pusty formularz do tworzenia nowej aplikacji.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML z formularzem tworzenia aplikacji lub przekierowanie po zapisaniu aplikacji.
    """
    job = get_object_or_404(Job, pk=job_id)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(
                commit=False)  # Tworzy obiekt Application, ale nie zapisuje go jeszcze w bazie danych
            application.job = job  # Przypisuje ofertę pracy do aplikacji
            application.applicant = request.user  # Przypisuje zalogowanego użytkownika jako aplikanta
            application.status = Application.ApplicationStatus.SUBMITTED  # Ustawia status na 'Złożone'
            application.save()  # Zapisuje obiekt Application w bazie danych
            return redirect('jobs:application_list')  # Przekierowuje na listę aplikacji
    else:
        form = ApplicationForm()  # Tworzy pusty formularz
    return render(request, 'jobs/create_application.html',
                  {'form': form, 'job': job})  # Renderuje stronę HTML z formularzem


def public_job_detail_view(request, job_id):
    """
    Widok szczegółów publicznej oferty pracy.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML ze szczegółami oferty pracy.
    """
    job = get_object_or_404(Job, pk=job_id)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje
    return render(request, 'home/public_job_detail.html', {'job': job})  # Renderuje stronę HTML ze szczegółami oferty


def guest_feedback_view(request, job_id):
    """
    Widok do zbierania opinii od gości dla konkretnej oferty pracy.

    - Jeśli użytkownik jest zalogowany, przekierowuje do odpowiedniego widoku na podstawie roli użytkownika.
    - Jeśli metoda żądania to POST, przetwarza dane formularza opinii gości.
    - Jeśli formularz jest poprawny, zapisuje opinię gościa i wysyła email weryfikacyjny.
    - Jeśli użytkownik już zostawił zweryfikowaną opinię, ponownie ustawia opinię jako zweryfikowaną i zapisuje.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML z formularzem opinii gości lub przekierowanie po zapisaniu opinii.
    """
    job = get_object_or_404(Job, pk=job_id)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje

    if request.user.is_authenticated:
        user_role = request.user.role
        if user_role == 'candidate':
            return redirect(reverse('jobs:create_application', args=[job_id]))
        elif user_role in ['client', 'recruiter']:
            warning_message = _("Zarejestrowani klienci i rekruterzy nie mogą zostawić opinii.")
            return render(request, 'home/guest_feedback.html', {'warning_message': warning_message, 'job': job})

    if request.method == 'POST':
        form = GuestFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job = job
            existing_feedback = GuestFeedback.objects.filter(email=feedback.email, is_verified=True).first()
            if existing_feedback:
                feedback.is_verified = True
                feedback.save()
                return redirect('jobs:guest_feedback_thanks')
            else:
                temp_feedback = TempGuestFeedback(
                    job=job,
                    email=feedback.email,
                    message=feedback.message,
                    phone_number=feedback.phone_number
                )
                temp_feedback.save()
                send_verification_email(temp_feedback)  # Отправка письма для верификации
                return redirect(
                    'jobs:guest_feedback_confirmation')  # Страница уведомления о необходимости подтверждения email
        else:
            messages.error(request, _("Proszę poprawić błędy w formularzu."))
    else:
        form = GuestFeedbackForm()

    return render(request, 'home/guest_feedback.html',
                  {'form': form, 'job': job})  # Renderuje stronę HTML z formularzem opinii


def verify_feedback_view(request, token):
    """
    Widok do weryfikacji opinii gości na podstawie tokenu weryfikacyjnego.

    - Pobiera tymczasową opinię gościa na podstawie tokenu weryfikacyjnego.
    - Tworzy nową opinię gościa jako zweryfikowaną.
    - Usuwa tymczasową opinię gościa.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        token (str): Token weryfikacyjny.

    Returns:
        HttpResponse: Przekierowanie na stronę z potwierdzeniem weryfikacji opinii.
    """
    temp_feedback = get_object_or_404(TempGuestFeedback, verification_token=token)
    feedback = GuestFeedback(
        job=temp_feedback.job,
        email=temp_feedback.email,
        message=temp_feedback.message,
        phone_number=temp_feedback.phone_number,
        is_verified=True
    )
    feedback.save()
    temp_feedback.delete()
    return redirect('jobs:guest_feedback_verified')  # Przekierowuje na stronę potwierdzenia weryfikacji opinii


def guest_feedback_verified_view(request):
    """
    Widok strony potwierdzenia weryfikacji opinii gościa.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z potwierdzeniem weryfikacji opinii.
    """
    return render(request, 'home/guest_feedback_verified.html')


def guest_feedback_thanks_view(request):
    """
    Widok strony podziękowania za opinię gościa.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z podziękowaniem za opinię.
    """
    return render(request, 'home/guest_feedback_thanks.html')


def guest_feedback_confirmation_view(request):
    """
    Widok strony potwierdzenia wysłania emaila weryfikacyjnego dla opinii gościa.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z potwierdzeniem wysłania emaila weryfikacyjnego.
    """
    return render(request, 'home/guest_feedback_confirmation.html')


@login_required
def guest_feedback_applications_view(request):
    """
    Widok wyświetlający opinie gości dla ofert pracy rekrutera. Dostępny tylko dla zalogowanych użytkowników z rolą rekrutera.

    - Sprawdza, czy zalogowany użytkownik jest rekruterem. Jeśli nie, zwraca błąd 403 (Access Denied).
    - Pobiera opinie gości dla ofert pracy przypisanych do zalogowanego rekrutera.
    - Umożliwia filtrowanie opinii na podstawie zapytania wyszukiwania.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z listą opinii gości lub błąd 403 (Access Denied).
    """
    if request.user.role != 'recruiter':
        return HttpResponseForbidden("Access Denied")  # Sprawdza, czy użytkownik jest rekruterem

    feedbacks = GuestFeedback.objects.filter(
        job__recruiter=request.user)  # Pobiera opinie gości dla ofert pracy rekrutera

    search_query = request.GET.get('q', '')  # Pobiera zapytanie wyszukiwania z parametrów URL
    if search_query:
        feedbacks = feedbacks.filter(job__title__icontains=search_query)  # Filtrowanie opinii na podstawie zapytania

    context = {
        'feedbacks': feedbacks,
        'search_query': search_query
    }
    return render(request, 'jobs/guest_feedback_applications.html',
                  context)  # Renderuje stronę HTML z listą opinii gości


@login_required
def recruiter_applications_view(request):
    """
    Widok wyświetlający aplikacje na oferty pracy rekrutera. Dostępny tylko dla zalogowanych użytkowników z rolą rekrutera.

    - Sprawdza, czy zalogowany użytkownik jest rekruterem. Jeśli nie, zwraca błąd 403 (Access Denied).
    - Pobiera aplikacje na oferty pracy przypisane do zalogowanego rekrutera.
    - Umożliwia filtrowanie aplikacji na podstawie zapytania wyszukiwania.
    - Umożliwia paginację wyników.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z listą aplikacji na oferty pracy lub błąd 403 (Access Denied).
    """
    if request.user.role != 'recruiter':
        return HttpResponseForbidden("Access Denied")  # Sprawdza, czy użytkownik jest rekruterem

    search_query = request.GET.get('search', '')  # Pobiera zapytanie wyszukiwania z parametrów URL
    page = request.GET.get('page', 1)  # Pobiera numer strony z parametrów URL

    applications = Application.objects.filter(job__recruiter=request.user).select_related('job',
                                                                                          'applicant__candidate_profile')

    # Mapa statusów aplikacji
    status_mapping = {
        'Złożone': 'submitted',
        'Przejrzane': 'reviewed',
        'Zaakceptowane': 'accepted',
        'Odrzucone': 'rejected'
    }

    if search_query in status_mapping:
        search_query = status_mapping[search_query]

    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(applicant__email__icontains=search_query) |
            Q(applicant__candidate_profile__first_name__icontains=search_query) |
            Q(applicant__candidate_profile__last_name__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(created_at__icontains=search_query)
        )

    applications = applications.order_by('-created_at')  # Sortowanie aplikacji według daty utworzenia

    paginator = Paginator(applications, 10)  # Paginacja wyników, 10 aplikacji na stronę
    try:
        applications_page = paginator.page(page)
    except PageNotAnInteger:
        applications_page = paginator.page(1)  # Jeśli numer strony nie jest liczbą, wyświetla pierwszą stronę
    except EmptyPage:
        applications_page = paginator.page(
            paginator.num_pages)  # Jeśli numer strony przekracza liczbę stron, wyświetla ostatnią stronę

    # Obsługa odpowiedzi AJAX
    if request.GET.get('json', '').lower() == 'true':
        applications_list = [
            {
                'id': application.id,
                'job_title': application.job.title,
                'applicant_name': application.get_applicant_full_name(),
                'status': application.get_status_display(),
                'created_at': application.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for application in applications_page
        ]

        pagination_html = ''
        if applications_page.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={applications_page.previous_page_number()}&search={search_query}">Previous</a></li>'
        for num in paginator.page_range:
            if num == applications_page.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&search={search_query}">{num}</a></li>'
        if applications_page.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={applications_page.next_page_number()}&search={search_query}">Next</a></li>'

        return JsonResponse({'applications': applications_list, 'pagination': pagination_html})

    context = {
        'applications': applications_page,
        'search_query': search_query,
        'page_obj': applications_page,
        'paginator': paginator,
    }
    return render(request, 'jobs/recruiter_applications.html', context)  # Renderuje stronę HTML z listą aplikacji


@login_required
def registered_applications_for_job_view(request, job_id):
    """
    Widok wyświetlający aplikacje zarejestrowanych użytkowników na konkretną ofertę pracy.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id) i sprawdza, czy zalogowany użytkownik jest rekruterem tej oferty.
    - Pobiera aplikacje na daną ofertę pracy.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML z listą aplikacji na ofertę pracy.
    """
    job = get_object_or_404(Job, id=job_id,
                            recruiter=request.user)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje
    applications = job.applications.select_related('applicant')  # Pobiera aplikacje na daną ofertę pracy

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'jobs/registered_applications_for_job.html',
                  context)  # Renderuje stronę HTML z listą aplikacji


@login_required
def guest_applications_view(request):
    """
    Widok wyświetlający aplikacje gości na oferty pracy.

    - Pobiera aplikacje gości (aplikacje bez zalogowanego użytkownika) na oferty pracy przypisane do zalogowanego rekrutera.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z listą aplikacji gości.
    """
    applications = Application.objects.filter(job__recruiter=request.user,
                                              applicant__isnull=True)  # Pobiera aplikacje gości
    return render(request, 'jobs/guest_applications.html',
                  {'applications': applications})  # Renderuje stronę HTML z listą aplikacji gości


@login_required
def update_job_status(request, job_id):
    """
    Widok aktualizacji statusu oferty pracy.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id) i sprawdza, czy zalogowany użytkownik jest rekruterem tej oferty.
    - Jeśli metoda żądania to POST, przetwarza dane formularza.
    - Jeśli formularz jest poprawny, zapisuje zmiany w ofercie pracy.
    - Jeśli metoda żądania to GET, wyświetla formularz z aktualnymi danymi oferty pracy.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML z formularzem aktualizacji oferty pracy lub przekierowanie po zapisaniu zmian.
    """
    job = get_object_or_404(Job, pk=job_id)  # Pobiera ofertę pracy lub zwraca błąd 404, jeśli nie istnieje

    if request.user != job.recruiter:
        return HttpResponseForbidden(
            "You are not authorized to update this job.")  # Sprawdza, czy użytkownik jest rekruterem tej oferty

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)  # Przetwarza dane formularza
        if form.is_valid():
            form.save()
            return redirect('jobs:job_detail', job_id=job.pk)  # Przekierowuje po zapisaniu zmian
    else:
        form = JobForm(instance=job)  # Wyświetla formularz z aktualnymi danymi oferty pracy

    return render(request, 'jobs/edit_job.html',
                  {'form': form, 'job': job})  # Renderuje stronę HTML z formularzem aktualizacji oferty pracy


@login_required
def application_detail_view(request, application_id):
    """
    Widok szczegółów aplikacji na ofertę pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera aplikację na podstawie podanego identyfikatora (application_id).
    - Jeśli aplikacja zawiera profil kandydata ze zdjęciem, ustawia URL zdjęcia.
    - W przeciwnym razie, ustawia domyślny URL zdjęcia.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        application_id (int): Identyfikator aplikacji.

    Returns:
        HttpResponse: Renderowana strona HTML z szczegółami aplikacji.
    """
    application = get_object_or_404(Application, pk=application_id)
    photo_url = None
    if hasattr(application.applicant, 'candidate_profile') and application.applicant.candidate_profile.photo:
        photo_url = application.applicant.candidate_profile.photo.url
    else:
        photo_url = static('images/Icon_1.png')

    context = {
        'application': application,
        'photo_url': photo_url
    }
    return render(request, 'jobs/application_detail.html', context)


@login_required
def recruiter_job_list_view(request):
    """
    Widok listy ofert pracy rekrutera. Dostępny tylko dla zalogowanych użytkowników z rolą rekrutera.

    - Pobiera zapytanie wyszukiwania z parametrów URL.
    - Filtrowanie ofert pracy na podstawie tytułu lub statusu.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.

    Returns:
        HttpResponse: Renderowana strona HTML z listą ofert pracy.
    """
    search_query = request.GET.get('search', '')  # Pobiera zapytanie wyszukiwania z parametrów URL
    jobs = Job.objects.filter(recruiter=request.user)

    status_mapping = {
        'Otwarta': 'open',
        'Zamknięta': 'closed'
    }

    if search_query in status_mapping:
        search_query = status_mapping[search_query]

    if search_query:
        jobs = jobs.filter(Q(title__icontains=search_query) | Q(status=search_query))

    jobs = jobs.order_by('title')

    return render(request, 'jobs/recruiter_job_list.html', {'jobs': jobs, 'search_query': search_query})


@login_required
def guest_feedback_applications_for_job_view(request, job_id):
    """
    Widok wyświetlający opinie gości dla konkretnej oferty pracy.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id) i sprawdza, czy zalogowany użytkownik jest rekruterem tej oferty.
    - Pobiera opinie gości dla danej oferty pracy.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Renderowana strona HTML z listą opinii gości dla oferty pracy.
    """
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    feedbacks = job.guest_feedbacks.all()

    context = {
        'job': job,
        'feedbacks': feedbacks,
    }
    return render(request, 'jobs/guest_feedback_applications_for_job.html', context)


@login_required
def update_application_status(request, application_id):
    """
    Widok aktualizacji statusu aplikacji na ofertę pracy.

    - Pobiera aplikację na podstawie podanego identyfikatora (application_id).
    - Jeśli metoda żądania to POST, przetwarza dane formularza.
    - Jeśli formularz jest poprawny, zapisuje zmiany w aplikacji.
    - Jeśli metoda żądania to GET, wyświetla formularz z aktualnymi danymi aplikacji.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        application_id (int): Identyfikator aplikacji.

    Returns:
        HttpResponse: Renderowana strona HTML z formularzem aktualizacji aplikacji lub przekierowanie po zapisaniu zmian.
    """
    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.ApplicationStatus.choices):
            application.status = new_status
            application.save()
            messages.success(request, 'Status aplikacji został pomyślnie zaktualizowany.')
            return redirect('jobs:registered_applications_for_job',
                            job_id=application.job.id)  # Przekierowuje po zapisaniu zmian
        else:
            messages.error(request, 'Недопустимый статус заявки.')
            return redirect('jobs:application_detail', application_id=application_id)

    return render(request, 'jobs/update_application_status.html',
                  {'application': application})  # Renderuje stronę HTML z formularzem aktualizacji aplikacji


@login_required
def like_job(request, job_id):
    """
    Widok do polubienia oferty pracy. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id).
    - Tworzy rekord polubienia oferty pracy dla zalogowanego użytkownika.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Przekierowanie do listy ofert pracy.
    """
    job = get_object_or_404(Job, pk=job_id)
    Like.objects.get_or_create(user=request.user, job=job)
    return redirect('jobs:job_list')  # Przekierowuje do listy ofert pracy


@login_required
def favorite_job(request, job_id):
    """
    Widok do dodania oferty pracy do ulubionych. Dostępny tylko dla zalogowanych użytkowników.

    - Pobiera ofertę pracy na podstawie podanego identyfikatora (job_id).
    - Tworzy rekord ulubionych ofert pracy dla zalogowanego użytkownika.

    Args:
        request (HttpRequest): Obiekt żądania HTTP.
        job_id (int): Identyfikator oferty pracy.

    Returns:
        HttpResponse: Przekierowanie do listy ofert pracy.
    """
    job = get_object_or_404(Job, pk=job_id)
    Favorite.objects.get_or_create(user=request.user, job=job)
    return redirect('jobs:job_list')  # Przekierowuje do listy ofert pracy


class LikedJobsListView(LoginRequiredMixin, ListView):
    """
    Klasa widoku listy polubionych ofert pracy. Dostępna tylko dla zalogowanych użytkowników.

    - Pobiera i wyświetla listę ofert pracy polubionych przez zalogowanego użytkownika.

    Attributes:
        model (Model): Model danych, z którym związany jest widok.
        template_name (str): Ścieżka do szablonu używanego do renderowania strony.
        context_object_name (str): Nazwa kontekstu używana w szablonie.
    """
    model = Job
    template_name = 'jobs/liked_jobs_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        """
        Zwraca zestaw zapytań zawierający polubione oferty pracy zalogowanego użytkownika.

        Returns:
            QuerySet: Zestaw zapytań zawierający polubione oferty pracy.
        """
        liked_job_ids = Like.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        return Job.objects.filter(id__in=liked_job_ids)


class FavoritedJobsListView(LoginRequiredMixin, ListView):
    """
    Klasa widoku listy ulubionych ofert pracy. Dostępna tylko dla zalogowanych użytkowników.

    - Pobiera i wyświetla listę ofert pracy dodanych do ulubionych przez zalogowanego użytkownika.

    Attributes:
        model (Model): Model danych, z którym związany jest widok.
        template_name (str): Ścieżka do szablonu używanego do renderowania strony.
        context_object_name (str): Nazwa kontekstu używana w szablonie.
    """
    model = Job
    template_name = 'jobs/favorited_jobs_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        """
        Zwraca zestaw zapytań zawierający ulubione oferty pracy zalogowanego użytkownika.

        Returns:
            QuerySet: Zestaw zapytań zawierający ulubione oferty pracy.
        """
        favorited_job_ids = Favorite.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        return Job.objects.filter(id__in=favorited_job_ids)

