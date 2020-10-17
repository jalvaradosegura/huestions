from django.contrib import admin
from django.urls import path

from questions.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path(route='', view=home, name='home'),
]
