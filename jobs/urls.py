from django.urls import path
from jobs import views
from jobs.views import PublicJobListView, JobListView, LikedJobsListView, FavoritedJobsListView

"""
Importuje moduł path z django.urls, który jest używany do definiowania tras URL w aplikacji Django.

Importuje moduł views z aplikacji jobs, który zawiera funkcje i klasy widoków używane w tej aplikacji.

Importuje klasy widoków z aplikacji jobs:
- PublicJobListView: Widok publicznej listy ofert pracy.
- JobListView: Widok listy ofert pracy dla zalogowanych użytkowników.
- LikedJobsListView: Widok listy polubionych ofert pracy.
- FavoritedJobsListView: Widok listy ulubionych ofert pracy.
"""

app_name = 'jobs'
"""
Ustawia przestrzeń nazw dla tej aplikacji, umożliwiając odwoływanie się do jej tras URL w sposób jednoznaczny.
"""

urlpatterns = [
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('jobs/create/', views.common_create_job_view, name='create_job'),
    path('jobs/<int:job_id>/', views.common_job_detail_view, name='job_detail'),
    path('applications/', views.application_list_view, name='application_list'),
    path('jobs/<int:job_id>/apply/', views.create_application_view, name='create_application'),
    path('guest/feedback/<int:job_id>/', views.guest_feedback_view, name='guest_feedback'),
    path('guest/feedback/thanks/', views.guest_feedback_thanks_view, name='guest_feedback_thanks'),
    path('public/jobs/', PublicJobListView.as_view(), name='public_job_list'),
    path('public/<int:job_id>/', views.public_job_detail_view, name='public_job_detail'),
    path('applications/guest_feedback/', views.guest_feedback_applications_view, name='guest_feedback_applications'),
    path('applications/recruiter/', views.recruiter_applications_view, name='recruiter_applications'),
    path('jobs/<int:job_id>/registered_applications/', views.registered_applications_for_job_view,
         name='registered_applications_for_job'),
    path('jobs/guest_feedback_applications/', views.guest_applications_view, name='guest_applications'),
    path('jobs/<int:job_id>/update_status/', views.update_job_status, name='update_job_status'),
    path('applications/<int:application_id>/', views.application_detail_view, name='application_detail'),
    path('my-jobs/', views.recruiter_job_list_view, name='recruiter_job_list'),
    path('jobs/<int:job_id>/guest_feedback_applications/', views.guest_feedback_applications_for_job_view,
         name='guest_feedback_applications_for_job'),
    path('applications/<int:application_id>/update/', views.update_application_status,
         name='update_application_status'),
    path('like/<int:job_id>/', views.like_job, name='like_job'),
    path('favorite/<int:job_id>/', views.favorite_job, name='favorite_job'),
    path('liked/', LikedJobsListView.as_view(), name='liked_jobs_list'),
    path('favorited/', FavoritedJobsListView.as_view(), name='favorited_jobs_list'),
    path('guest/feedback/<int:job_id>/', views.guest_feedback_view, name='guest_feedback'),
    path('guest/feedback/verify/<str:token>/', views.verify_feedback_view, name='guest_feedback_verify'),
    path('guest/feedback/verified/', views.guest_feedback_verified_view, name='guest_feedback_verified'),
    path('guest/feedback/thanks/', views.guest_feedback_thanks_view, name='guest_feedback_thanks'),
    path('guest/feedback/confirmation/', views.guest_feedback_confirmation_view, name='guest_feedback_confirmation'),
]
