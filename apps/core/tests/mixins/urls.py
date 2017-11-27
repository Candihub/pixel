from django.conf.urls import include, url
from django.contrib.auth import urls as auth_urls

from . import views


urlpatterns = [
    # URLs/Views required for testing
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
    # Test app views
    url(
        r'^foo$',
        views.FooView.as_view(),
        name='foo'
    ),
]
