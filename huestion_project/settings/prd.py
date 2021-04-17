import os
from pathlib import Path

from google.oauth2 import service_account

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
