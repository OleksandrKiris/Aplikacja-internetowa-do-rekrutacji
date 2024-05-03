from django.urls import path

from jobs import views

app_name = 'jobs'

urlpatterns = [
    path('jobs/', views.common_job_list_view, name='job_list'),
    path('jobs/create/', views.common_create_job_view, name='create_job'),
    path('jobs/<int:job_id>/', views.common_job_detail_view, name='job_detail'),
    path('applications/', views.application_list_view, name='application_list'),
    path('jobs/<int:job_id>/apply/', views.create_application_view, name='create_application'),
    path('guest/feedback/<int:job_id>/', views.guest_feedback_view, name='guest_feedback'),
    path('guest/feedback/thanks/', views.guest_feedback_thanks_view, name='guest_feedback_thanks'),
    path('public/jobs/', views.public_job_list_view, name='public_job_list'),
    path('public/jobs/<int:job_id>/', views.public_job_detail_view, name='public_job_detail'),
]



