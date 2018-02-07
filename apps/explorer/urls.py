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
        r'^pixelset/(?P<pk>{})/values.json$'.format(UUID_REGEX),
        views.PixelSetDetailValuesView.as_view(),
        name='pixelset_detail_values'
    ),
    url(
        r'^pixelset/(?P<pk>{})/quality-scores.json$'.format(UUID_REGEX),
        views.PixelSetDetailQualityScoresView.as_view(),
        name='pixelset_detail_quality_scores'
    ),
    url(
        r'^pixelset/clear$',
        views.PixelSetClearView.as_view(),
        name='pixelset_clear'
    ),
    url(
        r'^pixelset/deselect$',
        views.PixelSetDeselectView.as_view(),
        name='pixelset_deselect'
    ),
    url(
        r'^pixelset/select$',
        views.PixelSetSelectView.as_view(),
        name='pixelset_select'
    ),
    url(
        r'^pixelset/export$',
        views.PixelSetExportView.as_view(),
        name='pixelset_export'
    ),
    url(
        r'^pixelset/explore$',
        views.PixelSetSelectionView.as_view(),
        name='pixelset_explore'
    ),
    url(
        r'^pixelset/(?P<pk>{})/export$'.format(UUID_REGEX),
        views.PixelSetExportPixelsView.as_view(),
        name='pixelset_export_pixels'
    ),
]
