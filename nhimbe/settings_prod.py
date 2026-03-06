"""Production settings for PythonAnywhere deployment"""

from .settings import *
import os

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'nhimbe-ai-prod-key-change-this-to-something-random-and-long-2024')

ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com']

CSRF_TRUSTED_ORIGINS = [
    'https://YOUR_USERNAME.pythonanywhere.com',
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'your-groq-api-key-here')

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True