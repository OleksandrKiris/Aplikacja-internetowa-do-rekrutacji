from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView

from accounts.forms import UserRegistrationForm, UserLoginForm, ApplicantProfileForm
from accounts.models import ApplicantProfile, EmployerProfile, RecruiterProfile


class HomeView(TemplateView):
    template_name = 'home/base.html'


class AboutView(TemplateView):
    template_name = 'home/about_us.html'


class ContactView(TemplateView):
    template_name = 'home/contact.html'


class UserRegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')  # Перенаправление на страницу входа после регистрации

    def form_valid(self, form):
        response = super().form_valid(form)
        # Получение выбранной роли и перенаправление на соответствующий дашборд
        role = form.cleaned_data['role']
        if role == 'candidate':
            self.success_url = reverse_lazy('candidate_dashboard')
        elif role == 'client':
            self.success_url = reverse_lazy('client_dashboard')
        return response


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'candidate_profile'):
            return reverse_lazy('accounts:candidate_dashboard')
        elif hasattr(user, 'client_profile'):
            return reverse_lazy('accounts:client_dashboard')
        elif hasattr(user, 'recruiter_profile'):
            return reverse_lazy('accounts:recruiter_dashboard')
        return super().get_success_url()


class CandidateDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/candidate_dashboard.html'


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/client_dashboard.html'


class RecruiterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/recruiter_dashboard.html'


