from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.home, name='home'),
    path(
        route='lists/',
        view=views.QuestionsListView.as_view(),
        name='questions_list',
    ),
    path(
        route='lists/create/',
        view=views.create_question_list,
        name='create_question_list',
    ),
    path(
        route='lists/<slug:slug>/',
        view=views.AnswerListView.as_view(),
        name='answer_list',
    ),
    path(
        route='lists/<slug:slug>/results/',
        view=views.ListResultsView.as_view(),
        name='list_results',
    ),
    path(
        route='lists/<slug:list_slug>/add_question/',
        view=views.AddQuestionView.as_view(),
        name='create_question',
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
        route='lists/<slug:slug>/<int:id>/delete/',
        view=views.DeleteQuestionView.as_view(),
        name='delete_question',
    ),
    path(
        route='lists/<slug:list_slug>/<slug:slug>/<int:question_id>/edit/',
        view=views.EditQuestionView.as_view(),
        name='edit_question',
    ),
]
