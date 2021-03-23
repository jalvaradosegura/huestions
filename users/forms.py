from django import forms
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm


class MyCustomSignupForm(SignupForm):
    check = forms.BooleanField(
        label=mark_safe(
            _(
                'Please accept '
                '<a href="%(url)s" target="_bank">Terms and Conditions</a>'
                ) % {'url': reverse('home')}
        )
    )

    field_order = ['email', 'password1', 'check']

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        return user
