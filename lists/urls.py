from django.urls import path

from . import views

urlpatterns = [
    path(
        route='lists/',
        view=views.QuestionsListView.as_view(),
        name='questions_list',
    ),
    path(
        route='lists/create/',
        view=views.create_list,
        name='create_list',
    ),
    path(
        route='lists/<slug:slug>/results/',
        view=views.ListResultsView.as_view(),
        name='list_results',
    ),
    path(
        route='lists/<slug:slug>/results/shared-by-<str:username>/',
        view=views.ListResultsView.as_view(),
        name='list_results',
    ),
    path(
        route='lists/<slug:slug>/edit/',
        view=views.EditListView.as_view(),
        name='edit_list',
    ),
    path(
        route='lists/<slug:slug>/delete/',
        view=views.DeleteListView.as_view(),
        name='delete_list',
    ),
    path(
        route='lists/search/',
        view=views.SearchListsView.as_view(),
        name='search_lists',
    ),
]
