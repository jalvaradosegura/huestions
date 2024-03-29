from django.urls import path

from . import views

urlpatterns = [
    path(
        route='<str:username>/lists/',
        view=views.UserListsView.as_view(),
        name='lists',
    ),
    path(
        route='<str:username>/lists/played/',
        view=views.UserPlayedListsView.as_view(),
        name='user_played_lists',
    ),
    path(
        route='<str:username>/stats/',
        view=views.UserStatsView.as_view(),
        name='stats',
    ),
]
