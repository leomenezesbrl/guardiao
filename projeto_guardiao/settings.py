import os
from pathlib import Path
from decouple import config
import dj_database_url

# =====================================
# 🚀 CONFIGURAÇÕES BÁSICAS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.onrender.com').split(',')


# =====================================
# 🚀 LOGGING
# =====================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
}

# =====================================
# 🚀 AUTENTICAÇÃO
# =====================================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'listar_emprestimos'
LOGOUT_REDIRECT_URL = 'login'

# =====================================
# 🚀 APLICAÇÕES INSTALADAS
# =====================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guardiao',
]

# =====================================
# 🚀 MIDDLEWARES
# =====================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise para arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'guardiao.middleware.NivelAcessoMiddleware',
]

# =====================================
# 🚀 URLS E WSGI
# =====================================

ROOT_URLCONF = 'projeto_guardiao.urls'

WSGI_APPLICATION = 'projeto_guardiao.wsgi.application'

# =====================================
# 🚀 TEMPLATES
# =====================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Diretório de templates
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

# =====================================
# 🚀 BANCO DE DADOS
# =====================================

DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}

# =====================================
# 🚀 VALIDAÇÃO DE SENHAS
# =====================================

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

# =====================================
# 🚀 INTERNACIONALIZAÇÃO
# =====================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Manaus'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =====================================
# 🚀 ARQUIVOS ESTÁTICOS E MÍDIA
# =====================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# =====================================
# 🚀 PADRÃO PARA CHAVES PRIMÁRIAS
# =====================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================================
# 🚀 CONFIGURAÇÕES PARA PRODUÇÃO
# =====================================

if os.environ.get('RENDER'):
    DEBUG = False
    ALLOWED_HOSTS = ['guardiao.onrender.com']
