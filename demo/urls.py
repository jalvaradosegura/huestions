from django.urls import path

from . import views


urlpatterns = [
    path(
        route='',
        view=views.DemoHomeView.as_view(),
        name='demo_home',
    ),
    path(
        route='lists/<int:pk>/question-1/',
        view=views.AnswerDemoView1.as_view(),
        name='answer_demo_1',
    ),
    path(
        route='lists/<int:pk>/question-2/',
        view=views.AnswerDemoView2.as_view(),
        name='answer_demo_2',
    ),
    path(
        route='lists/<int:pk>/question-3/',
        view=views.AnswerDemoView3.as_view(),
        name='answer_demo_3',
    ),
    path(
        route='lists/<int:pk>/results/',
        view=views.DemoResults.as_view(),
        name='demo_results',
    ),
]
