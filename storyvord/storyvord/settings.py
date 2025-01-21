import os
from pathlib import Path
import environ
import datetime
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from utils.env_utils import get_bool_env_var, get_site_url

load_dotenv()

SITE_URL = get_site_url()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY')
WEATHERAPI_API_KEY = os.getenv('WEATHERAPI_API_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
# SECURITY WARNING: don't run with debug turned on in production!

PROD = get_bool_env_var('PROD')
if PROD:
    logging.info("Running on PROD")
    DEBUG = False
else:
    logging.info("Running on DEV")
    DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://storyvord-back-end-d432tn3msq-uc.a.run.app']
INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'storages',
    'rest_framework_swagger',
    'django.contrib.sites',
    #'drf_yasg',                      # Yet Another Swagger generator,
    'crew',
    'client',
    'accounts',
    'project',
    'storyvord_calendar',
    'files',
    'tasks',
    'announcement',
    'notification',
    'callsheets',
    'corsheaders',
    'django.core.mail.backends.smtp',
    'drf_spectacular',
    'referral',
    'company',
    'inbox',
    'ai_assistant',
    'chat',
    'network',
    'creative_hub',
    'ticket',


    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history", # optional, if django-simple-history package is used
    'django.contrib.admin'
]

SITE_ID = 1


# Add Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "dj_rest_auth.utils.JWTCookieAuthentication",
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
     'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # drf-spectacular settings
    'EXCEPTION_HANDLER': 'storyvord.exception_handlers.custom_exception_handler',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Storyvord API',
    'DESCRIPTION': 'Storyvord API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVE_URLCONF': 'storyvord.urls',
    'COMPONENT_SPLIT_REQUEST': True,
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'TOKEN_BLACKLIST_ENABLED': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ROTATE_REFRESH_TOKENS': False,

    'JTI_CLAIM': 'jti',

}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': None,
    # Other settings as per your requirements
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
    'allauth.account.middleware.AccountMiddleware',
    'storyvord.logging_middleware.RequestResponseLoggingMiddleware',

]
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
ASGI_APPLICATION = "storyvord.asgi.application"

if PROD:
    DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.postgresql',
                "HOST": os.getenv('DATABASE_HOST'),
                'NAME': os.getenv('DATABASE_NAME'),
                'USER': os.getenv('DATABASE_USER'),
                'PASSWORD': os.getenv('DATABASE_PASSWORD'),
                'PORT': 5432
            }
    }
else:
    DATABASES = {
        'default': {
              'ENGINE': 'django.db.backends.postgresql',
                "HOST": os.getenv('LOCAL_DATABASE_HOST'),
                'NAME': os.getenv('LOCAL_DATABASE_NAME'),
                'USER': os.getenv('LOCAL_DATABASE_USER'),
                'PASSWORD': os.getenv('LOCAL_DATABASE_PASSWORD'),
                'PORT': 5432
            }
    }


AUTH_USER_MODEL = "accounts.User"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',  # A unique name for the in-memory cache
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
# DEFAULT_NO_REPLY_EMAIL = 'getvishalprajapati@gmail.com'
# DEFAULT_FROM_EMAIL = 'getvishalprajapati@gmail.com'  # Update this line
ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.postmarkapp.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('POSTMARK_API_KEY')  # This is always 'postmark'
EMAIL_HOST_PASSWORD = os.getenv('POSTMARK_API_KEY')  # Your Postmark Server API Token
EMAIL_USE_TLS = True  # Use TLS
DEFAULT_FROM_EMAIL = 'no-reply@storyvord.com'  # The verified sender email address on Postmark
DEFAULT_NO_REPLY_EMAIL = 'no-reply@storyvord.com'

# Consider adding settings for static and media files for production
if not PROD:
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
        'timeout': 20,
        'expiration_secs': 500,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
    },
}

AZURE_CONTAINER=os.getenv('AZURE_CONTAINERS')
AZURE_ACCOUNT_NAME=os.getenv('AZURE_ACCOUNT_NAMES')
AZURE_ACCOUNT_KEY=os.getenv('AZURE_ACCOUNT_KEYS')
AZURE_BLOB_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net"

# Google Provider configuration
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1 

# Allauth settings
ACCOUNT_EMAIL_VERIFICATION = "none"  
ACCOUNT_USER_MODEL_USERNAME_FIELD = None 
ACCOUNT_USERNAME_REQUIRED = False  
ACCOUNT_EMAIL_REQUIRED = True  
ACCOUNT_AUTHENTICATION_METHOD = 'email'  

