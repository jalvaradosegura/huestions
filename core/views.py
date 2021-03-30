from django.views.generic.base import TemplateView


class TermsAndConditionsView(TemplateView):
    template_name = 'terms_and_conditions.html'


class AboutView(TemplateView):
    template_name = 'about.html'
