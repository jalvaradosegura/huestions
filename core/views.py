from django.contrib import messages
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.generic.base import TemplateView

from .constants import INVALID_HEADER_ON_EMAIL
from .forms import ContactForm

FOR_TESTING = ''


class TermsAndConditionsView(TemplateView):
    template_name = 'terms_and_conditions.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class ContactView(View):
    template_name = 'contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                if FOR_TESTING:
                    from_email = 'wrong@email.com\n'
                send_mail(subject, message, from_email, ['admin@example.com'])
            except BadHeaderError:
                messages.error(self.request, INVALID_HEADER_ON_EMAIL)
                return render(request, self.template_name, {'form': form})
            return redirect('contact_success')
        return render(request, self.template_name, {'form': form})


class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'


def handler403(request, exception=Exception):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception=Exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)
