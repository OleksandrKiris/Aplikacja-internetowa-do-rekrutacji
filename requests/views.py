from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from .models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter
from .forms import JobRequestForm, JobRequestStatusUpdateForm
from accounts.models import RecruiterProfile

"""
Importy:
- from django.contrib.auth.decorators import login_required: Importuje dekorator, który wymaga zalogowania się użytkownika, aby uzyskać dostęp do widoku.
- from django.db.models import Q: Importuje klasę Q do tworzenia złożonych zapytań do bazy danych.
- from django.db.models import Count, Case, When, IntegerField: Importuje funkcje do agregacji, warunków i tworzenia pól całkowitych w zapytaniach.
- from django.http import JsonResponse: Importuje klasę JsonResponse, która pozwala na zwracanie odpowiedzi w formacie JSON.
- from django.shortcuts import render, redirect, get_object_or_404: Importuje funkcje skrótów do renderowania szablonów, przekierowań i uzyskiwania obiektów lub zgłaszania błędu 404.
- from django.urls import reverse_lazy, reverse: Importuje funkcje do odwracania nazw URL.
- from django.core.paginator import Paginator: Importuje klasę Paginator do paginacji wyników zapytań.
- from .models import JobRequest, JobRequestStatusUpdate, FavoriteRecruiter: Importuje modele JobRequest, JobRequestStatusUpdate i FavoriteRecruiter z bieżącego modułu.
- from .forms import JobRequestForm, JobRequestStatusUpdateForm: Importuje formularze JobRequestForm i JobRequestStatusUpdateForm z bieżącego modułu.
- from accounts.models import RecruiterProfile: Importuje model RecruiterProfile z modułu 'accounts'.
"""


@login_required
def client_job_request_list_view(request):
    """
    Widok wyświetlający listę zapotrzebowań klienta.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.

    Opis:
        Pobiera zapotrzebowania pracy powiązane z zalogowanym użytkownikiem (pracodawcą)
        i renderuje stronę z listą zapotrzebowań.
    """
    job_requests = JobRequest.objects.filter(employer=request.user)
    # Pobiera wszystkie zapotrzebowania pracy powiązane z zalogowanym użytkownikiem (pracodawcą)

    return render(request, 'job_requests/client_job_request_list.html', {'job_requests': job_requests})
    # Renderuje szablon 'client_job_request_list.html' z danymi zapotrzebowań pracy


@login_required
def client_job_request_create_view(request):
    """
    Widok tworzenia nowego zapotrzebowania klienta.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną lub przekierowanie po zapisaniu.

    Opis:
        Tworzy nowe zapotrzebowanie pracy na podstawie danych wprowadzonych przez użytkownika w formularzu.
        Użytkownik może również przekazać identyfikator rekrutera, który zostanie wstępnie wybrany w formularzu.
    """
    initial_data = {}
    # Inicjalizuje pusty słownik dla wstępnych danych formularza

    if 'recruiter' in request.GET:
        # Sprawdza, czy parametr 'recruiter' jest w żądaniu GET
        recruiter_id = request.GET['recruiter']
        try:
            selected_recruiter = RecruiterProfile.objects.get(user_id=recruiter_id)
            initial_data['recruiter'] = selected_recruiter.user.id
            # Jeśli rekruter istnieje, dodaje jego ID do wstępnych danych formularza
        except RecruiterProfile.DoesNotExist:
            selected_recruiter = None
            # Jeśli rekruter nie istnieje, nic nie robi

    if request.method == 'POST':
        # Jeśli metoda żądania to POST, przetwarza dane formularza
        form = JobRequestForm(request.POST)
        if form.is_valid():
            # Jeśli formularz jest prawidłowy, zapisuje nowe zapotrzebowanie pracy
            job_request = form.save(commit=False)
            job_request.employer = request.user
            job_request.save()
            return redirect(reverse_lazy('requests:client_job_request_list'))
            # Przekierowuje użytkownika do listy zapotrzebowań klienta po zapisaniu
    else:
        form = JobRequestForm(initial=initial_data)
        # Tworzy instancję formularza JobRequestForm z wstępnymi danymi (jeśli istnieją)

    return render(request, 'job_requests/job_request_form.html', {'form': form})
    # Renderuje szablon 'job_request_form.html' z formularzem


@login_required
def client_job_request_delete_view(request, pk):
    """
    Widok usuwania zapotrzebowania klienta.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        pk (int): Klucz główny zapotrzebowania do usunięcia.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z przekierowaniem po usunięciu.

    Opis:
        Usuwa zapotrzebowanie pracy powiązane z podanym kluczem głównym (pk),
        jeśli zapotrzebowanie należy do zalogowanego użytkownika (pracodawcy).
    """
    job_request = get_object_or_404(JobRequest, pk=pk)
    # Pobiera obiekt JobRequest z bazy danych na podstawie klucza głównego (pk) lub zwraca błąd 404, jeśli nie istnieje

    if request.method == 'POST':
        # Sprawdza, czy metoda żądania to POST (czyli czy formularz usunięcia został przesłany)
        job_request.delete()
        # Usuwa obiekt JobRequest z bazy danych
        return redirect(reverse_lazy('requests:client_job_request_list'))
        # Przekierowuje użytkownika do listy zapotrzebowań klienta po usunięciu

    return render(request, 'job_requests/client_job_request_confirm_delete.html', {'job_request': job_request})
    # Renderuje szablon 'client_job_request_confirm_delete.html' z danymi zapotrzebowania do usunięcia


