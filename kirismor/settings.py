import os
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Określenie podstawowego katalogu projektu
BASE_DIR = Path(__file__).resolve().parent.parent

# Tajny klucz używany przez Django do kryptograficznych operacji
SECRET_KEY = os.getenv('SECRET_KEY')

# Tryb debugowania, który powinien być wyłączony w produkcji
DEBUG = os.getenv('DEBUG') == 'True'

# Lista hostów, które są dozwolone do dostępu do aplikacji
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Aplikacje zainstalowane w projekcie Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'jobs',
    'requests',
    'news',
]

# Middleware używane przez aplikację
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Główna konfiguracja URLi projektu
ROOT_URLCONF = 'kirismor.urls'

# Konfiguracja szablonów
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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# Aplikacja WSGI dla projektu Django
WSGI_APPLICATION = 'kirismor.wsgi.application'

# Konfiguracja bazy danych
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '',
    }
}

# Walidatory haseł
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

# Ustawienia lokalizacyjne
LANGUAGE_CODE = 'pl'
USE_L10N = False
DATE_FORMAT = 'd-m-Y'
DATE_INPUT_FORMATS = ['%d-%m-%Y', '%d/%m/%Y']
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_TZ = True

# Obsługiwane języki
LANGUAGES = [
    ('pl', _('Polski')),
    ('uk', _('Ukrainian')),
    ('ru', _('Russian')),
    ('en', _('English')),
    ('tr', _('Turkish')),
    ('de', _('German')),
    ('ka', _('Georgian')),
]

# Ścieżki do plików lokalizacyjnych
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'templates', 'locale'),
    os.path.join(BASE_DIR, 'accounts', 'locale'),
    os.path.join(BASE_DIR, 'jobs', 'locale'),
    os.path.join(BASE_DIR, 'requests', 'locale'),
    os.path.join(BASE_DIR, 'news', 'locale'),
]

# Ustawienia statycznych plików
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Ustawienia plików mediów
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Domyślne pole automatyczne
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Model użytkownika
AUTH_USER_MODEL = 'accounts.User'

# URL przekierowania po wylogowaniu
LOGOUT_REDIRECT_URL = '/'

# Konfiguracja backendu email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# URL strony
SITE_URL = 'http://localhost:8000'
