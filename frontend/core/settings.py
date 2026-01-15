# Settings for Django configuration

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from env
load_dotenv()

# Assign environment variables for Django
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ['DEBUG'].lower() == 'true'
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://127.0.0.1:8001/api')

# Define Django and 3rd party apps for core functionality
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chat',
]

# Define middleware used to handle requests, security, auth
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Defines URLs
ROOT_URLCONF = 'core.urls'

# Defines HTML rendering for Django, enables UI
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

# Defines web interface for Django app
WSGI_APPLICATION = 'core.wsgi.application'

# Defines database, db needs to be defined in backend
DATABASES = {}

# Define time zone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Define primary key field , reduces warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

MIDDLEWARE += ["core.middleware.LoginRequiredMiddleware"]

# When running behind an ALB + nginx reverse proxy, honor X-Forwarded-* headers.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Secure cookies when DEBUG is off (production)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

