from calories_tracker import __version__
from getpass import getuser
from os import makedirs
from pathlib import Path
from shutil import rmtree

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lzb1pfk%=da50@n-hns(kvnk5bdt+fnv1vq8&15j&1g-tq=6$l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

REST_FRAMEWORK={ 
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication', 
    ], 
    'COERCE_DECIMAL_TO_STRING': False, 
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

if 'rest_framework.authentication.BasicAuthentication' in REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
    print ("You should remove BasicAuthentication for production systems")


SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Calories Tracker API Documentation',
    'DESCRIPTION': 'Interactive documentation',
    'VERSION': __version__,
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken', 
    'corsheaders', 
    'calories_tracker', 
    'drf_spectacular', 
    'simple_history', 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'django_calories_tracker.urls'

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

CORS_ORIGIN_WHITELIST =  "http://127.0.0.1:8012",
WSGI_APPLICATION = 'django_calories_tracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'calories_tracker',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LOCALE_PATHS = (
    str(BASE_DIR) + '/calories_tracker/locale', )
LANGUAGE_CODE = 'en-us'

LANGUAGES=[
    ("en", "English"),  
    ("es",  "Español"), 
    ("fr", "Français") , 
    ("ro", "Romanian"), 
    ("ru", "Russian"), 
]
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TMPDIR=f"/tmp/django_calories_tracker-{getuser()}"
TMPDIR_PREVIEW_CACHE=f"{TMPDIR}/preview_cache"
TMPDIR_FILES=f"{TMPDIR}/files"
TMPDIR_REPORTS=f"{TMPDIR}/reports"
rmtree(TMPDIR, ignore_errors=True)
makedirs(TMPDIR_PREVIEW_CACHE, exist_ok=True)
makedirs(TMPDIR_FILES, exist_ok=True)
makedirs(TMPDIR_REPORTS, exist_ok=True)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = str(BASE_DIR) + "/calories_tracker/static/"
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
