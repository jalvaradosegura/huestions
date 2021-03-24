from django import forms
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm


class MyCustomSignupForm(SignupForm):
    check = forms.BooleanField(
        label=mark_safe(
            _(
                'I acknowledge that I have read and agree to the '
                '<a href="%(url)s" target="_blank">Terms and Conditions</a>'
                ) % {'url': reverse('terms_and_conditions')}
        )
    )

    field_order = ['email', 'password1', 'check']

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        return user
