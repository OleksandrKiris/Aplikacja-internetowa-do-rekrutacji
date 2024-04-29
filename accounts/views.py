from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from accounts.forms import UserRegistrationForm, UserLoginForm, ApplicantProfileForm, EmployerProfileForm, \
    RecruiterProfileForm
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


@login_required
def dashboard_redirect(request):
    if request.user.role == 'candidate':
        return redirect('accounts:candidate_dashboard')
    elif request.user.role == 'employer':
        return redirect('accounts:client_dashboard')
    elif request.user.role == 'recruiter':
        return redirect('accounts:recruiter_dashboard')
    else:
        # Обработка для пользователей без роли или других ситуаций
        return redirect('home')


class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('accounts:home')

class CandidateDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/candidate_dashboard.html'


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/client_dashboard.html'


class RecruiterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/recruiter_dashboard.html'


class ApplicantProfileDetailView(LoginRequiredMixin, DetailView):
    model = ApplicantProfile
    template_name = 'profiles/candidate_profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        return ApplicantProfile.objects.filter(user=self.request.user)


class ApplicantProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ApplicantProfile
    form_class = ApplicantProfileForm
    template_name = 'profiles/candidate_profile_edit.html'
    success_url = reverse_lazy('accounts:candidate_dashboard')

    def get_queryset(self):
        return ApplicantProfile.objects.filter(user=self.request.user)


class EmployerProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployerProfile
    template_name = 'profiles/client_profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        return EmployerProfile.objects.filter(user=self.request.user)


class EmployerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployerProfile
    form_class = EmployerProfileForm
    template_name = 'profiles/client_profile_edit.html'
    success_url = reverse_lazy('accounts:client_dashboard')

    def get_queryset(self):
        return EmployerProfile.objects.filter(user=self.request.user)


class RecruiterProfileDetailView(LoginRequiredMixin, DetailView):
    model = RecruiterProfile
    template_name = 'profiles/recruiter_profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        return RecruiterProfile.objects.filter(user=self.request.user)


class RecruiterProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = RecruiterProfile
    form_class = RecruiterProfileForm
    template_name = 'profiles/recruiter_profile_edit.html'
    success_url = reverse_lazy('accounts:recruiter_dashboard')

    def get_queryset(self):
        return RecruiterProfile.objects.filter(user=self.request.user)
