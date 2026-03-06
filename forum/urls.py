"""Forum URL configuration"""

from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_home, name='home'),
    path('new/', views.create_post, name='create_post'),
    path('search/', views.forum_search, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/poll/', views.poll_comments, name='poll_comments'),
]