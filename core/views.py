from django.views.generic.base import TemplateView


class TermsAndConditionsView(TemplateView):
    template_name = 'terms_and_conditions.html'
