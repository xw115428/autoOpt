#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from django.conf.urls import include, url
import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'cmdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^all_log/', views.all_log,name='all_log'),
    url(r'^exec_result/', views.exec_result,name='exec_result'),


    ]