from django.urls import path
from .views import (
    ClientJobRequestListView, ClientJobRequestCreateView,
    RecruiterJobRequestListView, RecruiterJobRequestUpdateView, ClientJobRequestDeleteView
)

app_name = 'requests'

urlpatterns = [
    path('client/requests/', ClientJobRequestListView.as_view(), name='client_job_request_list'),
    path('client/requests/create/', ClientJobRequestCreateView.as_view(), name='client_job_request_create'),
    path('client/requests/<int:pk>/delete/', ClientJobRequestDeleteView.as_view(), name='client_job_request_delete'),
    path('recruiter/requests/', RecruiterJobRequestListView.as_view(), name='recruiter_job_request_list'),
    path('recruiter/requests/<int:pk>/update/', RecruiterJobRequestUpdateView.as_view(), name='recruiter_job_request_update'),
]
