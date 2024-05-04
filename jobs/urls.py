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
    path('jobs/<int:job_id>/applications/', views.job_applications_view, name='job_applications'),
    path('applications/<int:application_id>/update/', views.update_application_status_view,
         name='update_application_status'),
    path('applications/registered/', views.registered_applications_view, name='registered_applications'),
    path('applications/guest_feedback/', views.guest_feedback_applications_view, name='guest_feedback_applications'),
    path('applications/recruiter/', views.recruiter_applications_view, name='recruiter_applications'),
    path('jobs/<int:job_id>/registered_applications/', views.registered_applications_for_job_view, name='registered_applications_for_job'),
    path('jobs/<int:job_id>/guest_feedback_applications/', views.guest_feedback_applications_for_job_view, name='guest_feedback_applications_for_job'),
    path('jobs/<int:job_id>/update_status/', views.update_job_status, name='update_job_status'),
    path('applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
]
