from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import News

"""
Importy:
- from django.core.paginator import Paginator: Importuje klasę Paginator z Django, która służy do paginacji (dzielenia na strony) wyników zapytań.
- from django.http import JsonResponse: Importuje klasę JsonResponse, która pozwala na zwracanie odpowiedzi w formacie JSON.
- from django.shortcuts import render, redirect: Importuje funkcje render i redirect, które umożliwiają renderowanie szablonów i przekierowanie użytkownika.
- from .models import News: Importuje model News z bieżącego modułu, aby móc pracować z danymi w widokach.
"""


def news_list_view(request):
    """
    Widok dla wyświetlania listy wiadomości dla zalogowanego użytkownika.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną.
    """
    if request.user.is_authenticated:
        role = request.user.role
        news_list = News.objects.filter(role=role).order_by('-date_posted')
        return render(request, 'dashboard/dashboard.html', {'news_list': news_list, 'role': role})
    else:
        return redirect('news:all_news_view')


def all_news_view(request):
    """
    Widok dla wyświetlania listy wszystkich wiadomości z paginacją.

    Args:
        request (HttpRequest): Obiekt reprezentujący żądanie HTTP.

    Returns:
        HttpResponse: Obiekt odpowiedzi HTTP z renderowaną stroną lub odpowiedzią JSON.
    """
    news_list = News.objects.order_by('-date_posted')
    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    paginator = Paginator(news_list, 7)  # Pokazuje 7 wiadomości na stronę
    page_obj = paginator.get_page(page_number)

    if request.GET.get('format') == 'json':
        news_data = [
            {
                'title': news.title,
                'content': news.content,
                'date_posted': news.date_posted.strftime('%Y-%m-%d')
            }
            for news in page_obj
        ]
        return JsonResponse({
            'news': news_data,
            'page_number': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages
        })

    return render(request, 'news/all_news_list.html', {'page_obj': page_obj, 'paginator': paginator})


"""
Funkcje:
- news_list_view: Funkcja widoku wyświetlająca listę wiadomości dla zalogowanego użytkownika na podstawie jego roli. Jeśli użytkownik nie jest zalogowany, następuje przekierowanie do widoku all_news_view.
- all_news_view: Funkcja widoku wyświetlająca listę wszystkich wiadomości z paginacją. Jeśli żądanie zawiera parametr 'format' równy 'json', zwraca dane w formacie JSON, w przeciwnym razie renderuje stronę HTML z listą wiadomości.
"""
