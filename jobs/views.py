from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job, Application
from .forms import JobForm, ApplicationForm, GuestFeedbackForm
from django.views.generic import ListView
from django.views.generic import TemplateView


class RecruiterJobListView(LoginRequiredMixin, View):
    def get(self, request):
        jobs = request.user.jobs_managed.all()
        return render(request, 'jobs/recruiter_job_list.html', {'jobs': jobs})


class RecruiterJobDetailView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        return render(request, 'jobs/recruiter_job_detail.html', {'job': job})


class RecruiterCreateJobView(LoginRequiredMixin, View):
    def get(self, request):
        form = JobForm()
        return render(request, 'jobs/recruiter_create_job.html', {'form': form})

    def post(self, request):
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect('jobs:recruiter_job_detail', job_id=job.pk)
        return render(request, 'jobs/recruiter_create_job.html', {'form': form})


class CandidateJobListView(LoginRequiredMixin, View):
    def get(self, request):
        jobs = Job.objects.all()
        return render(request, 'jobs/candidate_job_list.html', {'jobs': jobs})


class CandidateJobDetailView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        return render(request, 'jobs/candidate_job_detail.html', {'job': job})


class CandidateCreateApplicationView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        form = ApplicationForm()
        return render(request, 'jobs/candidate_create_application.html', {'form': form, 'job': job})

    def post(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('jobs:candidate_application_list')
        return render(request, 'jobs/candidate_create_application.html', {'form': form, 'job': job})


class CandidateApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'jobs/candidate_application_list.html'

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)


class ClientJobListView(LoginRequiredMixin, View):
    def get(self, request):
        jobs = Job.objects.all()
        return render(request, 'jobs/client_job_list.html', {'jobs': jobs})


class ClientJobDetailView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        return render(request, 'jobs/client_job_detail.html', {'job': job})


class GuestFeedbackView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        form = GuestFeedbackForm()
        return render(request, 'home/guest_feedback.html', {'form': form, 'job': job})

    def post(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        form = GuestFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.job = job
            feedback.save()
            return redirect('guest_feedback_thanks', job_id=job_id)
        return render(request, 'home/guest_feedback.html', {'form': form, 'job': job})


class PublicJobListView(View):
    def get(self, request):
        query = request.GET.get('q')
        if query:
            jobs = Job.objects.filter(title__icontains=query, status=Job.JobStatus.OPEN)
        else:
            jobs = Job.objects.filter(status=Job.JobStatus.OPEN)
        return render(request, 'home/public_job_list.html', {'jobs': jobs})



class PublicJobDetailView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        return render(request, 'home/public_job_detail.html', {'job': job})


class GuestFeedbackThanksView(TemplateView):
    template_name = 'home/guest_feedback_thanks.html'
