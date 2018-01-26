from django.conf.urls import url

from . import views

UUID_REGEX = (
    '[a-f0-9]{8}-?'
    '[a-f0-9]{4}-?'
    '4[a-f0-9]{3}-?'
    '[89ab][a-f0-9]{3}-?'
    '[a-f0-9]{12}'
)

urlpatterns = [
    url(
        r'^pixelset/$',
        views.PixelSetListView.as_view(),
        name='pixelset_list'
    ),
    url(
        r'^pixelset/(?P<pk>{})/$'.format(UUID_REGEX),
        views.PixelSetDetailView.as_view(),
        name='pixelset_detail'
    ),
    url(
        r'^pixelset/export$',
        views.PixelSetExportView.as_view(),
        name='pixelset_export'
    ),
]
