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

    ADMINS = [('The Pixel Team', 'pixel@candihub.eu'), ]

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
        'viewflow',

        # Pixel apps
        'apps.core',
        'apps.data',
        'apps.explorer',
        'apps.submission',
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

    INSTALLED_APPS = Base.INSTALLED_APPS + [
        'debug_toolbar',
    ]

    MIDDLEWARE = Base.MIDDLEWARE + [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'apps': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
            'apps.submission': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False
            },
        },
    }


class Staging(Base):
    """
    Depends on environment variables that SHOULD be defined (in addition to the
    base environment variables):

    EMAIL_HOST=smtp.example.org
    EMAIL_PORT=587
    EMAIL_HOST_USER=babar
    EMAIL_HOST_PASSWORD=KingOfTheElephants
    """

    ALLOWED_HOSTS = ['staging.pixel.candihub.eu', ]

    EMAIL_HOST = values.Value(
        '', environ_name='EMAIL_HOST', environ_prefix=None
    )
    EMAIL_PORT = values.IntegerValue(
        587, environ_name='EMAIL_PORT', environ_prefix=None
    )
    EMAIL_HOST_USER = values.Value(
        '', environ_name='EMAIL_HOST_USER', environ_prefix=None
    )
    EMAIL_HOST_PASSWORD = values.Value(
        '', environ_name='EMAIL_HOST_PASSWORD', environ_prefix=None
    )
    EMAIL_USE_TLS = True
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_SUBJECT_PREFIX = '[Pixel/staging] '
    DEFAULT_FROM_EMAIL = "Pixel Admin <no-reply@pixel.candihub.eu>"
    SERVER_EMAIL = DEFAULT_FROM_EMAIL


class Production(Staging):

    ALLOWED_HOSTS = ['pixel.candihub.eu', ]
    EMAIL_SUBJECT_PREFIX = '[Pixel/production] '


class Test(Base):

    INSTALLED_APPS = Base.INSTALLED_APPS + [
        'apps.core.tests.mixins',
    ]
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'apps': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
            'apps.submission': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False
            },
            'factory': {
                'handlers': ['console'],
                'level': 'ERROR',
            },
        },
    }
