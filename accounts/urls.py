# В файле accounts/urls.py

from django.urls import path

from accounts.views import UserRegisterView, CustomLoginView, ClientDashboardView, \
    CandidateDashboardView, RecruiterDashboardView

# Добавьте пространство имён для приложения accounts
app_name = 'accounts'


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/candidate/', CandidateDashboardView.as_view(), name='candidate_dashboard'),
    path('dashboard/client/', ClientDashboardView.as_view(), name='client_dashboard'),
    path('dashboard/recruiter/', RecruiterDashboardView.as_view(), name='recruiter_dashboard'),

]