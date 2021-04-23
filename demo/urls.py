from django.urls import path

from . import views


urlpatterns = [
    path(
        route='',
        view=views.DemoHomeView.as_view(),
        name='demo_home',
    ),
]
