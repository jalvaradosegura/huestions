import debug_toolbar
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from lists.models import QuestionList

info_dict = {
    'queryset': QuestionList.objects.all(),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lists.urls')),
    path('', include('questions.urls')),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {'blog': GenericSitemap(info_dict, priority=0.6)}},
        name='django.contrib.sitemaps.views.sitemap',
    ),
]
