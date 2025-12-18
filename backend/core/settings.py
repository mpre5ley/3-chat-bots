# Settings for Django configuration

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from env
load_dotenv()

# Assign environment variables for Django
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ['DEBUG']
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS']

# Define Django and 3rd party apps for core functionality
INSTALLED_APPS = {
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'cors_headers',
    'api',
}

# Define middleware used to handle requests
MIDDLEWARE = {
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
}









