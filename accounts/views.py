from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from accounts.forms import UserRegistrationForm, UserLoginForm, ApplicantProfileForm, EmployerProfileForm, \
    RecruiterProfileForm, TaskForm
from accounts.models import ApplicantProfile, EmployerProfile, RecruiterProfile, Task


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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            try:
                if user.role == 'candidate':
                    ApplicantProfile.objects.create(user=user)
                elif user.role == 'employer':
                    EmployerProfile.objects.create(user=user)
            except Exception as e:
                print(f"Error creating profile: {e}")  # Логгирование ошибки
        return user


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
    """Детальный просмотр профиля кандидата."""
    model = ApplicantProfile
    template_name = 'profiles/candidate_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Переопределяем метод для извлечения объекта по текущему пользователю."""
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No ApplicantProfile found for the current user.")

    def get_queryset(self):
        return ApplicantProfile.objects.filter(user=self.request.user)


class ApplicantProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля кандидата."""
    model = ApplicantProfile
    form_class = ApplicantProfileForm
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
        return ApplicantProfile.objects.filter(user=self.request.user)


class EmployerProfileDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр профиля работодателя."""
    model = EmployerProfile
    template_name = 'profiles/client_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No EmployerProfile found for the current user.")

    def get_queryset(self):
        return EmployerProfile.objects.filter(user=self.request.user)


class EmployerProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля работодателя."""
    model = EmployerProfile
    form_class = EmployerProfileForm
    template_name = 'profiles/client_profile_edit.html'
    success_url = reverse_lazy('accounts:client_dashboard')

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No EmployerProfile found for the current user.")

    def get_queryset(self):
        return EmployerProfile.objects.filter(user=self.request.user)


class RecruiterProfileDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр профиля рекрутера."""
    model = RecruiterProfile
    template_name = 'profiles/recruiter_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        try:
            return queryset.get(user=self.request.user)
        except queryset.model.DoesNotExist:
            raise Http404("No RecruiterProfile found for the current user.")

    def get_queryset(self):
        return RecruiterProfile.objects.filter(created_by=self.request.user)


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
        return RecruiterProfile.objects.filter(created_by=self.request.user)


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
