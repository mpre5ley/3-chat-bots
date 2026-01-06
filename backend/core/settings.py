# Settings for Django configuration

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url


# Load environment variables from env
load_dotenv()

# Assign environment variables for Django
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ['DEBUG'].lower() == 'true'
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# Define Django and 3rd party apps for core functionality
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

# Define middleware used to handle requests, security, auth
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Defines URLs
ROOT_URLCONF = 'core.urls'

# Defines HTML rendering for Django, enables UI
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Defines web interface for Django app
WSGI_APPLICATION = 'core.wsgi.application'

# Defines database used, SQLite used for development
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# Defines Django password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Define time zone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Define primary key field , reduces warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings to allow admin access through web browser
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Defines react dev servers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allows any domain in Docker
CORS_ALLOW_ALL_ORIGINS = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

# Available models configuration (using Hugging Face Inference with Cerebras provider)
AVAILABLE_MODELS = [
    {
        'id': 'meta-llama/Llama-3.1-8B-Instruct',
        'name': 'Llama 3.1 8B Instruct',
        'description': 'Meta Llama 3.1 8B Instruct model via Cerebras',
        'max_length': 1000
    },
    {
        'id': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
        'name': 'Qwen 3 235B Instruct',
        'description': 'Alibaba Qwen 3 235B Instruct model via Cerebras',
        'max_length': 1000
    },
    {
        'id': 'meta-llama/Llama-3.3-70B-Instruct',
        'name': 'Llama 3.3 70B Instruct',
        'description': 'Meta Llama 3.3 70B Instruct model via Cerebras',
        'max_length': 1000
    },
    {
        'id': 'openai/gpt-oss-120b',
        'name': 'OpenAI gpt-oss-120b',
        'description': 'OpenAI GPT Open-Weight Model via Cerebras',
        'max_length': 1000
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/' 

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication"
    ],
}