from django import forms
from . import models
from .models import Contact, UserProfileInfo
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class FormContact(forms.ModelForm):
    name = forms.CharField(max_length=150, label='Name', widget=forms.TextInput(attrs={
        'class': 'form-control fh5co_contact_text_box',
        'placeholder': 'Enter your name',
    }))
    phone_number = forms.CharField(max_length=20, label='Phone', widget=forms.TextInput(attrs={
        'class': 'form-control fh5co_contact_text_box',
        'placeholder': 'Phone number',
    }))
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={
        'class': 'form-control fh5co_contact_text_box',
        'placeholder': 'Email',
    }))
    subject = forms.CharField(label='Subject', widget=forms.TextInput(attrs={
        'class': 'form-control fh5co_contact_text_box',
        'placeholder': 'Subject',
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control fh5co_contact_message',
        'placeholder': 'Message',
    }))

    class Meta:
        model = Contact
        exclude = ['submit_day', ]


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=100, label='Username', widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    email = forms.EmailField(max_length=100, label='E-mail', widget=forms.EmailInput(attrs={
        'class': 'form-control',
    }))

    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }))

    confirm = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm')


class UserProfileInfoForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Avatar image')
    portfolio = forms.CharField(label='Portfolio', widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    class Meta:
        model = UserProfileInfo
        exclude = ('user',)
