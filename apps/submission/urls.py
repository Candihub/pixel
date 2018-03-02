from django.conf.urls import include, url
from viewflow.flow.viewset import FlowViewSet

from . import flows, views


urlpatterns = [
    url(
        r'^(?P<process_pk>\d+)/(?P<task_pk>\d+)/next/$',
        views.NextTaskRedirectView.as_view(),
        name='next_task'
    ),
    url(
        r'^',
        include(FlowViewSet(flows.SubmissionFlow).urls),
    ),
]
