from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.home, name='home'),
    path(route='random/', view=views.random_question, name='random_question'),
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
        view=views.edit_list,
        name='edit_list',
    ),
    path(
        route=(
            'lists/<slug:list_slug>/<slug:question_slug>/'
            '<int:question_id>/add_alternatives/'
        ),
        view=views.add_alternatives,
        name='add_alternatives',
    ),
]
