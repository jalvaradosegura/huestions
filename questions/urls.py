from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.home, name='home'),
    path(route='random/', view=views.random_question, name='random_question'),
    path(
        route='<int:question_id>/', view=views.details, name='question_details'
    ),
]
