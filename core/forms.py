from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label=_('Your email'))
    subject = forms.CharField(required=True, label=_('Subject'))
    message = forms.CharField(
        widget=forms.Textarea, required=True, label=_('Message')
    )
