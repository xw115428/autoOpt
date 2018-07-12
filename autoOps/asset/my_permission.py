#!/usr/bin/env python
#coding:utf-8
from django.shortcuts import render
from asset import models
from django.db.models import Q
from django.core.urlresolvers import resolve

def perm_check(request, *args, **kwargs):
    url_obj = resolve(request.path_info)
    url_name = url_obj.url_name
    perm_name = ''
    #权限必须和urlname配合使得
    if url_name:
        #获取请求方法，和请求参数
        url_method = request.method
        #操作数据库
        get_perm = models.group_twomenu_permission.objects.filter(Q(twomenu_url=url_name),Q(per_method=1))
        if get_perm:
            for i in get_perm:
                perm_name = i.twomenu_name
                perm_str = 'asset.%s' % perm_name
                if request.user.has_perm(perm_str):
                    return True
            else:
                return False
        else:
            return False
    else:
        return False   #没有权限设置，默认不放过

def check_permission(fun):    #定义一个装饰器，在views中应用
    def wapper(request, *args, **kwargs):
        if perm_check(request, *args, **kwargs):  #调用上面的权限验证方法
            return fun(request, *args, **kwargs)
        return render(request, '403.html', locals())
    return wapper