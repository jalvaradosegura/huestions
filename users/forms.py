from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField
from django.conf import settings


class MyCustomSignupForm(SignupForm):
    if not settings.DEBUG:
        captcha = ReCaptchaField()

        field_order = ['email', 'password1', 'captcha']
