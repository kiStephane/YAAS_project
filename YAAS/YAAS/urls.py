from django.conf.urls import patterns, include, url
from django.contrib import admin
from yaasApp.rest_views import auction_search_api

from yaasApp.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YAAS.views.home', name='home'),

    url(r'^register/$', register),

    url(r'^signin/$', sign_in),

    url(r'^logout/$', sign_out),

    url(r'^home/$', show_home),

    url(r'^$', show_home),

    url(r'^profile/$', show_profile),

    url(r'^editprofile/$', edit_profile),

    url(r'^changepassword/$', change_password),

    url(r'^createauction/$', create_auction),

    url(r'^saveauction/$', save_auction),

    url(r'^editauction/(?P<a_id>\d+)$', edit_auction),

    url(r'^banauction/(?P<a_id>\d+)$', ban_auction),

    url(r'^auction/(?P<a_id>\d+)$', show_auction),

    url(r'^createbid/(?P<a_id>\d+)$', create_bid),

    url(r'^savebid/$', save_bid),

    url(r'^search/$', search),

    url(r'^api/search/(\d{1,3})$', api_search), #TODO Delete that URL

    url(r'^api/v1/search/$', auction_search_api),

    url(r'^results/$', search_result_pagination),

    url(r'^selectlang/(?P<lang>\w+)$', select_lang),


    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
