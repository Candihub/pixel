from django.conf.urls import include, url
from viewflow.flow.viewset import FlowViewSet

from . import flows


urlpatterns = [
    url(
        r'^',
        include(FlowViewSet(flows.SubmissionFlow).urls),
    ),
]