#
LOGIN_REDIRECT_URL = "/api/accounts/google/"
LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': ''
        },
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'offline'},
        'redirect_uri': 'http://localhost:8000',
    }
}
SOCIALACCOUNT_FORMS = {
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'allauth.socialaccount.forms.SignupForm',
}

# Disable the default behavior of logging in the user immediately after the social account is connected
SOCIALACCOUNT_LOGIN_ON_GET = True


# Logging Configuration settings
# Set up the log directory path with date and time
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create subdirectories for each log type
APPLICATION_LOG_DIR = os.path.join(LOG_DIR, 'application')
REQUEST_LOG_DIR = os.path.join(LOG_DIR, 'requests')
ERROR_LOG_DIR = os.path.join(LOG_DIR, 'errors')
DB_INFO_LOG_DIR = os.path.join(LOG_DIR, 'db_info')
INFO_LOG_DIR = os.path.join(LOG_DIR, 'info')  # New directory for INFO logs

for log_subdir in [APPLICATION_LOG_DIR, REQUEST_LOG_DIR, ERROR_LOG_DIR, DB_INFO_LOG_DIR, INFO_LOG_DIR]:
    if not os.path.exists(log_subdir):
        os.makedirs(log_subdir)

# Logging Configuration
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'exclude_autoreload': {
#             '()': 'storyvord.logging_middleware.ExcludeAutoreloadFilter',
#         },
#     },
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'application_file': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(APPLICATION_LOG_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'),
#             'formatter': 'verbose',
#             'filters': ['exclude_autoreload'],
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#         },
#         'request_file': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(REQUEST_LOG_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'),
#             'formatter': 'verbose',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#         },
#         'error_file': {
#             'level': 'ERROR',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(ERROR_LOG_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'),
#             'formatter': 'verbose',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#         },
#         'db_info_file': {  
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(DB_INFO_LOG_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'), 
#             'formatter': 'verbose',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#         },
#         'info_file': {  # New handler for INFO logs
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(INFO_LOG_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'),
#             'formatter': 'verbose',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['application_file', 'info_file'],  # Add info_file handler
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['request_file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         'django.db.backends': {
#             'handlers': ['db_info_file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         'rest_framework': {
#             'handlers': ['request_file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         'django.utils.autoreload': {
#             'handlers': ['application_file'],
#             'level': 'WARNING',
#             'propagate': False,
#         },
#         'errors': {  # Logger for errors
#             'handlers': ['error_file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'info': {  # Logger for INFO logs
#             'handlers': ['info_file'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     },
# }

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_autoreload': {
            '()': 'storyvord.logging_middleware.ExcludeAutoreloadFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'application_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(APPLICATION_LOG_DIR, 'application.log'),
            'formatter': 'verbose',
            'filters': ['exclude_autoreload'],
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        },
        'request_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(REQUEST_LOG_DIR, 'request.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(ERROR_LOG_DIR, 'error.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        },
        'db_info_file': {  
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(DB_INFO_LOG_DIR, 'db_info.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        },
        'info_file': {  
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(INFO_LOG_DIR, 'info.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['application_file', 'info_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_info_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rest_framework': {
            'handlers': ['request_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['application_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'errors': {  
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'info': {  
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


#
# UNFOLD SETTINGS
#

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

def dashboard_callback(request, context):
    """
    Callback to prepare custom variables for index template which is used as dashboard
    template. It can be overridden in application by creating custom admin/index.html.
    """
    context.update(
        {
            "sample": "example",  # this will be injected into templates/admin/index.html
        }
    )
    return context


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Production", "danger"] # info, danger, warning, success


def badge_callback(request):
    return 3

def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")

UNFOLD = {
    "SITE_TITLE": "Storyvord",
    "SITE_HEADER": "Storyvord",
    "SITE_URL": "https://storyvord.com/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    "SITE_ICON": {
        "light": lambda request: static("icon-light.svg"),  # light mode
        "dark": lambda request: static("icon-dark.svg"),  # dark mode
    },
    # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    "SITE_LOGO": {
        "light": lambda request: static("logo-light.svg"),  # light mode
        "dark": lambda request: static("logo-dark.svg"),  # dark mode
    },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.svg"),
        },
    ],
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    "ENVIRONMENT": environment_callback,
    "DASHBOARD_CALLBACK": dashboard_callback,
    "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "image": lambda request: static("sample/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "badge": badge_callback,
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": "accounts/user/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "app_label.model_name_in_lowercase",
            ],
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": "",
                    "permission": permission_callback,
                },
            ],
        },
    ],
}


DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
