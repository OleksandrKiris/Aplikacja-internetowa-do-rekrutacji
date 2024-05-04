# news/views.py
from django.shortcuts import render, redirect
from .models import News


def news_list_view(request):
    if request.user.is_authenticated:
        role = request.user.role
        news_list = News.objects.filter(role=role).order_by('-date_posted')
        return render(request, 'dashboard/dashboard.html', {'news_list': news_list, 'role': role})
    else:
        return redirect('news:all_news_view')


def all_news_view(request):
    news_list = News.objects.order_by('-date_posted')
    return render(request, 'news/all_news_list.html', {'news_list': news_list})
