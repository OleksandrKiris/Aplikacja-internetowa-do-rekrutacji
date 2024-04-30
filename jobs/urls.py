from django.urls import path
from .views import RecruiterJobListView, RecruiterJobDetailView, RecruiterCreateJobView, \
                   CandidateJobListView, CandidateJobDetailView, CandidateCreateApplicationView, \
                   ClientJobListView, ClientJobDetailView


app_name = 'jobs'

urlpatterns = [
    # URL-адреса для рекрутера
    path('recruiter/jobs/', RecruiterJobListView.as_view(), name='recruiter_job_list'),
    path('recruiter/jobs/<int:job_id>/', RecruiterJobDetailView.as_view(), name='recruiter_job_detail'),
    path('recruiter/jobs/create/', RecruiterCreateJobView.as_view(), name='recruiter_create_job'),

    # URL-адреса для кандидата
    path('candidate/jobs/', CandidateJobListView.as_view(), name='candidate_job_list'),
    path('candidate/jobs/<int:job_id>/', CandidateJobDetailView.as_view(), name='candidate_job_detail'),
    path('candidate/jobs/<int:job_id>/apply/', CandidateCreateApplicationView.as_view(), name='candidate_create_application'),

    # URL-адреса для клиента
    path('client/jobs/', ClientJobListView.as_view(), name='client_job_list'),
    path('client/jobs/<int:job_id>/', ClientJobDetailView.as_view(), name='client_job_detail'),
]
