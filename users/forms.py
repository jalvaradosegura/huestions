from allauth.account.forms import ResetPasswordForm, SignupForm
from captcha.fields import ReCaptchaField
from django.conf import settings


class MyCustomSignupForm(SignupForm):
    if not settings.DEBUG and not settings.USED_FOR_TESTING:
        captcha = ReCaptchaField()

        field_order = ['email', 'password1', 'captcha']


class MyCustomResetPasswordForm(ResetPasswordForm):
    if not settings.DEBUG and not settings.USED_FOR_TESTING:
        captcha = ReCaptchaField()

        field_order = ['email', 'captcha']
