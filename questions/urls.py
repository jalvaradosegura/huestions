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
        name='questions_list'
    ),
    path(
        route='lists/<slug:slug>/',
        view=views.QuestionsListDetailView.as_view(),
        name='questions_list_details'
    ),
]
