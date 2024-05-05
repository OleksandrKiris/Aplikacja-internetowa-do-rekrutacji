from datetime import date
from decimal import Decimal, DecimalException

from django.core.checks import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import ListView

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
def common_job_detail_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    user_role = request.user.role

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_role': user_role,
        'current_user': request.user,  # Pass current user to the template
    })


@login_required
def application_list_view(request):
    search_query = request.GET.get('q', '')  # Get the search query
    user_role = request.user.role

    # Filter applications for open jobs based on search query
    if search_query:
        applications = Application.objects.filter(
            applicant=request.user,
            job__title__icontains=search_query,
            job__status=Job.JobStatus.OPEN  # Filter for open jobs only
        ).select_related('job')
    else:
        applications = Application.objects.filter(
            applicant=request.user,
            job__status=Job.JobStatus.OPEN  # Filter for open jobs only
        ).select_related('job')

    context = {
        'applications': applications,
        'user_role': user_role,
        'search_query': search_query  # Pass search query to context
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


class PublicJobListView(ListView):
    model = Job
    template_name = 'home/public_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 7

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        queryset = Job.objects.filter(status=Job.JobStatus.OPEN)

        if query:
            queryset = queryset.filter(
                Q(salary__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query)
            )

        return queryset.order_by('-created_at')

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            jobs = [
                {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:100]  # First 100 characters of description
                }
                for job in context['jobs']
            ]

            # Generate pagination data
            pagination_html = ''
            page_obj = context['page_obj']
            paginator = context['paginator']

            if page_obj.has_previous():
                pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}">Previous</a>'
            for num in paginator.page_range:
                pagination_html += f'<a class="pagination-link" href="?page={num}">{num}</a>'
            if page_obj.has_next():
                pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}">Next</a>'

            return JsonResponse({'jobs': jobs, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)


def public_job_detail_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'home/public_job_detail.html', {'job': job})


def guest_feedback_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        user_role = request.user.role

        if user_role == 'candidate':
            return redirect(reverse('jobs:create_application', args=[job_id]))
        elif user_role in ['client', 'recruiter']:
            # Redirect to the public job list with a warning message
            warning_message = "Zarejestrowani klienci i rekruterzy nie mogą zostawić opinii."
            return render(request, 'home/guest_feedback.html', {'warning_message': warning_message, 'job': job})

    # For unauthenticated users, handle the feedback form
    if request.method == 'POST':
        form = GuestFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job = job
            feedback.save()
            # Redirect to the thank you page
            return redirect('jobs:guest_feedback_thanks')
        else:
            # Provide error messages in form
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = GuestFeedbackForm()

    return render(request, 'home/guest_feedback.html', {'form': form, 'job': job})


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
def guest_applications_view(request):
    applications = Application.objects.filter(job__recruiter=request.user, applicant__isnull=True)
    return render(request, 'jobs/guest_applications.html', {'applications': applications})


@login_required
def update_job_status(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    if request.user != job.recruiter:
        return HttpResponseForbidden("You are not authorized to update this job.")

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('jobs:job_detail', job_id=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


def application_detail_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    return render(request, 'jobs/application_detail.html', {
        'application': application
    })


@login_required
def recruiter_job_list_view(request):
    search_query = request.GET.get('search', '')  # Get the search query from the GET request
    jobs = Job.objects.filter(recruiter=request.user)

    if search_query:
        jobs = jobs.filter(title__icontains=search_query)  # Filter jobs by title if search query is provided

    return render(request, 'jobs/recruiter_job_list.html', {'jobs': jobs, 'search_query': search_query})


@login_required
def guest_feedback_applications_for_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    feedbacks = job.guest_feedbacks.all()

    context = {
        'job': job,
        'feedbacks': feedbacks,
    }
    return render(request, 'jobs/guest_feedback_applications_for_job.html', context)
