from datetime import date

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from .forms import JobForm, ApplicationForm, GuestFeedbackForm


@login_required
def common_job_list_view(request):
    current_date = date.today()
    user_role = request.user.role
    search_query = request.GET.get('q', '')
    view_mode = request.GET.get('view', 'all')  # Default to 'all'

    if user_role == 'recruiter':
        if view_mode == 'my':
            # Show only managed jobs
            jobs = request.user.jobs_managed.all()
        else:
            # Show all jobs
            jobs = Job.objects.filter(status=Job.JobStatus.OPEN, created_at__lte=current_date)
    else:
        # Show only open jobs for non-recruiters
        jobs = Job.objects.filter(status=Job.JobStatus.OPEN, created_at__lte=current_date)

    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    paginator = Paginator(jobs, 10)  # Paginator: 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj,
        'user_role': user_role,
        'search_query': search_query,
        'view_mode': view_mode,
        'page_obj': page_obj
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def common_job_detail_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})


@login_required
def common_create_job_view(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect('jobs:job_detail', job_id=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html', {'form': form})


@login_required
def application_list_view(request):
    applications = Application.objects.filter(applicant=request.user).select_related('job')
    context = {
        'applications': applications,
        'user_role': request.user.role
    }
    return render(request, 'jobs/application_list.html', context)


@login_required
def create_application_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('jobs:application_list')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/create_application.html', {'form': form, 'job': job})


def guest_feedback_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == 'POST':
        form = GuestFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job = job
            feedback.save()
            return redirect('guest_feedback_thanks', job_id=job_id)
    else:
        form = GuestFeedbackForm()
    return render(request, 'home/guest_feedback.html', {'form': form, 'job': job})


def public_job_list_view(request):
    query = request.GET.get('q')
    if query:
        jobs = Job.objects.filter(title__icontains=query, status=Job.JobStatus.OPEN)
    else:
        jobs = Job.objects.filter(status=Job.JobStatus.OPEN)
    return render(request, 'home/public_job_list.html', {'jobs': jobs})


def public_job_detail_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'home/public_job_detail.html', {'job': job})


def guest_feedback_thanks_view(request):
    return render(request, 'home/guest_feedback_thanks.html')
