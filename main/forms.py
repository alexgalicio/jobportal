from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Application, UserProfile, StudentProfile, EmployerProfile, Job
from tinymce.widgets import TinyMCE
import re
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})

     # validate email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                "This email is already registered. Please use a different email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # use email as username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
            )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_img',
            'first_name',
            'last_name',
            'phone',
            'school',
            'course',
            'year_level',
            'skills',
            'bio',
        ]
        widgets = {
            'profile_img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +63 912 345 6789'}),
            'school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your school name'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your course'}),
            'year_level': forms.Select(attrs={'class': 'form-select'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Python, HTML, Communication'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a short bio about yourself'}),
        }


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = [
            'first_name',
            'last_name',
            'company_name',
            'logo',
            'phone',
            'company_address',
            'industry',
            'company_size',
            'description',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +63 912 345 6789'}),
            'company_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full company address'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Information Technology'}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Brief company description'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_digits = re.sub(r'[\s\-\(\)]', '', phone)
        phone_digits = phone_digits.replace('+', '')

        if phone_digits.startswith('63'):
            phone_digits = phone_digits[2:]

        if phone_digits.startswith('0'):
            phone_digits = phone_digits[1:]

        if not phone_digits.isdigit() or len(phone_digits) != 10:
            raise ValidationError(
                'Please enter a valid Philippines phone number (e.g., +63 912 345 6789 or 0912 345 6789)')

        formatted_phone = f'+63 {phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:]}'

        return formatted_phone


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'location',
            'workplace',
            'work_type',
            'pay_type',
            'pay_min',
            'pay_max',
            'job_description',
            'summary',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Developer Intern'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Malolos, Bulacan'}),
            'workplace': forms.Select(attrs={'class': 'form-select'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'pay_type': forms.Select(attrs={'class': 'form-select'}),
            'pay_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum pay',
                'step': '1',
                'min': '1',
                'max': '4000000'
            }),
            'pay_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum pay',
                'step': '1',
                'min': '1',
                'max': '4000000'
            }),
            'job_description': TinyMCE(attrs={'cols': 80, 'rows': 15}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief summary of the position'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume']

    resume = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
