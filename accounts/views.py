import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from accounts.forms import UserRegistrationForm, UserLoginForm, \
    RecruiterProfileForm, TaskForm, ClientProfileForm, CandidateProfileForm
from accounts.models import RecruiterProfile, Task, ClientProfile, CandidateProfile
from jobs.models import Job
from django.views.generic import FormView, CreateView

#---------------------------------------STRONA GOWNA-------------------------------------------------------------------#
class HomeView(TemplateView):
    template_name = 'home/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Job.objects.filter(status=Job.JobStatus.OPEN)
        return context


class AboutView(TemplateView):
    template_name = 'home/about_us.html'


class ContactView(TemplateView):
    template_name = 'home/contact.html'


class RecruiterListView(ListView):
    model = RecruiterProfile
    template_name = 'home/recruiters.html'  # Путь к вашему шаблону с рекрутерами
    context_object_name = 'recruiters'


class ClientListView(ListView):
    model = ClientProfile
    template_name = 'home/client_list.html'
    context_object_name = 'clients'


#---------------------------------------STRONA GOWNA - REJESTRACJA I LOGOWANIE, WYLOGOWANIE----------------------------#


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:create_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def create_profile(request):
    if request.method == 'POST':
        if request.user.role == 'candidate':
            form = CandidateProfileForm(request.POST)
        elif request.user.role == 'client':
            form = ClientProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('accounts:dashboard_redirect')
    else:
        if request.user.role == 'candidate':
            form = CandidateProfileForm()
        elif request.user.role == 'client':
            form = ClientProfileForm()
    return render(request, 'registration/create_profile.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'candidate' and hasattr(user, 'candidate_profile'):
            return reverse_lazy('accounts:candidate_dashboard')
        elif user.role == 'client' and hasattr(user, 'client_profile'):
            return reverse_lazy('accounts:client_dashboard')
        elif user.role == 'recruiter' and hasattr(user, 'recruiter_profile'):
            return reverse_lazy('accounts:recruiter_dashboard')
        else:
            return reverse_lazy('home')

def dashboard_redirect(request):
    user = request.user
    role_redirects = {
        'candidate': 'accounts:candidate_dashboard',
        'client': 'accounts:client_dashboard',
        'recruiter': 'accounts:recruiter_dashboard'
    }
    if user.role in role_redirects:
        return redirect(role_redirects[user.role])
    return redirect('home')

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('accounts:home')


#-------------------------------------DASZBOARDY I AKAUNTY-------------------------------------------------------------#
class CandidateDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/candidate_dashboard.html'


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/client_dashboard.html'


class RecruiterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/recruiter_dashboard.html'


class ApplicantProfileDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр профиля кандидата."""
    model = CandidateProfile
    template_name = 'profiles/candidate_profile_detail.html'
    context_object_name = 'candidate_profile'

    def get_object(self, queryset=None):
        """Переопределяем метод для извлечения объекта по текущему пользователю."""
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No ApplicantProfile found for the current user.")

    def get_queryset(self):
        return CandidateProfile.objects.filter(user=self.request.user)


class ApplicantProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля кандидата."""
    model = CandidateProfile
    form_class = CandidateProfileForm
    template_name = 'profiles/candidate_profile_edit.html'
    success_url = reverse_lazy('accounts:candidate_dashboard')

    def get_object(self, queryset=None):
        """Переопределяем метод для извлечения объекта по текущему пользователю."""
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No ApplicantProfile found for the current user.")

    def get_queryset(self):
        return CandidateProfile.objects.filter(user=self.request.user)


class ClientProfileDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр профиля работодателя."""
    model = ClientProfile
    template_name = 'profiles/client_profile_detail.html'
    context_object_name = 'client_profile'

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No EmployerProfile found for the current user.")

    def get_queryset(self):
        return ClientProfile.objects.filter(user=self.request.user)


class ClientProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля работодателя."""
    model = ClientProfile
    form_class = ClientProfileForm
    template_name = 'profiles/client_profile_edit.html'
    success_url = reverse_lazy('accounts:client_dashboard')

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No EmployerProfile found for the current user.")

    def get_queryset(self):
        return ClientProfile.objects.filter(user=self.request.user)


class RecruiterProfileDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр профиля рекрутера."""
    model = RecruiterProfile
    template_name = 'profiles/recruiter_profile_detail.html'
    context_object_name = 'recrutier_profile'

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No RecruiterProfile found for the current user.")

    def get_queryset(self):
        return RecruiterProfile.objects.filter(user=self.request.user)


class RecruiterProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля рекрутера."""
    model = RecruiterProfile
    form_class = RecruiterProfileForm
    template_name = 'profiles/recruiter_profile_edit.html'
    success_url = reverse_lazy('accounts:recruiter_dashboard')

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No RecruiterProfile found for the current user.")

    def get_queryset(self):
        return RecruiterProfile.objects.filter(user=self.request.user)


#------------------------------------TASKI-----------------------------------------------------------------------------#


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/task_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('accounts:task_list')

    def form_valid(self, form):
        # Установка пользователя как создателя задачи
        form.instance.created_by = self.request.user
        if not self.request.user.is_authenticated:
            # В случае если пользователь не аутентифицирован, можно добавить обработку ошибки
            return HttpResponse("User is not authenticated", status=401)
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('accounts:task_list')

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('accounts:task_list')

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
