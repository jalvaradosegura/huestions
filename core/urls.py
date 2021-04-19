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
    path(
        route='403/',
        view=views.Error403View.as_view(),
        name='403',
    ),
    path(
        route='404/',
        view=views.Error404View.as_view(),
        name='404',
    ),
    path(
        route='500/',
        view=views.Error500View.as_view(),
        name='500',
    ),
    path(
        route='a-very-hidden-link-super-hard-to-find/',
        view=views.HiddenRedPandaView.as_view(),
        name='hidden_red_panda',
    ),
]
