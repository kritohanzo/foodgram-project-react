import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gbv^xez2$sf^7&ek0k#98m1@&vmrgl8n(f)z!tb@_x*%l3za&-'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',
    'api.apps.ApiConfig',
    'extra.apps.ExtraConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATE_DIR = BASE_DIR / "templates"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'main.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'django'),
#         'USER': os.getenv('POSTGRES_USER', 'django_user'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'django_password'),
#         'HOST': os.getenv('DB_HOST', '127.0.0.1'),
#         'PORT': os.getenv('DB_PORT', 5432)
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }
}

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"

# скорее всего не нужен - удалить
# AUTHENTICATION_BACKENDS = ['users.backends.EmailBackend']

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "api.permissions.DisallowAny",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
    'SEARCH_PARAM': 'name'
}

DJOSER = {
    'LOGIN_FIELD': "email",
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.IsAuthenticated'],
        'user_me': ['rest_framework.permissions.IsAuthenticated'],
        'set_password': ['rest_framework.permissions.IsAuthenticated'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
        'subscribe': ['rest_framework.permissions.IsAuthenticated']

    },
    'SERIALIZERS': {
        'user': 'api.serializers.CustomDjoserUserSerializer',
        'subscribe': 'api.serializers.SubscribeSerializer'
    },
    'SET_PASSWORD_RETYPE': False
}