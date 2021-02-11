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
        view=views.QuestionsListListView.as_view(),
        name='questions_list',
    ),
    path(
        route='lists/create/',
        view=views.create_question_list,
        name='create_question_list',
    ),
    path(
        route='lists/<slug:slug>/',
        view=views.QuestionsListDetailView.as_view(),
        name='questions_list_details',
    ),
    path(
        route='lists/<slug:slug>/results/',
        view=views.QuestionsListDetailViewResults.as_view(),
        name='questions_list_details_results',
    ),
    path(
        route='lists/<slug:slug>/add_question/',
        view=views.create_question,
        name='create_question',
    ),
]
