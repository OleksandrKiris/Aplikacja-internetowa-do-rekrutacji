# В файле accounts/urls.py

from django.urls import path

from accounts.views import UserRegisterView, CustomLoginView, ClientDashboardView, \
    CandidateDashboardView, RecruiterDashboardView, ApplicantProfileDetailView, ApplicantProfileUpdateView, \
    EmployerProfileDetailView, EmployerProfileUpdateView, RecruiterProfileDetailView, RecruiterProfileUpdateView, \
    dashboard_redirect, CustomLogoutView, TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView

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
    # Заменил <int:pk> на использование сессии для получения профиля текущего пользователя
    path('candidate/profile/', ApplicantProfileDetailView.as_view(), name='candidate_profile'),
    path('candidate/profile/edit/', ApplicantProfileUpdateView.as_view(), name='candidate_profile_edit'),

    # Employer Profile URLs
    # Также использование сессии вместо явного указания pk
    path('client/profile/', EmployerProfileDetailView.as_view(), name='client_profile'),
    path('client/profile/edit/', EmployerProfileUpdateView.as_view(), name='client_profile_edit'),

    # Recruiter Profile URLs
    # Аналогичное изменение для унификации и безопасности
    path('recruiter/profile/', RecruiterProfileDetailView.as_view(), name='recruiter_profile'),
    path('recruiter/profile/edit/', RecruiterProfileUpdateView.as_view(), name='recruiter_profile_edit'),

    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/update/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name='task_delete'),
]


