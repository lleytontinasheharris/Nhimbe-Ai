"""Accounts URL configuration"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('agritex/verify/', views.agritex_verification_view, name='agritex_verify'),
    path('agritex/status/', views.agritex_status_view, name='agritex_status'),
]