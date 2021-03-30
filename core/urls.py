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
    path(
        route='contact/',
        view=views.ContactView.as_view(),
        name='contact',
    ),
    path(
        route='contact/success/',
        view=views.ContactSuccessView.as_view(),
        name='contact_success',
    ),
]
