from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.db.models import Q
from django.http import JsonResponse
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
    initial_data = {}
    if 'recruiter' in request.GET:
        recruiter_id = request.GET['recruiter']
        try:
            selected_recruiter = RecruiterProfile.objects.get(user_id=recruiter_id)
            initial_data['recruiter'] = selected_recruiter.user.id
        except RecruiterProfile.DoesNotExist:
            selected_recruiter = None

    if request.method == 'POST':
        form = JobRequestForm(request.POST)
        if form.is_valid():
            job_request = form.save(commit=False)
            job_request.employer = request.user
            job_request.save()
            return redirect(reverse_lazy('requests:client_job_request_list'))
    else:
        form = JobRequestForm(initial=initial_data)

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
    recruiters = RecruiterProfile.objects.filter(Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))

    paginator = Paginator(recruiters, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        recruiters_data = []
        for recruiter in page_obj:
            recruiter_data = {
                'id': recruiter.user.id,
                'first_name': recruiter.first_name,
                'last_name': recruiter.last_name,
                'bio': recruiter.bio[:100],  # Truncate bio
                # Add other fields as needed
            }
            recruiters_data.append(recruiter_data)

        pagination_html = ''
        if page_obj.has_previous():
            pagination_html += f'<a class="btn btn-secondary pagination-link" href="?page={page_obj.previous_page_number()}&q={search_query}">Poprzednia</a>'
        for num in page_obj.paginator.page_range:
            pagination_html += f'<a class="pagination-link" href="?page={num}&q={search_query}">{num}</a>'
        if page_obj.has_next():
            pagination_html += f'<a class="btn btn-secondary ms-auto pagination-link" href="?page={page_obj.next_page_number()}&q={search_query}">Następna</a>'

        return JsonResponse({'recruiters': recruiters_data, 'pagination': pagination_html})

    return render(request, 'job_requests/recruiter_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
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


@login_required
def recruiter_job_request_detail_view(request, pk):
    job_request = get_object_or_404(JobRequest, pk=pk, recruiter=request.user)
    status_updates = job_request.status_updates.all()  # Получаем все обновления статуса для этого запроса
    return render(request, 'job_requests/recruiter_job_request_detail.html', {
        'job_request': job_request,
        'status_updates': status_updates
    })