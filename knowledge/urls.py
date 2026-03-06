"""Knowledge Base URL configuration"""

from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    # Public views
    path('', views.knowledge_home, name='home'),
    path('search/', views.knowledge_search, name='search'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/rate/', views.rate_article, name='rate_article'),
    
    # Admin views
    path('manage/', views.admin_article_list, name='admin_article_list'),
    path('manage/create/', views.admin_create_article, name='admin_create_article'),
    path('manage/edit/<slug:slug>/', views.admin_edit_article, name='admin_edit_article'),
    path('manage/delete/<slug:slug>/', views.admin_delete_article, name='admin_delete_article'),
]