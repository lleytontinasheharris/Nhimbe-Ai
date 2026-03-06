"""Production settings for PythonAnywhere deployment"""

from .settings import *
import os

DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'nhimbe-ai-production-secret-key-change-this-2024-xyz')

ALLOWED_HOSTS = ['tinashelleytonharris.pythonanywhere.com']

CSRF_TRUSTED_ORIGINS = [
    'https://tinashelleytonharris.pythonanywhere.com',
]

STATIC_URL = '/static/'
STATIC_ROOT = '/home/tinashelleytonharris/Nhimbe-Ai/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/tinashelleytonharris/Nhimbe-Ai/media'

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True