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

# When uploading files, where to store them
STORE_IN_BUCKET = False

# Google Captcha
RECAPTCHA_PUBLIC_KEY = '6LeltbUaAAAAAHcbapp6ewFAbso1sSi19DdVWl8x'
RECAPTCHA_PRIVATE_KEY = '6LeltbUaAAAAAGDTzDw_IYvlhqO_1wqzTT0rFNim'
# SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
