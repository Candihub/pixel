from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import urls as auth_urls


urlpatterns = [
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^accounts/',
        include(auth_urls)
    ),
    url(
        r'^',
        include('apps.core.urls', namespace='core')
    ),
    url(
        r'^submission/',
        include('apps.submission.urls', namespace='submission')
    ),
]

if settings.DEBUG:
    import debug_toolbar  # noqa

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
