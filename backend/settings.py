from pathlib import Path
import os
import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env()

SECRET_KEY = 'django-insecure-3&qyto@en$od2dnauag^6gh#l=rjv#b%70r+$ozbd35vsj=#q0'
DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userAccountApp',
    'rest_framework',
    'corsheaders',
    'insuranceApp',
    'employeeApp',
    'patientApp',
    'insurancePredictionApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'fraud_detection_app',
#         'USER': 'root',
#         # 'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))

}
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'princemugabe568@gmail.com'
EMAIL_HOST_PASSWORD = 'mram vzsp iphw ielb'

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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'templates', 'user', 'static'),
#     os.path.join(BASE_DIR, 'templates', 'insurance', 'static'),
#     os.path.join(BASE_DIR, 'templates', 'prediction', 'static'),
# ]


STATIC_DIR = BASE_DIR / 'static'
# Location of static files
STATICFILES_DIRS = [
    STATIC_DIR,
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
