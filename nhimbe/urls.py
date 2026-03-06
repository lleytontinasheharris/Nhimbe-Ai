"""Nhimbe AI - Main URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('forum/', include('forum.urls', namespace='forum')),
    path('knowledge/', include('knowledge.urls', namespace='knowledge')),
    path('chat/', include('chatbot.urls', namespace='chatbot')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)