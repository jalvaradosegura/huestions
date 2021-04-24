from pathlib import Path

from google.oauth2 import service_account

from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    'django_extensions',
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

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = True

# Google Captcha
RECAPTCHA_PUBLIC_KEY = '6LeltbUaAAAAAHcbapp6ewFAbso1sSi19DdVWl8x'
RECAPTCHA_PRIVATE_KEY = '6LeltbUaAAAAAGDTzDw_IYvlhqO_1wqzTT0rFNim'
# SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Tests related
USED_FOR_TESTING = True
