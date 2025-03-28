"""
Django settings for kutok project.

Generated by 'django-admin startproject' using Django 4.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Создаем объект Env
env = environ.Env(DEBUG=(bool, False))
# Читаем файл .env
environ.Env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SECRET_KEY = env('SECRET_KEY')  # Берется из .env
DEBUG = env.bool('DEBUG', default=False)  # Преобразуется в bool
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])  # Преобразуется в список

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

SITE_ID = env('SITE_ID', cast=int)

# Настройки аутентификации
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Верификация email обязательна
ACCOUNT_AUTHENTICATED_REDIRECT_URL = '/'  # Страница, на которую перенаправляется пользователь после логина
SOCIALACCOUNT_EMAIL_REQUIRED = True

# Настройки для социальных аккаунтов
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True  # Запрос email при аутентификации через социальную сеть

SOCIAL_AUTH_GOOGLE_CLIENT_ID = env('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = env('SOCIAL_AUTH_GOOGLE_SECRET')

SOCIAL_AUTH_GOOGLE_SCOPE = ['openid', 'profile', 'email']

# Настройка редиректа после авторизации
SOCIALACCOUNT_LOGIN_ON_SIGNUP = True  # Автоматически логиним пользователя после регистрации
SOCIALACCOUNT_SIGNUP_REDIRECT_URL = '/'  # Куда редиректить после успешной регистрации

# Пример настроек для Google (добавление дополнительных данных)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],  # Права доступа
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,  # Включение PKCE для безопасности
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='kutok'),
        'USER': env('DB_USER', default='blog'),
        'PASSWORD': env('DB_PASSWORD', default='Grekovinka322'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default=5432, cast=int),
    }
}


# Application definition

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'forum.apps.ForumConfig',
    'channels',
    'django_extensions',
    'django.contrib.sites',  # Важно для allauth
    'allauth',                # Само приложение allauth
    'allauth.account',        # Модуль для учётных записей
    'allauth.socialaccount',  # Модуль для социальных аккаунтов
    'allauth.socialaccount.providers.google',  # Провайдер Google
    'chat.apps.ChatConfig'
]

MIDDLEWARE = [
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kutok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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


# Путь к статическим файлам
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles/'


# Папка для хранения статических файлов на сервере (для production)
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# Папка для поиска статических файлов в проекте (в разработке)
STATICFILES_DIRS = [BASE_DIR / 'static']

WSGI_APPLICATION = 'kutok.wsgi.application'
# Меняем WSGI на ASGI
# ASGI_APPLICATION = 'kutok.asgi.application'
ASGI_APPLICATION = 'kutok.asgi.application'

# Настройка Redis для обмена сообщениями
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],  # Redis по стандартному порту
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'kutok',
#         'USER': 'blog',
#         'PASSWORD': 'Grekovinka322',
#     }
# }


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Обычная аутентификация
    'allauth.account.auth_backends.AuthenticationBackend',  # Аутентификация через соцсети
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Настройки для работы с медиафайлами
MEDIA_URL = '/media/'  # URL для доступа к файлам через браузер
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Папка на сервере для хранения файлов§

CSRF_TRUSTED_ORIGINS = [
    "https://localhost",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "https://rozmova.eu",
    "https://www.rozmova.eu",
]

# SECURE_SSL_REDIRECT = True  # Перенаправлять все HTTP-запросы на HTTPS

CSRF_COOKIE_SECURE = True  # Cookies передаются только по HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'  # Устанавливает SameSite флаг для CSRF cookie
SESSION_COOKIE_SECURE = True  # Для сессий тоже
SESSION_COOKIE_SAMESITE = 'Lax'  # SameSite флаг для session cookies
