#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from django.conf.urls import include, url
import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'cmdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'^graphs/', views.graphs,name='graphs'),
    url(r'^report_forms/', views.report_forms,name='report_forms'),
    url(r'^database_forms/', views.database_forms,name='database_forms'),
    url(r'^index_data/', views.index_data,name='index_data'),
    url(r'^monitor_data/', views.monitor_data,name='monitor_data'),
    url(r'^report_froms_post/', views.report_froms_post,name='report_froms_post'),
    url(r'^database_search_post/', views.database_search_post,name='database_search_post'),

    ]