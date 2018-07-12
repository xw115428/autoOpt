#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from django.conf.urls import include, url
import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'cmdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #批量命令
    url(r'^batch_cmd/', views.batch_cmd,name='batch_cmd'),
    url(r'^batch_cmd_ajax/', views.batch_cmd_ajax,name='batch_cmd_ajax'),
    #软件安装
    url(r'^batch_install/', views.batch_install,name='batch_install'),
    url(r'^batch_install-(\d+)/', views.batch_install_result,name='batch_install_result'),
    url(r'^batch_install_ajax/', views.batch_install_ajax,name='batch_install_ajax'),
    #版本发布
    url(r'^version_update/', views.version_update,name='version_update'),
    #资产收集
    url(r'^get_data/', views.get_data,name='get_data'),
    url(r'^get_data_ajax/', views.get_data_ajax,name="get_data_ajax"),
    url(r'^exec_result/', views.exec_result,name="exec_result"),

    ]