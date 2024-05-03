from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import JobRequest, JobRequestStatusUpdate
from .forms import JobRequestForm, JobRequestStatusUpdateForm
from accounts.models import RecruiterProfile


@login_required
def client_job_request_list_view(request):
    job_requests = JobRequest.objects.filter(employer=request.user)
    return render(request, 'job_requests/client_job_request_list.html', {
        'job_requests': job_requests
    })


@login_required
def client_job_request_create_view(request):
    if request.method == 'POST':
        form = JobRequestForm(request.POST)
        if form.is_valid():
            job_request = form.save(commit=False)
            job_request.employer = request.user
            job_request.save()
            return redirect(reverse_lazy('requests:client_job_request_list'))
    else:
        form = JobRequestForm()
    return render(request, 'job_requests/job_request_form.html', {'form': form})


@login_required
def client_job_request_delete_view(request, pk):
    job_request = get_object_or_404(JobRequest, pk=pk)
    if request.method == 'POST':
        job_request.delete()
        return redirect(reverse_lazy('requests:client_job_request_list'))
    return render(request, 'job_requests/client_job_request_confirm_delete.html', {'job_request': job_request})


@login_required
def recruiter_job_request_list_view(request):
    job_requests = JobRequest.objects.filter(recruiter=request.user)
    return render(request, 'job_requests/recruiter_job_request_list.html', {
        'job_requests': job_requests
    })


@login_required
def recruiter_list_view(request):
    search_query = request.GET.get('q', '')
    recruiters = RecruiterProfile.objects.all()

    if search_query:
        recruiters = recruiters.filter(user__first_name__icontains=search_query) | recruiters.filter(
            user__last_name__icontains=search_query)

    paginator = Paginator(recruiters, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job_requests/recruiter_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


@login_required
def recruiter_job_request_update_view(request, pk):
    job_request = get_object_or_404(JobRequest, pk=pk)
    if request.method == 'POST':
        form = JobRequestStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['new_status']
            message = form.cleaned_data['message']
            # Сохранение нового статуса запроса
            job_request.status = new_status
            job_request.save()
            # Сохранение информации об изменении статуса и сообщения
            JobRequestStatusUpdate.objects.create(
                job_request=job_request,
                new_status=new_status,
                updated_by=request.user,
                message=message
            )
            return redirect(reverse_lazy('requests:recruiter_job_request_list'))
    else:
        form = JobRequestStatusUpdateForm()
    return render(request, 'job_requests/job_request_status_update.html', {'form': form})


@login_required
def client_job_request_detail_view(request, pk):
    job_request = get_object_or_404(JobRequest, pk=pk)
    status_updates = JobRequestStatusUpdate.objects.filter(job_request=job_request)
    return render(request, 'job_requests/client_job_request_detail.html', {
        'job_request': job_request,
        'status_updates': status_updates
    })
