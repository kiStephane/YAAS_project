from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YAAS.views.home', name='home'),

    url(r'^register/$', 'yaasApp.views.register'),
    url(r'^signin/$', 'yaasApp.views.sign_in'),
    url(r'^home/$', 'yaasApp.views.show_home'),
    url(r'^$', 'yaasApp.views.show_home'),




    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
