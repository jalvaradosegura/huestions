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
        view=views.look_handler403,
        name='look_403',
    ),
    path(
        route='404/',
        view=views.look_handler404,
        name='look_404',
    ),
    path(
        route='500/',
        view=views.look_handler500,
        name='look_500',
    ),
]
