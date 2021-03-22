import debug_toolbar
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lists.urls')),
    path('', include('questions.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
