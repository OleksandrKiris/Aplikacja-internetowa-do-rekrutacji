# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ApplicantProfile, EmployerProfile, RecruiterProfile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('candidate', ('Kandydat')),
        ('employer', ('Klient'))
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            if user.role == 'candidate':
                ApplicantProfile.objects.create(user=user)
            elif user.role == 'employer':
                EmployerProfile.objects.create(user=user)
        return user


class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio', 'date_of_birth', 'skills']



class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['phone_number', 'photo', 'location', 'bio', 'company_name', 'industry']


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['first_name', 'last_name', 'phone_number', 'photo', 'location', 'bio']


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 254}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

