from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from requests import views
from requests.views import client_job_request_list_view, client_job_request_create_view, client_job_request_delete_view, \
    recruiter_job_request_list_view, recruiter_job_request_update_view, recruiter_list_view

app_name = 'requests'

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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
