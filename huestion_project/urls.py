import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views as error_views
from lists.models import QuestionList

info_dict = {
    'queryset': QuestionList.objects.filter(active=True),
}

urlpatterns = [
    path('', include('lists.urls')),
    path('', include('questions.urls')),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('demo/', include('demo.urls')),
    path('accounts/', include('allauth.urls')),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {'blog': GenericSitemap(info_dict, priority=0.6)}},
        name='django.contrib.sitemaps.views.sitemap',
    ),
]

handler403 = error_views.handler403
handler404 = error_views.handler404
handler500 = error_views.handler500


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += [
        path('admin/', admin.site.urls),
        path('rosetta/', include('rosetta.urls')),
        path('__debug__/', include(debug_toolbar.urls)),
    ]
else:
    path('zendo-phi-phi-island-admin/', admin.site.urls),
