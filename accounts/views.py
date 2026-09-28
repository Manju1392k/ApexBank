from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import UserRegistrationForm, UserLoginForm
from .models import BankAccount

def register_view(request):
    """
    Handles customer registration with PAN & Aadhar KYC capture.
    Generates BankAccount upon successful registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create User
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()

                    # Create BankAccount
                    account = BankAccount.objects.create(
                        user=user,
                        phone_number=form.cleaned_data['phone_number'],
                        pan_number=form.cleaned_data['pan_number'],
                        aadhar_number=form.cleaned_data['aadhar_number'],
                        balance=0.00
                    )

                messages.success(
                    request, 
                    f"Account successfully created! Your Bank Account Number is: {account.account_number}. Please sign in."
                )
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Registration failed due to an error: {str(e)}")
        else:
            messages.error(request, "Please correct the highlighted errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Custom login view supporting username or account number authentication.
    Redirects staff/admin to admin_dashboard and normal customers to dashboard.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Check if identifier is an account number
            user_obj = None
            if login_identifier.isdigit() and len(login_identifier) >= 10:
                try:
                    bank_acc = BankAccount.objects.select_related('user').get(account_number=login_identifier)
                    user_obj = bank_acc.user
                    username = user_obj.username
                except BankAccount.DoesNotExist:
                    username = login_identifier
            else:
                username = login_identifier

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    if user.is_staff:
                        return redirect('admin_dashboard')
                    return redirect('dashboard')
                else:
                    messages.error(request, "This account is inactive. Please contact bank support.")
            else:
                messages.error(request, "Invalid username/account number or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logs out the active user."""
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('login')


@login_required
def profile_view(request):
    """Displays detailed KYC and profile information."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
        
    account = getattr(request.user, 'bank_account', None)
    return render(request, 'accounts/profile.html', {'account': account})
