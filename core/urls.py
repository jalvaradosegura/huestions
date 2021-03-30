from django.urls import path

from . import views

urlpatterns = [
    path(
        route='terms-and-conditions/',
        view=views.TermsAndConditionsView.as_view(),
        name='terms_and_conditions',
    ),
    path(
        route='about/',
        view=views.AboutView.as_view(),
        name='about',
    ),
]
