"""
Django settings for storyvord project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
import environ

from datetime import timedelta 
from dotenv import load_dotenv


# Import the service_account module
from google.oauth2 import service_account

# Initialize django-environ
env = environ.Env()
# Reading .env file
environ.Env.read_env('')
import os 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
OPENAI_API_KEY = env('OPENAI_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://story-app.azurewebsites.net']
# CSRF_TRUSTED_ORIGINS = ['https://story-app.azurewebsites.net', 'https://storyvord-newly-twice-d432tn3msq-uc.a.run.app']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'storages',
    'rest_framework_swagger',
    #'drf_yasg',                      # Yet Another Swagger generator,
    'crew',
    'client',
    'accounts',
    'project',
    'corsheaders',
    'djoser',
    'drf_spectacular'
]

# Add Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,


     'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # drf-spectacular settings
}


SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer'),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'storyvord.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'storyvord.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Get the database URL from the DATABASE_URL environment variable
database_url = env('DATABASE_URL')
# Get the database password from the DATABASE_PASSWORD environment variable
database_password = env('DATABASE_PASSWORD')

# Parse the database URL
db_config = env.db_url_config(database_url)
# Override the password component with the value from the DATABASE_PASSWORD environment variable
db_config['PASSWORD'] = database_password
db_config['OPTIONS'] = {'sslmode': 'require'}

# DATABASES = {'default': db_config}

# AZURE_ACCOUNT_NAME = 'storyvordprofilepics'
# AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')
# AZURE_CONTAINER = 'storyvordprofilepicscontainer'
# DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'



DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql',  #'django.db.backends.mysql',  # or 
            "NAME": "storyvord",
            "USER": "postgres",
            "PASSWORD": "root",
            "HOST": "127.0.0.1",
            "PORT": 5432,
        }   
    

    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR + '/db.sqlite3', # This is where you put the name of the db file. 
    #              # If one doesn't exist, it will be created at migration time.
    # },


    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',  #'django.db.backends.mysql',  # or 
    #     # 'HOST': '/cloudsql/apis-424409:us-central1:storyvord',    
    #     'HOST': 'apis-424409:us-central1:storyvord',
    #     'NAME': 'storyvord_db',
    #     'USER': 'storyvord',
    #     'PASSWORD': 'storyvord',
    #     'PORT': '5432' 
    # }
       
}


# Google Cloud Storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'storyvord-profile'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, r'D:\storyvord\storyvord\storyvord\apis-gcp-storyvord.json')
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'


# GCP_ACCOUNT_NAME = 'storyvordprofilepics'
# GCP_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')
# GCP_CONTAINER = 'storyvordprofilepicscontainer'
# GCP_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

#AUTH_USER_MODEL = 'core.User'

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = 'static/'

# Consider adding settings for static and media files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True