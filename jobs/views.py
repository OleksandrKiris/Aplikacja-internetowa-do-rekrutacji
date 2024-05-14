from django.conf.urls.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.html import escape
from django.views.generic import ListView
from .models import Job, Application, GuestFeedback, Like, Favorite
from .forms import JobForm, ApplicationForm, GuestFeedbackForm
from django.contrib import messages


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        search_query = escape(self.request.GET.get('q', '')[:100])
        queryset = Job.objects.filter(status=Job.JobStatus.OPEN)
        if search_query:
            queryset = queryset.filter(
                Q(salary__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['liked_jobs'] = Like.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        context['favorited_jobs'] = Favorite.objects.filter(user=self.request.user).values_list('job_id', flat=True)

        page_obj = context['page_obj']
        paginator = context['paginator']
        range_size = 2
        start_page = max(1, page_obj.number - range_size)
        end_page = min(paginator.num_pages, page_obj.number + range_size)
        context['page_range'] = range(start_page, end_page + 1)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('json', '').lower() == 'true':
            jobs = [
                {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:100],
                    'salary': job.salary
                }
                for job in context['jobs']
            ]
            page_obj = context['page_obj']
            pagination_html = self.generate_pagination_html(page_obj, context['page_range'])
            return JsonResponse({'jobs': jobs, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)

    def generate_pagination_html(self, page_obj, page_range):
        pagination_html = ''
        query = escape(self.request.GET.get('q', ''))
        if page_obj.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&q={query}">Previous</a></li>'
        for num in page_range:
            if num == page_obj.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&q={query}">{num}</a></li>'
        if page_obj.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&q={query}">Next</a></li>'
        return pagination_html


class PublicJobListView(ListView):
    model = Job
    template_name = 'home/public_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 7

    def get_queryset(self):
        search_query = escape(self.request.GET.get('q', '')[:100])
        queryset = Job.objects.filter(status=Job.JobStatus.OPEN)
        if search_query:
            queryset = queryset.filter(
                Q(salary__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context['page_obj']
        paginator = context['paginator']

        # Рассчитаем диапазон страниц вокруг текущей страницы
        range_size = 2
        start_page = max(1, page_obj.number - range_size)
        end_page = min(paginator.num_pages, page_obj.number + range_size)

        context['page_range'] = range(start_page, end_page + 1)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('json', '').lower() == 'true':
            jobs = [
                {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:100],
                    'salary': job.salary
                }
                for job in context['jobs']
            ]
            page_obj = context['page_obj']
            pagination_html = self.generate_pagination_html(page_obj, context['page_range'])
            return JsonResponse({'jobs': jobs, 'pagination': pagination_html})
        return super().render_to_response(context, **response_kwargs)

    def generate_pagination_html(self, page_obj, page_range):
        pagination_html = ''
        query = escape(self.request.GET.get('q', ''))
        if page_obj.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}&q={query}">Previous</a></li>'
        for num in page_range:
            if num == page_obj.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&q={query}">{num}</a></li>'
        if page_obj.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}&q={query}">Next</a></li>'
        return pagination_html


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
            application.status = Application.ApplicationStatus.SUBMITTED  # Установка статуса на 'Złożone'
            application.save()
            return redirect('jobs:application_list')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/create_application.html', {'form': form, 'job': job})


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

    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    applications = Application.objects.filter(job__recruiter=request.user).select_related('job',
                                                                                          'applicant__candidate_profile')

    status_mapping = {
        'Złożone': 'submitted',
        'Przejrzane': 'reviewed',
        'Zaakceptowane': 'accepted',
        'Odrzucone': 'rejected'
    }

    if search_query in status_mapping:
        search_query = status_mapping[search_query]

    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(applicant__email__icontains=search_query) |
            Q(applicant__candidate_profile__first_name__icontains=search_query) |
            Q(applicant__candidate_profile__last_name__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(created_at__icontains=search_query)
        )

    applications = applications.order_by('-created_at')

    paginator = Paginator(applications, 10)
    try:
        applications_page = paginator.page(page)
    except PageNotAnInteger:
        applications_page = paginator.page(1)
    except EmptyPage:
        applications_page = paginator.page(paginator.num_pages)

    if request.GET.get('json', '').lower() == 'true':
        applications_list = [
            {
                'id': application.id,
                'job_title': application.job.title,
                'applicant_name': application.get_applicant_full_name(),
                'status': application.get_status_display(),
                'created_at': application.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for application in applications_page
        ]

        pagination_html = ''
        if applications_page.has_previous():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={applications_page.previous_page_number()}&search={search_query}">Previous</a></li>'
        for num in paginator.page_range:
            if num == applications_page.number:
                pagination_html += f'<li class="page-item active"><span class="page-link">{num}</span></li>'
            else:
                pagination_html += f'<li class="page-item"><a class="page-link" href="?page={num}&search={search_query}">{num}</a></li>'
        if applications_page.has_next():
            pagination_html += f'<li class="page-item"><a class="page-link" href="?page={applications_page.next_page_number()}&search={search_query}">Next</a></li>'

        return JsonResponse({'applications': applications_list, 'pagination': pagination_html})

    context = {
        'applications': applications_page,
        'search_query': search_query,
        'page_obj': applications_page,
        'paginator': paginator,
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
    photo_url = None
    if hasattr(application.applicant, 'candidate_profile') and application.applicant.candidate_profile.photo:
        photo_url = application.applicant.candidate_profile.photo.url
    else:
        photo_url = static('images/Icon_1.png')

    context = {
        'application': application,
        'photo_url': photo_url
    }
    return render(request, 'jobs/application_detail.html', context)


@login_required
def recruiter_job_list_view(request):
    search_query = request.GET.get('search', '')  # Get the search query from the GET request
    jobs = Job.objects.filter(recruiter=request.user)

    status_mapping = {
        'Otwarta': 'open',
        'Zamknięta': 'closed'
    }

    if search_query in status_mapping:
        search_query = status_mapping[search_query]

    if search_query:
        jobs = jobs.filter(Q(title__icontains=search_query) | Q(status=search_query))

    jobs = jobs.order_by('title')

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


@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.ApplicationStatus.choices):
            application.status = new_status
            application.save()
            messages.success(request, 'Статус заявки успешно обновлен.')
            # Redirect to registered_applications_for_job view
            return redirect('jobs:registered_applications_for_job', job_id=application.job.id)
        else:
            messages.error(request, 'Недопустимый статус заявки.')
            return redirect('jobs:application_detail', application_id=application_id)

    return render(request, 'jobs/update_application_status.html', {'application': application})


@login_required
def like_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    Like.objects.get_or_create(user=request.user, job=job)
    return redirect('jobs:job_list')  # Adjust the redirect to the correct job list view name


@login_required
def favorite_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    Favorite.objects.get_or_create(user=request.user, job=job)
    return redirect('jobs:job_list')  # Adjust the redirect to the correct job list view name


class LikedJobsListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/liked_jobs_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        liked_job_ids = Like.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        return Job.objects.filter(id__in=liked_job_ids)


class FavoritedJobsListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/favorited_jobs_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        favorited_job_ids = Favorite.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        return Job.objects.filter(id__in=favorited_job_ids)
