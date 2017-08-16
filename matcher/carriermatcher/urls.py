from django.conf.urls import url

from matcher.carriermatcher import views

urlpatterns = [
    url(r'^$', views.create_matching_request, name='create_matching_request'),
    url(r'^(?P<pk>\d+)/$', views.matching_request_detail, name='matching_request_detail'),
    url(r'^(?P<pk>\d+)/download/$', views.matching_request_download, name='matching_request_download'),
    url(r'^match/$', views.match_company, name='match_company'),
]
