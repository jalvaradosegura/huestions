from django.contrib import admin
from django.urls import path, include

from questions.views import home, details

urlpatterns = [
    path('admin/', admin.site.urls),
    path(route='', view=home, name='home'),
    path(route='<int:question_id>/', view=details, name='details'),
    path('accounts/', include('allauth.urls')),
]
