from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('dashboard/agritex/', views.agritex_applications, name='agritex_applications'),
    path('dashboard/agritex/review/<int:user_id>/', views.agritex_review, name='agritex_review'),
]