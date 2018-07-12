#!/usr/bin/env python
#coding:utf-8
from django.conf.urls import include, url
import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'cmdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^asset_get_choices/', views.asset_get_choices,name='asset_get_choices'),
    url(r'^asset_Cabinets/', views.asset_Cabinets,name='asset_Cabinets'),
    url(r'^asset_get_businessUnit/', views.asset_get_businessUnit,name='asset_get_businessUnit'),
    url(r'^asset_get_hostgroup/', views.asset_get_hostgroup,name='asset_get_hostgroup'),
    url(r'^asset_get_cabinetscolum/', views.asset_get_cabinetscolum,name='asset_get_cabinetscolum'),
    url(r'^asset_get_cabinetsnum/', views.asset_get_cabinetsnum,name='asset_get_cabinetsnum'),
    url(r'^asset_get_chsystem/', views.asset_get_chsystem,name='asset_get_chsystem'),
    url(r'^asset_get_hostname/', views.asset_get_hostname,name='asset_get_hostname'),
    url(r'^asset_get_management_ip/', views.asset_get_management_ip,name='asset_get_management_ip'),
    #业务线管理
    url(r'^asset_businessunit/', views.asset_businessunit,name='asset_businessunit'),
    url(r'^asset_businessunit_add_save/', views.asset_businessunit_add_save,name='asset_businessunit_add_save'),
    url(r'^asset_businessunit_edit_save/', views.asset_businessunit_edit_save,name='asset_businessunit_edit_save'),
    #子系统管理
    url(r'asset_childrensystem/',views.asset_childrensystem,name='asset_childrensystem'),
    url(r'^asset_chsystem_save/', views.asset_chsystem_save,name='asset_chsystem_save'),
    url(r'^asset_chsystem_edit/', views.asset_chsystem_edit,name='asset_chsystem_edit'),
    #服务器管理
    url(r'^asset_server/', views.asset_server,name='asset_server'),
    url(r'^asset_server_edit/', views.asset_server_edit,name='asset_server_edit'),
    url(r'^asset_server_edit_save/', views.asset_server_edit_save,name='asset_server_edit_save'),
    #网络设备管理
    url(r'^asset_network/', views.asset_network,name='asset_network'),
    url(r'^asset_network_edit/', views.asset_network_edit,name='asset_network_edit'),
    url(r'^asset_network_save/', views.asset_network_save,name='asset_network_save'),
    url(r'^asset_export/', views.asset_export,name='asset_export'),

    #主机组管理
    url(r'^asset_hostgroup/', views.asset_hostgroup,name='asset_hostgroup'),
    url(r'^asset_hostgroup_add_save/', views.asset_hostgroup_add_save,name='asset_hostgroup_add_save'),
    url(r'^asset_hostgroup_edit_save/', views.asset_hostgroup_edit_save,name='asset_hostgroup_edit_save'),

    #机柜列管理
    url(r'^asset_cabinetscolum', views.asset_cabinetscolum,name='asset_cabinetscolum'),
    url(r'^asset_cabinetscolum_add_save/', views.asset_cabinetscolum_add_save,name='asset_cabinetscolum_add_save'),
    url(r'^asset_cabinetscolum_edit_save/', views.asset_cabinetscolum_edit_save,name='asset_cabinetscolum_edit_save'),

    #机柜管理
    url(r'asset_cabinetsnum',views.asset_cabinetsnum,name='asset_cabinetsnum'),
    url(r'^asset_cabinets_num_save/', views.asset_cabinets_num_save,name='asset_cabinets_num_save'),
    url(r'^asset_cabinets_num_edit/', views.asset_cabinets_num_edit,name='asset_cabinets_num_edit'),
    ]