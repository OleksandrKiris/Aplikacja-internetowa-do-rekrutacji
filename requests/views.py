from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import JobRequest
from .forms import JobRequestForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ClientJobRequestListView(LoginRequiredMixin, ListView):
    model = JobRequest
    template_name = 'job_requests/client_job_request_list.html'
    context_object_name = 'job_requests'

    def get_queryset(self):
        return JobRequest.objects.filter(employer=self.request.user)


class ClientJobRequestCreateView(LoginRequiredMixin, CreateView):
    model = JobRequest
    form_class = JobRequestForm
    template_name = 'job_requests/job_request_form.html'
    success_url = reverse_lazy('requests:client_job_request_list')

    def form_valid(self, form):
        form.instance.employer = self.request.user
        return super().form_valid(form)


class ClientJobRequestDeleteView(LoginRequiredMixin, DeleteView):
    model = JobRequest
    template_name = 'job_requests/client_job_request_confirm_delete.html'
    success_url = reverse_lazy('requests:client_job_request_list')


class RecruiterJobRequestListView(LoginRequiredMixin, ListView):
    model = JobRequest
    template_name = 'job_requests/recruiter_job_request_list.html'
    context_object_name = 'job_requests'

    def get_queryset(self):
        return JobRequest.objects.filter(recruiter=self.request.user)


class RecruiterJobRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = JobRequest
    form_class = JobRequestForm
    template_name = 'job_requests/job_request_form.html'
    success_url = reverse_lazy('requests:recruiter_job_request_list')
