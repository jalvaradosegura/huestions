from django.urls import path

from . import views

urlpatterns = [
    path(
        route='<str:username>/lists/',
        view=views.UserListsView.as_view(),
        name='lists',
    ),
]
