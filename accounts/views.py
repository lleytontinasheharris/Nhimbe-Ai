"""Accounts views"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm, AgritexVerificationForm
from .models import CustomUser


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Nhimbe AI!')
            return redirect('core:home')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
    })


@login_required
def agritex_verification_view(request):
    """Handle AGRITEX officer verification application"""
    user = request.user

    # If already verified or pending, show status
    if user.agritex_verification_status in ['approved', 'pending']:
        return render(request, 'accounts/agritex_status.html', {'user': user})

    if request.method == 'POST':
        form = AgritexVerificationForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.agritex_verification_status = 'pending'
            user.agritex_applied_at = timezone.now()
            user.save()
            messages.success(request, 'Your AGRITEX verification request has been submitted. An admin will review it shortly.')
            return redirect('accounts:agritex_status')
    else:
        form = AgritexVerificationForm(instance=user)

    return render(request, 'accounts/agritex_apply.html', {'form': form})


@login_required
def agritex_status_view(request):
    """Show AGRITEX verification status"""
    return render(request, 'accounts/agritex_status.html', {'user': request.user})