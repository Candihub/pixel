"""
Django settings for pixel project.
"""
import os

from configurations import Configuration, values


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Base(Configuration):
    """
    Depends on environment variables that SHOULD be defined:

    DJANGO_SECRET_KEY="yourkey"
    POSTGRES_DB="foo"
    POSTGRES_USER="foo"
    POSTGRES_PASSWORD="bar"
    """

    SECRET_KEY = values.Value(None)

    DEBUG = False

    ALLOWED_HOSTS = []

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # third party
        'mptt',
        'tagulous',
        'django_extensions',

        # Pixel apps
        'apps.core',
        'apps.data',
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

    ROOT_URLCONF = 'pixel.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
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

    WSGI_APPLICATION = 'pixel.wsgi.application'

    # Databases connections
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': values.Value(
                '', environ_name='POSTGRES_DB', environ_prefix=None
            ),
            'USER': values.Value(
                '', environ_name='POSTGRES_USER', environ_prefix=None
            ),
            'PASSWORD': values.Value(
                '', environ_name='POSTGRES_PASSWORD', environ_prefix=None
            ),
            'HOST': values.Value(
                '', environ_name='POSTGRES_HOST', environ_prefix=None
            ),
            'PORT': values.Value(
                '', environ_name='POSTGRES_PORT', environ_prefix=None
            ),
        }
    }

    # Password validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
        },
    ]
    AUTH_USER_MODEL = 'core.Pixeler'
    LOGIN_REDIRECT_URL = 'core:home'

    # Internationalization
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
    MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
    MEDIA_URL = '/media/'

class Development(Base):

    DEBUG = True


class Test(Base):

    INSTALLED_APPS = Base.INSTALLED_APPS + [
        'apps.core.tests.mixins',
    ]
