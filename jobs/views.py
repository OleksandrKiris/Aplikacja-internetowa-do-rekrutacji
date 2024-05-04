from datetime import date

from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, Application, GuestFeedback
from .forms import JobForm, ApplicationForm, GuestFeedbackForm


@login_required
def common_job_list_view(request):
    current_date = date.today()
    user_role = request.user.role
    search_query = request.GET.get('q', '')
    view_mode = request.GET.get('view', 'all')  # Default to 'all'

    if user_role == 'recruiter' and view_mode == 'my':
        # Show only managed jobs
        jobs = request.user.jobs_managed.all()
    else:
        # Show all open jobs (temporarily removed created_at filter for testing)
        jobs = Job.objects.filter(status=Job.JobStatus.OPEN)

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
    user_role = request.user.role

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_role': user_role,
        'current_user': request.user,  # Pass current user to the template
    })



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


@login_required
def job_applications_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user != job.recruiter:
        return HttpResponseForbidden()

    applications = job.applications.select_related('applicant')
    context = {
        'job': job,
        'applications': applications
    }
    return render(request, 'jobs/job_applications.html', context)


def update_application_status_view(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    job = application.job

    if request.user != job.recruiter:
        return HttpResponseForbidden()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if application.update_status(new_status):
            return redirect('jobs:registered_applications_for_job', job_id=job.id)

    return render(request, 'jobs/update_application_status.html', {
        'application': application,
        'job': job
    })


@login_required
def registered_applications_view(request):
    if request.user.role != 'recruiter':
        return HttpResponseForbidden("Access Denied")

    applications = Application.objects.filter(job__recruiter=request.user).select_related('job', 'applicant')

    search_query = request.GET.get('q', '')
    if search_query:
        applications = applications.filter(job__title__icontains=search_query)

    context = {
        'applications': applications,
        'search_query': search_query
    }
    return render(request, 'jobs/registered_applications.html', context)


@login_required
def guest_feedback_applications_view(request):
    if request.user.role != 'recruiter':
        return HttpResponseForbidden("Access Denied")

    feedbacks = GuestFeedback.objects.filter(job__recruiter=request.user)

    search_query = request.GET.get('q', '')
    if search_query:
        feedbacks = feedbacks.filter(job__title__icontains=search_query)

    context = {
        'feedbacks': feedbacks,
        'search_query': search_query
    }
    return render(request, 'jobs/guest_feedback_applications.html', context)


@login_required
def recruiter_applications_view(request):
    if request.user.role != 'recruiter':
        return HttpResponseForbidden("Access Denied")

    search_query = request.GET.get('q', '')

    # Get applications for jobs managed by the logged-in recruiter
    applications = Application.objects.filter(job__recruiter=request.user).select_related('job', 'applicant')

    # Get guest feedback for jobs managed by the logged-in recruiter
    feedbacks = GuestFeedback.objects.filter(job__recruiter=request.user)

    # Filter applications and feedbacks based on the search query
    if search_query:
        applications = applications.filter(job__title__icontains=search_query)
        feedbacks = feedbacks.filter(job__title__icontains=search_query)

    context = {
        'applications': applications,
        'feedbacks': feedbacks,
        'search_query': search_query
    }
    return render(request, 'jobs/recruiter_applications.html', context)


@login_required
def registered_applications_for_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = job.applications.select_related('applicant')

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'jobs/registered_applications_for_job.html', context)


@login_required
def guest_feedback_applications_for_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    feedbacks = job.guest_feedbacks.all()

    context = {
        'job': job,
        'feedbacks': feedbacks
    }
    return render(request, 'jobs/guest_feedback_applications_for_job.html', context)


@login_required
def update_job_status(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    # Check if the logged-in user is the recruiter for this job
    if request.user != job.recruiter:
        return HttpResponseForbidden("You are not authorized to update this job.")

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('jobs:job_detail', job_id=job.pk)
    else:
        # Prepopulate the form with the current job data
        form = JobForm(instance=job)

    return render(request, 'jobs/application_detail.html', {'form': form, 'job': job})


def application_detail_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    job = application.job  # Extract the job associated with the application

    return render(request, 'jobs/application_detail.html', {
        'application': application,
        'job': job,  # Add job to the context
    })
