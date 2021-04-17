from pathlib import Path

from google.oauth2 import service_account

from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# django-debug-toolbar
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = [
    '127.0.0.1',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'NAME': 'h',
        'USER': 'testuser',
        'PASSWORD': 'hola1234',
    }
}

# Remove all the following lines if you want to store locally
STATIC_URL = 'https://storage.googleapis.com/my-h-static-bucket/static/'

# Credential generated in API & Services
# for media store in the bucket
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    BASE_DIR / env('BUCKET_CREDENTIAL')
)

DEFAULT_FILE_STORAGE = 'huestion_project.gcloud.GoogleCloudMediaFileStorage'
GS_PROJECT_ID = 'testing-h-for-the-first-time'
GS_BUCKET_NAME = 'testing-h-for-the-first-time-media'
MEDIA_ROOT = Path('media/')
UPLOAD_ROOT = 'media/uploads/'
MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)
GS_FILE_OVERWRITE = False

# When uploading files, where to store them
STORE_IN_BUCKET = True
