from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import BankAccount
import re

class UserRegistrationForm(forms.ModelForm):
    """
    Customer Registration Form:
    Requires Username, First/Last Name, Email, Password, Phone Number, PAN Number, and Aadhar Number.
    """
    first_name = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 9876543210', 'id': 'id_phone'})
    )
    pan_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input uppercase-input', 'placeholder': 'ABCDE1234F', 'id': 'id_pan', 'maxlength': '10'})
    )
    aadhar_number = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12-digit Aadhar number', 'id': 'id_aadhar', 'maxlength': '12'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter strong password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm your password'}),
        min_length=8
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a unique username'}),
        }

    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number', '').strip().upper()
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan):
            raise ValidationError("Invalid PAN format. Must be 5 uppercase letters, 4 digits, followed by 1 letter (e.g. ABCDE1234F).")
        if BankAccount.objects.filter(pan_number=pan).exists():
            raise ValidationError("A bank account with this PAN Number already exists.")
        return pan

    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number', '').strip()
        if not re.match(r'^[2-9]{1}[0-9]{11}$', aadhar):
            raise ValidationError("Invalid Aadhar Number. Must be exactly 12 numeric digits.")
        if BankAccount.objects.filter(aadhar_number=aadhar).exists():
            raise ValidationError("A bank account with this Aadhar Number already exists.")
        return aadhar

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        pwd_confirm = cleaned_data.get("confirm_password")

        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    """Clean modern login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username or Account Number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Your Password'})
    )
