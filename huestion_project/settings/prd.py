import os

from .base import *  # noqa

ALLOWED_HOSTS = ['*']
DEBUG = True

if os.getenv('GAE_APPLICATION', None):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': '/cloudsql/testing-h-for-the-first-time:southamerica-east1:h-instance',
            'USER': 'testuser',
            'PASSWORD': 'hola1234',
            'NAME': 'h',
        }
    }

STATIC_URL = 'https://storage.googleapis.com/my-h-static-bucket/static/'
