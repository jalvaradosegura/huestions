from django.views.generic.base import TemplateView


class DemoHomeView(TemplateView):
    template_name = 'demo_home.html'
