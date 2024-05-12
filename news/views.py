# news/views.py
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import News


def news_list_view(request):
    if request.user.is_authenticated:
        role = request.user.role
        news_list = News.objects.filter(role=role).order_by('-date_posted')
        return render(request, 'polish/dashboard/dashboard.html', {'news_list': news_list, 'role': role})
    else:
        return redirect('news:all_news_view')


def all_news_view(request):
    news_list = News.objects.order_by('-date_posted')
    try:
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    paginator = Paginator(news_list, 7)  # Показывать 7 новостей на странице
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

    return render(request, 'polish/news/all_news_list.html', {'page_obj': page_obj, 'paginator': paginator})
