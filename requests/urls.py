from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from requests import views
from requests.views import (
    client_job_request_list_view,
    client_job_request_create_view,
    client_job_request_delete_view,
    recruiter_job_request_list_view,
    recruiter_job_request_update_view,
    recruiter_list_view,
    recruiter_detail_view,
    add_to_favorites_view
)

"""
Importy:
- from django.conf import settings: Importuje ustawienia projektu Django.
- from django.conf.urls.static import static: Importuje funkcję static, która umożliwia serwowanie plików statycznych podczas debugowania.
- from django.urls import path: Importuje funkcję path, która służy do definiowania ścieżek URL w Django.
- from requests import views: Importuje moduł widoków z aplikacji 'requests'.
- from requests.views import (...): Importuje poszczególne widoki z modułu 'requests.views', aby można było je przypisać do ścieżek URL.
"""

app_name = 'requests'
"""
Nazwa aplikacji, używana do przestrzeni nazw w URLach.
"""

urlpatterns = [
    path('requests/', client_job_request_list_view, name='client_job_request_list'),
    path('requests/create/', client_job_request_create_view, name='client_job_request_create'),
    path('requests/<int:pk>/delete/', client_job_request_delete_view, name='client_job_request_delete'),
    path('recruiter/requests/', recruiter_job_request_list_view, name='recruiter_job_request_list'),
    path('recruiter/requests/<int:pk>/edit/', recruiter_job_request_update_view, name='recruiter_job_request_update'),
    path('recruiters/', recruiter_list_view, name='recruiter_list'),
    path('recruiter/requests/<int:pk>/update/', views.recruiter_job_request_update_view,
         name='recruiter_job_request_update'),
    path('client/job_requests/<int:pk>/', views.client_job_request_detail_view, name='client_job_request_detail'),
    path('recruiter/requests/<int:pk>/detail/', views.recruiter_job_request_detail_view,
                       name='recruiter_job_request_detail'),
    path('recruiter/<int:pk>/', recruiter_detail_view, name='recruiter_detail_view'),
    path('add-to-favorites/<int:recruiter_id>/', add_to_favorites_view, name='add_to_favorites'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
