from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.home, name='home'),
    path(
        route='lists/<slug:slug>/images-credit/',
        view=views.ImagesCreditView.as_view(),
        name='images_credit',
    ),
    path(
        route='lists/<slug:slug>/',
        view=views.AnswerQuestionView.as_view(),
        name='answer_list',
    ),
    path(
        route='lists/<slug:slug>/shared-by-<str:username>/',
        view=views.AnswerQuestionView.as_view(),
        name='answer_list',
    ),
    path(
        route='lists/<slug:list_slug>/add_question/',
        view=views.AddQuestionView.as_view(),
        name='add_question',
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
