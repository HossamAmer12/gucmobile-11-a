from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('backend.views',
    url(r'^api/(?P<orig>(.)+)/(?P<dest>(.)+)/(?P<speed>(.)+)/(?P<who>[\w\-_]+)$', 'api'),
    url(r'^test/(?P<test_value>(.)+)', 'test_method_in_views'),
    url(r'^test_evaluate/(?P<origin>(.)+)/(?P<destination>(.)+)/([a-z]+)/([a-z]+)/$', 'route_blockage'),
    url(r'^directions/(?P<origin>(.)+)/(?P<destination>(.)+)/$', 'directions'),
    url(r'^inRadius/(?P<longitude>(.)+)/(?P<latitude>(.)+)/(?P<radius>(.)+)/$', 'inRadius'),
    url(r'^alternatives/(?P<location>\d+)/(?P<destination>\d+)$', 'alternatives'),
    url(r'^update/(?P<stepId>\d+)/(?P<speed>\d+)/(?P<who>[\w\-_]+)$', 'update'),
    url(r'rate_comment/(?P<who>[\w\-_]+)/(?P<comment_id>\d)/(?P<rate>\d)$', 'rate_comment'),
    url(r'get_comments/(?P<lat>(.)+)/(?P<lng>(.)+)/(?P<refresh_query>(.)+)?$', 'get_comments'),
    url(r'^admin/', include(admin.site.urls)),
)
