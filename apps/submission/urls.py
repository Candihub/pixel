from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^download/$', views.DownloadXLSXTemplateView.as_view(), name='download'),
    url(r'^download/template$', views.GenerateXLSXTemplateView.as_view(), name='generate_template'),
]
