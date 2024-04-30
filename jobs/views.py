from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job, Application
from .forms import JobForm, ApplicationForm


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
            return redirect('candidate_job_detail', job_id=job.pk)
        return render(request, 'jobs/candidate_create_application.html', {'form': form, 'job': job})


class ClientJobListView(LoginRequiredMixin, View):
    def get(self, request):
        jobs = Job.objects.all()
        return render(request, 'jobs/client_job_list.html', {'jobs': jobs})


class ClientJobDetailView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)
        return render(request, 'jobs/client_job_detail.html', {'job': job})
