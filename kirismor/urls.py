"""
URL configuration for kirismor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from accounts.views import HomeView, AboutView, ContactView, CustomLogoutView, RecruiterListView, ClientListView
from jobs.views import GuestFeedbackView, PublicJobDetailView, PublicJobListView, GuestFeedbackThanksView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    #path('communications/', include('communications.urls')),
    path('jobs/', include('jobs.urls')),
    path('requests/', include('requests.urls')),
    path('', HomeView.as_view(), name='home'),
    path('o-nas/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('recruiters/', RecruiterListView.as_view(), name='recruiters'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('public/jobs/', PublicJobListView.as_view(), name='public_job_list'),
    path('public/job/<int:job_id>/', PublicJobDetailView.as_view(), name='public_job_detail'),
    path('guest-feedback/<int:job_id>/', GuestFeedbackView.as_view(), name='guest_feedback'),
    path('guest-feedback-thanks/<int:job_id>/', GuestFeedbackThanksView.as_view(), name='guest_feedback_thanks'),



]