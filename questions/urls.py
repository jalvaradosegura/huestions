from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.home, name='home'),
    path(
        route='<int:question_id>/', view=views.details, name='question_details'
    ),
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
        view=views.AnswerQuestionListView.as_view(),
        name='questions_list_details',
    ),
    path(
        route='lists/<slug:slug>/results/',
        view=views.QuestionListResultsView.as_view(),
        name='questions_list_details_results',
    ),
    path(
        route='lists/<slug:list_slug>/add_question/',
        view=views.create_question,
        name='create_question',
    ),
    path(
        route='lists/<slug:list_slug>/edit/',
        view=views.EditListView.as_view(),
        name='edit_list',
    ),
]
