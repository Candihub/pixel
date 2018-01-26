from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^pixelset/$',
        views.PixelSetListView.as_view(),
        name='pixelset_list'
    ),
    url(
        r'^pixelset/export$',
        views.PixelSetExportView.as_view(),
        name='pixelset_export'
    ),
]
