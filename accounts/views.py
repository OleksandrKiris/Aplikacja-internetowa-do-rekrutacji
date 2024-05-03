from django.contrib.auth import logout, login  # Authentication functions
from django.contrib.auth.decorators import login_required  # For login required decorators
from django.http import Http404  # For handling HTTP exceptions
from django.shortcuts import redirect, render, get_object_or_404  # For rendering templates and redirects
from django.urls import reverse_lazy, reverse  # For lazy URL reverse lookups
from django.views.generic import TemplateView, ListView  # For generic views
from accounts.forms import (RecruiterProfileForm, TaskForm, ClientProfileForm, CandidateProfileForm,
                            UserLoginForm, UserRegistrationForm)
from accounts.models import RecruiterProfile, Task, ClientProfile, CandidateProfile
from jobs.models import Job  # Importing Job model

"---------------------------------------------------HOME PAGE----------------------------------------------------------"


# Home View for rendering the home page
class HomeView(TemplateView):
    template_name = 'home/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Job.objects.filter(status=Job.JobStatus.OPEN)  # Filtering open jobs
        return context


# About View for rendering the About Us page
class AboutView(TemplateView):
    template_name = 'home/about_us.html'


# Contact View for rendering the Contact page
class ContactView(TemplateView):
    template_name = 'home/contact.html'


"-------------------------------REJESTRACJA,LOGOWANIE, CREATE PROFILE, WYLOGOWANIE-------------------------------------"


# Recruiter List View for displaying a list of recruiters
class RecruiterListView(ListView):
    model = RecruiterProfile
    template_name = 'home/recruiters.html'
    context_object_name = 'recruiters'


# Client List View for displaying a list of clients
class ClientListView(ListView):
    model = ClientProfile
    template_name = 'home/client_list.html'
    context_object_name = 'clients'


# Function to handle user registration
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse_lazy('accounts:create_profile'))
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# Function to handle user login
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Store the user's role in the session
            request.session['role'] = user.role

            # Redirect to the dashboard after a successful login
            return redirect(reverse_lazy('accounts:dashboard'))
        else:
            # If the form is not valid, return an error message
            return render(request, 'registration/login.html', {
                'form': form,
                'error': 'Invalid username or password'
            })
    else:
        form = UserLoginForm()

    # Render the login form
    return render(request, 'registration/login.html', {'form': form})


# Function to handle user logout
def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('home'))


# Function to create a user profile, restricted to logged-in users
@login_required
def create_profile(request):
    form_classes = {
        'candidate': CandidateProfileForm,
        'client': ClientProfileForm,
    }
    form_class = form_classes.get(request.user.role)
    if not form_class:
        raise Http404("Этот тип роли не разрешен для создания профиля.")

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('accounts:dashboard')
    else:
        form = form_class()

    return render(request, 'registration/create_profile.html', {'form': form})


@login_required
def dashboard_view(request):
    role = request.user.role
    return render(request, 'dashboard/dashboard.html', {'role': role})


"------------------------------------------DETALI PROFILU,ZMIANA DANNYCH-----------------------------------------------"


# Profile Detail View
@login_required
def profile_detail_view(request):
    user = request.user
    profile_model = {
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)

    if not profile_model:
        raise Http404("Профиль не найден для текущего пользователя.")

    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        return redirect(reverse_lazy('accounts:create_profile'))

    context = {
        'profile': profile,
        'profile_type': user.role
    }
    return render(request, 'profiles/universal_profile_detail.html', context)


# Profile Edit View
@login_required
def profile_edit_view(request):
    user = request.user
    profile_model = {
        'candidate': CandidateProfile,
        'client': ClientProfile,
        'recruiter': RecruiterProfile
    }.get(user.role)

    if not profile_model:
        raise Http404("Профиль не найден для текущего пользователя.")

    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        return redirect(reverse_lazy('accounts:create_profile'))

    form_class = {
        'candidate': CandidateProfileForm,
        'client': ClientProfileForm,
        'recruiter': RecruiterProfileForm
    }.get(user.role)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)  # передаем request.FILES для обработки файлов
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('accounts:dashboard'))
    else:
        form = form_class(instance=profile)

    return render(request, 'profiles/universal_profile_edit.html', {'form': form})


"------------------------------------------TASKI REKRUTERA------------------------------------------------------------"


# Task List View
@login_required
def task_list_view(request):
    tasks = Task.objects.filter(created_by=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


# Task Create View
@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect(reverse_lazy('accounts:task_list'))
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form})


# Task Update View
@login_required
def task_update_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('accounts:task_list'))
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form})


# Task Delete View
@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id, created_by=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect(reverse_lazy('accounts:task_list'))

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
