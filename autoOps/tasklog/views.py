# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from asset import models
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json,datetime
# Create your views here.
class CustomPaginator(Paginator):
    def __init__(self,current_page, per_pager_num,*args,**kwargs):
        # 当前页
        self.current_page = int(current_page)
        # 最多显示的页码数量 11
        self.per_pager_num = int(per_pager_num)
        super(CustomPaginator,self).__init__(*args,**kwargs)
    def pager_num_range(self):
        # 当前页
        #self.current_page
        # 最多显示的页码数量 11
        #self.per_pager_num
        # 总页数
        # self.num_pages
        if self.num_pages < self.per_pager_num:
            return range(1,self.num_pages+1)
        # 总页数特别多 5
        part = int(self.per_pager_num/2)
        if self.current_page <= part:
            return range(1,self.per_pager_num+1)
        if (self.current_page + part) > self.num_pages:
            return range(self.num_pages-self.per_pager_num+1,self.num_pages+1)
        return range(self.current_page-part,self.current_page+part+1)
@login_required
def all_log(request):
    current_page = request.GET.get('p')
    is_admin = models.UserProfile.objects.values('is_admin').get(email=request.user.email)
    if is_admin['is_admin']:
        log_list = models.TaskJob.objects.all().order_by("-exec_date")
    else:
        log_list = models.TaskJob.objects.filter(exec_user__email=request.user.email).order_by("-exec_date")
    paginator = CustomPaginator(current_page, 7, log_list, 10)
    try:
        # Page对象
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'tasklog/all_log.html', {'posts': posts})

@login_required
@csrf_exempt
def exec_result(request):
    if request.method=='POST':
        resultid=int(request.POST.get('id'))
        result=models.TaskExecResult.objects.filter(jobname_id=resultid)
        result=serializers.serialize('json',result)
    return HttpResponse(result)