from django.urls import path
from .views import news_list_view, all_news_view

"""
Importy:
- from django.urls import path: Importuje funkcję path, która służy do definiowania ścieżek URL w Django.
- from .views import news_list_view, all_news_view: Importuje widoki z bieżącego modułu, które będą obsługiwać odpowiednie ścieżki URL.
"""

app_name = 'news'
"""
Nazwa aplikacji, używana do przestrzeni nazw w URLach.
"""


urlpatterns = [
    path('news/', news_list_view, name='news_list'),
    path('all/', all_news_view, name='all_news_view'),
]
