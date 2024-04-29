# В файле accounts/urls.py

from django.urls import path

from accounts.views import UserRegisterView, CustomLoginView, ClientDashboardView, \
    CandidateDashboardView, RecruiterDashboardView, ApplicantProfileDetailView, ApplicantProfileUpdateView, \
    EmployerProfileDetailView, EmployerProfileUpdateView, RecruiterProfileDetailView, RecruiterProfileUpdateView, \
    dashboard_redirect, CustomLogoutView

# Добавьте пространство имён для приложения accounts
app_name = 'accounts'


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/candidate/', CandidateDashboardView.as_view(), name='candidate_dashboard'),
    path('dashboard/client/', ClientDashboardView.as_view(), name='client_dashboard'),
    path('dashboard/recruiter/', RecruiterDashboardView.as_view(), name='recruiter_dashboard'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    # Applicant Profile URLs
    path('candidate/profile/<int:pk>/', ApplicantProfileDetailView.as_view(), name='candidate_profile'),
    path('candidate/profile/<int:pk>/edit/', ApplicantProfileUpdateView.as_view(), name='candidate_profile_edit'),

    # Employer Profile URLs
    path('client/profile/<int:pk>/', EmployerProfileDetailView.as_view(), name='client_profile'),
    path('client/profile/<int:pk>/edit/', EmployerProfileUpdateView.as_view(), name='client_profile_edit'),

    # Recruiter Profile URLs
    path('recruiter/profile/<int:pk>/', RecruiterProfileDetailView.as_view(), name='recruiter_profile'),
    path('recruiter/profile/<int:pk>/edit/', RecruiterProfileUpdateView.as_view(), name='recruiter_profile_edit'),
]

