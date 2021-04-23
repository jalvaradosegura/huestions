from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label=_('Your email'))
    subject = forms.CharField(required=True, label=_('Subject'))
    message = forms.CharField(
        widget=forms.Textarea, required=True, label=_('Message')
    )
    if not settings.DEBUG and not settings.USED_FOR_TESTING:
        captcha = ReCaptchaField()