@login_required
def recruiter_job_request_list_view(request):
    """
    Widok wyświetlający listę zapotrzebowań rekrutera.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.

    Opis:
        Pobiera zapotrzebowania pracy powiązane z zalogowanym użytkownikiem (rekruterem)
        i renderuje stronę z listą zapotrzebowań.
    """
    job_requests = JobRequest.objects.filter(recruiter=request.user)
    # Pobiera wszystkie zapotrzebowania pracy powiązane z zalogowanym użytkownikiem (rekruterem)

    return render(request, 'job_requests/recruiter_job_request_list.html', {'job_requests': job_requests})
    # Renderuje szablon 'recruiter_job_request_list.html' z danymi zapotrzebowań pracy


@login_required
def recruiter_list_view(request):
    """
    Widok wyświetlający listę rekruterów.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną lub JsonResponse dla żądań AJAX.

    Opis:
        Pobiera listę rekruterów na podstawie wyszukiwanego zapytania (jeśli istnieje)
        i renderuje stronę z listą rekruterów z paginacją. Obsługuje również żądania AJAX.
    """
    search_query = request.GET.get('q', '')
    # Pobiera wartość parametru 'q' z żądania GET jako zapytanie wyszukiwania. Jeśli nie ma takiego parametru, ustawia pusty ciąg znaków.

    user = request.user
    # Pobiera bieżącego zalogowanego użytkownika

    recruiters = RecruiterProfile.objects.filter(
        Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
    ).annotate(
        is_favorite=Count(
            Case(
                When(favorited_by__user=user, then=1),
                output_field=IntegerField(),
            )
        )
    ).order_by('-is_favorite', 'first_name', 'last_name')
    # Filtruje rekruterów na podstawie wyszukiwanego zapytania (wyszukując w imieniu i nazwisku),
    # a następnie dodaje adnotację 'is_favorite', która sprawdza, czy bieżący użytkownik dodał rekrutera do ulubionych.
    # Rekruterzy są sortowani według tego, czy są ulubieni, a następnie według imienia i nazwiska.

    paginator = Paginator(recruiters, 6)
    # Tworzy obiekt paginatora dla rekruterów, ustawiając 6 rekruterów na stronę

    page_number = request.GET.get('page')
    # Pobiera numer strony z parametrów GET żądania

    page_obj = paginator.get_page(page_number)
    # Pobiera obiekty rekruterów dla bieżącej strony

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Jeśli żądanie jest AJAX, zwraca dane w formacie JSON
        recruiters_data = []
        for recruiter in page_obj:
            recruiter_data = {
                'id': recruiter.user.id,
                'first_name': recruiter.first_name,
                'last_name': recruiter.last_name,
                'bio': recruiter.bio[:100],
                'is_favorite': recruiter.is_favorite,
            }
            recruiters_data.append(recruiter_data)

        pagination_html = ''
        if page_obj.has_previous():
            pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}&q={search_query}">Poprzednia</a>'
        for num in page_obj.paginator.page_range:
            pagination_html += f'<a class="pagination-link" href="?page={num}&q={search_query}">{num}</a>'
        if page_obj.has_next():
            pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}&q={search_query}">Następna</a>'

        return JsonResponse({'recruiters': recruiters_data, 'pagination': pagination_html})

    return render(request, 'job_requests/recruiter_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })
    # Renderuje szablon 'recruiter_list.html' z danymi paginacji i wyszukiwania


@login_required
def recruiter_detail_view(request, pk):
    """
    Widok szczegółowy rekrutera.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        pk (int): Klucz główny rekrutera.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.

    Opis:
        Pobiera szczegóły rekrutera na podstawie podanego klucza głównego (pk)
        i sprawdza, czy jest ulubionym rekruterem zalogowanego użytkownika.
        Renderuje stronę z danymi rekrutera i informacją, czy jest ulubiony.
    """
    recruiter = get_object_or_404(RecruiterProfile, pk=pk)
    # Pobiera obiekt RecruiterProfile z bazy danych na podstawie klucza głównego (pk) lub zwraca błąd 404,
    # jeśli nie istnieje

    is_favorite = FavoriteRecruiter.objects.filter(user=request.user, recruiter=recruiter).exists()
    # Sprawdza, czy zalogowany użytkownik dodał tego rekrutera do ulubionych

    context = {
        'recruiter': recruiter,
        'is_favorite': is_favorite,
        'return_url': '/requests/recruiters/'  # Przekazuje bezpośredni URL powrotu do listy rekruterów
    }
    return render(request, 'job_requests/recruiter_detail.html', context)
    # Renderuje szablon 'recruiter_detail.html' z danymi rekrutera i informacją o ulubionych


@login_required
def add_to_favorites_view(request, recruiter_id):
    """
    Widok dodający rekrutera do ulubionych.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        recruiter_id (int): Identyfikator rekrutera.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z przekierowaniem.

    Opis:
        Dodaje rekrutera do ulubionych dla zalogowanego użytkownika,
        a następnie przekierowuje do szczegółowego widoku rekrutera.
    """
    recruiter = get_object_or_404(RecruiterProfile, pk=recruiter_id)
    # Pobiera obiekt RecruiterProfile z bazy danych na podstawie identyfikatora (recruiter_id) lub zwraca błąd 404, jeśli nie istnieje

    FavoriteRecruiter.objects.get_or_create(user=request.user, recruiter=recruiter)
    # Dodaje rekrutera do ulubionych, jeśli jeszcze nie został dodany

    return redirect(reverse('requests:recruiter_detail_view', args=[recruiter_id]))
    # Przekierowuje użytkownika do szczegółowego widoku rekrutera


@login_required
def recruiter_job_request_update_view(request, pk):
    """
    Widok aktualizacji zapotrzebowania rekrutera.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        pk (int): Klucz główny zapotrzebowania.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną lub przekierowaniem po zapisaniu.

    Opis:
        Umożliwia rekruterowi aktualizację statusu zapotrzebowania na pracę.
        Po zapisaniu nowego statusu i wiadomości, przekierowuje do listy zapotrzebowań rekrutera.
    """
    job_request = get_object_or_404(JobRequest, pk=pk)
    # Pobiera obiekt JobRequest z bazy danych na podstawie klucza głównego (pk) lub zwraca błąd 404, jeśli nie istnieje

    if request.method == 'POST':
        # Jeśli metoda żądania to POST, przetwarza dane formularza
        form = JobRequestStatusUpdateForm(request.POST)
        if form.is_valid():
            # Jeśli formularz jest prawidłowy, zapisuje nowy status i wiadomość
            new_status = form.cleaned_data['new_status']
            message = form.cleaned_data['message']

            job_request.status = new_status
            job_request.save()
            # Zapisuje nowy status zapotrzebowania

            JobRequestStatusUpdate.objects.create(
                job_request=job_request,
                new_status=new_status,
                updated_by=request.user,
                message=message
            )
            # Tworzy nowy wpis aktualizacji statusu

            return redirect(reverse_lazy('requests:recruiter_job_request_list'))
            # Przekierowuje do listy zapotrzebowań rekrutera
    else:
        form = JobRequestStatusUpdateForm()
        # Jeśli metoda żądania to GET, tworzy pusty formularz

    return render(request, 'job_requests/job_request_status_update.html', {'form': form})
    # Renderuje szablon 'job_request_status_update.html' z formularzem


@login_required
def client_job_request_detail_view(request, pk):
    """
    Widok szczegółowy zapotrzebowania klienta.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        pk (int): Klucz główny zapotrzebowania.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.

    Opis:
        Wyświetla szczegóły zapotrzebowania klienta wraz z historią aktualizacji statusu.
    """
    job_request = get_object_or_404(JobRequest, pk=pk)
    # Pobiera obiekt JobRequest z bazy danych na podstawie klucza głównego (pk) lub zwraca błąd 404, jeśli nie istnieje

    status_updates = JobRequestStatusUpdate.objects.filter(job_request=job_request)
    # Pobiera wszystkie aktualizacje statusu powiązane z tym zapotrzebowaniem

    return render(request, 'job_requests/client_job_request_detail.html', {
        'job_request': job_request,
        'status_updates': status_updates
    })
    # Renderuje szablon 'client_job_request_detail.html' z danymi zapotrzebowania i historią aktualizacji


@login_required
def recruiter_job_request_detail_view(request, pk):
    """
    Widok szczegółowy zapotrzebowania rekrutera.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.
        pk (int): Klucz główny zapotrzebowania.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.

    Opis:
        Wyświetla szczegóły zapotrzebowania rekrutera wraz z historią aktualizacji statusu.
    """
    job_request = get_object_or_404(JobRequest, pk=pk, recruiter=request.user)
    # Pobiera obiekt JobRequest z bazy danych na podstawie klucza głównego (pk) i rekrutera, lub zwraca błąd 404,
    # jeśli nie istnieje lub nie należy do zalogowanego rekrutera

    status_updates = job_request.status_updates.all()
    # Pobiera wszystkie aktualizacje statusu powiązane z tym zapotrzebowaniem

    return render(request, 'job_requests/recruiter_job_request_detail.html', {
        'job_request': job_request,
        'status_updates': status_updates
    })
    # Renderuje szablon 'recruiter_job_request_detail.html' z danymi zapotrzebowania i historią aktualizacji
