from django.urls import path
from .views import news_list_view, all_news_view


app_name = 'news'

urlpatterns = [
    path('news/', news_list_view, name='news_list'),
    path('all/', all_news_view, name='all_news_view'),
]
