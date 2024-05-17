import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from jobs.models import Job, Application, GuestFeedback, Like, Favorite, TempGuestFeedback

User = get_user_model()


@pytest.mark.django_db
def test_job_creation():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=user, description='Test description',
                             requirements='Test requirements', status='open')
    assert job.title == 'Test Job'
    assert job.is_open()


@pytest.mark.django_db
def test_job_close():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=user, description='Test description',
                             requirements='Test requirements', status='open')
    job.close_job()
    assert not job.is_open()


@pytest.mark.django_db
def test_application_creation():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    applicant = User.objects.create_user(email='applicant@example.com', password='password', role='candidate')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    application = Application.objects.create(job=job, applicant=applicant, cover_letter='Test cover letter')
    assert application.job == job
    assert application.applicant == applicant
    assert application.status == 'submitted'


@pytest.mark.django_db
def test_application_status_update():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    applicant = User.objects.create_user(email='applicant@example.com', password='password', role='candidate')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    application = Application.objects.create(job=job, applicant=applicant, cover_letter='Test cover letter')
    application.update_status('reviewed')
    assert application.status == 'reviewed'


@pytest.mark.django_db
def test_guest_feedback_creation():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    feedback = GuestFeedback.objects.create(job=job, email='guest@example.com', message='Great job opportunity!')
    assert feedback.job == job
    assert feedback.email == 'guest@example.com'
    assert feedback.message == 'Great job opportunity!'


@pytest.mark.django_db
def test_like_creation():
    user = User.objects.create_user(email='user@example.com', password='password', role='candidate')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    like = Like.objects.create(user=user, job=job)
    assert like.user == user
    assert like.job == job


@pytest.mark.django_db
def test_favorite_creation():
    user = User.objects.create_user(email='user@example.com', password='password', role='candidate')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    favorite = Favorite.objects.create(user=user, job=job)
    assert favorite.user == user
    assert favorite.job == job


@pytest.mark.django_db
def test_job_fields_not_empty():
    with pytest.raises(Exception):  # Проверяем, что создание объекта вызовет исключение из-за неправильных данных
        job = Job.objects.create(title='', description='', requirements='')


@pytest.mark.django_db
def test_application_status_update_invalid():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    applicant = User.objects.create_user(email='applicant@example.com', password='password', role='candidate')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    application = Application.objects.create(job=job, applicant=applicant, cover_letter='Test cover letter')
    # Попытка обновления статуса на недопустимое значение
    assert not application.update_status('invalid_status')
    assert application.status == 'submitted'  # Проверяем, что статус остался без изменений


@pytest.mark.django_db
def test_like_unique_together_constraint():
    user = User.objects.create_user(email='user@example.com', password='password', role='candidate')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    Like.objects.create(user=user, job=job)
    # Попытка создания дубликата Like объекта (один пользователь не может лайкнуть одну и ту же работу дважды)
    with pytest.raises(Exception):
        Like.objects.create(user=user, job=job)


@pytest.mark.django_db
def test_favorite_unique_together_constraint():
    user = User.objects.create_user(email='user@example.com', password='password', role='candidate')
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    Favorite.objects.create(user=user, job=job)
    # Попытка создания дубликата Favorite объекта (один пользователь не может добавить одну и ту же работу в избранное дважды)
    with pytest.raises(Exception):
        Favorite.objects.create(user=user, job=job)


@pytest.mark.django_db
def test_job_update():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=user, description='Test description',
                             requirements='Test requirements', status='open')
    job.title = 'Updated Job Title'
    job.description = 'Updated description'
    job.save()
    updated_job = Job.objects.get(id=job.id)
    assert updated_job.title == 'Updated Job Title'
    assert updated_job.description == 'Updated description'


@pytest.mark.django_db
def test_application_rejection():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    applicant = User.objects.create_user(email='applicant@example.com', password='password', role='candidate')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    application = Application.objects.create(job=job, applicant=applicant, cover_letter='Test cover letter')
    application.update_status('rejected')
    assert application.status == 'rejected'
    assert not application.is_accepted()


@pytest.mark.django_db
def test_guest_feedback_verification():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    feedback = GuestFeedback.objects.create(job=job, email='guest@example.com', message='Great job opportunity!')
    feedback.is_verified = True
    feedback.save()
    assert feedback.is_verified


@pytest.mark.django_db
def test_temp_guest_feedback_verification():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    temp_feedback = TempGuestFeedback.objects.create(job=job, email='guest@example.com', message='Temporary feedback')
    verification_token = temp_feedback.generate_verification_token()
    temp_feedback.verification_token = verification_token
    temp_feedback.save()
    assert temp_feedback.verification_token == verification_token


@pytest.mark.django_db
def test_job_requirements():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=user, description='Test description',
                             requirements='Test requirements', status='open')
    assert job.requirements == 'Test requirements'


@pytest.mark.django_db
def test_invalid_job_status_update():
    user = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=user, description='Test description',
                             requirements='Test requirements', status='open')
    job.status = 'invalid_status'
    with pytest.raises(ValidationError):
        job.save()


@pytest.mark.django_db
def test_multiple_guest_feedbacks():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    feedback1 = GuestFeedback.objects.create(job=job, email='guest1@example.com', message='Great job opportunity!')
    feedback2 = GuestFeedback.objects.create(job=job, email='guest2@example.com',
                                             message='Another great job opportunity!')
    assert GuestFeedback.objects.filter(job=job).count() == 2
    assert feedback1.job == job
    assert feedback2.job == job


@pytest.mark.django_db
def test_multiple_temp_guest_feedbacks():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    temp_feedback1 = TempGuestFeedback.objects.create(job=job, email='guest1@example.com',
                                                      message='Temporary feedback 1')
    temp_feedback2 = TempGuestFeedback.objects.create(job=job, email='guest2@example.com',
                                                      message='Temporary feedback 2')
    assert TempGuestFeedback.objects.filter(job=job).count() == 2
    assert temp_feedback1.job == job
    assert temp_feedback2.job == job


@pytest.mark.django_db
def test_candidate_profile_creation():
    candidate = User.objects.create_user(email='candidate@example.com', password='password', role='candidate')
    assert candidate.email == 'candidate@example.com'
    assert candidate.role == 'candidate'


@pytest.mark.django_db
def test_application_count():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    applicant1 = User.objects.create_user(email='applicant1@example.com', password='password', role='candidate')
    applicant2 = User.objects.create_user(email='applicant2@example.com', password='password', role='candidate')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    Application.objects.create(job=job, applicant=applicant1, cover_letter='Test cover letter 1')
    Application.objects.create(job=job, applicant=applicant2, cover_letter='Test cover letter 2')
    assert job.application_count() == 2


@pytest.mark.django_db
def test_unique_temp_guest_feedback_email():
    recruiter = User.objects.create_user(email='recruiter@example.com', password='password', role='recruiter')
    job = Job.objects.create(title='Test Job', recruiter=recruiter, description='Test description',
                             requirements='Test requirements', status='open')
    TempGuestFeedback.objects.create(job=job, email='guest@example.com', message='Temporary feedback')
    with pytest.raises(Exception):
        TempGuestFeedback.objects.create(job=job, email='guest@example.com', message='Duplicate temporary feedback')
