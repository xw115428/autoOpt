# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import task,json
from config import config
import salt.client
from asset import models
import deny_cmd


####################################批量命令##########################
@login_required
def batch_cmd(request):
    """
    批量命令页面
    :param request:
    :return:
    """
    if request.method=="GET":
        hosts_list=models.Server.objects.filter()
        hostgroups_list = models.HostGroup.objects.all()
        return render(request,'batch_exec/batch_cmd.html',{'hostgroups_list':hostgroups_list,'hosts_list':hosts_list})
@csrf_exempt
@login_required
def batch_cmd_ajax(request):
    """
    批量命令ajax请求
    :param request:
    :return:
    """
    if request.method=='POST':
        cmd=request.POST.get("input_command").split(" ")
        print cmd
        for i in cmd:
            if i in deny_cmd.deny_cmd_list:
                result={'status':False,'data':"命令[%s]在被拒绝列表，请重新输入你要执行的命令 "%i}
                return HttpResponse(json.dumps(result))
        task_obj = task.salt_api(request)
        data = task_obj.handle()
        result = {'status': True, 'data': data}
        return HttpResponse(json.dumps(result))

###############################软件安装###########################
@login_required
def batch_install(request):
    """
    软件安装首页
    :param request:
    :return:
    """
    if request.method=="GET":
        hosts_list=models.Server.objects.filter()
        hostgroups_list = models.HostGroup.objects.all()
        soft_list=config.soft_install
        TaskJob_obj=models.TaskJob.objects.filter(exec_user__email=request.user.email,task_type='exec_sls').order_by("-id")[:5]
        return render(request,'batch_exec/batch_install.html',{'hostgroups_list':hostgroups_list,'hosts_list':hosts_list,"soft_list":soft_list,"TaskJob_obj":TaskJob_obj})

@login_required
def batch_install_result(request,id):
    if request.method == "GET":
        TaskJob_obj=models.TaskJob.objects.get(id=id)
        TaskExecResult_obj=models.TaskExecResult.objects.filter(jobname_id=id)
        return render(request,'batch_exec/batch_install_result.html',{"TaskExecResult_obj":TaskExecResult_obj,"TaskJob_obj":TaskJob_obj})
@csrf_exempt
@login_required
def batch_install_ajax(request):
    """
    软件安装ajax请求
    :param request:
    :return:
    """
    if request.method=='POST':
        task_obj = task.salt_api(request)
        mes={}
        try:
            data = task_obj.handle()
            mes["status"]=True
            mes["result"]=data["task_id"]
        except Exception,e:
            mes["status"] = False
            mes["result"] = e

        return HttpResponse(json.dumps(mes))

# def get_task_result(request):
#     if request.method == 'GET':
#         task_obj_id=request.GET.get("task_id")
#         TaskExecResult_data = models.TaskExecResult.objects.filter(jobname_id=task_obj_id)
#         TaskExecResult_data = serializers.serialize('json', TaskExecResult_data)
#         return HttpResponse(TaskExecResult_data)
############################版本发布###########################33
@login_required
def version_update(request):
    if request.method=="GET":
        file_path_list=config.file_update_dir
        return render(request,"batch_exec/version_update.html",{"file_path_list":file_path_list})

##############################资产收集#########################
@login_required
def get_data(request):
    """
    资产收集页面
    :param request:
    :return:
    """
    if request.method=='GET':
        return render(request,'batch_exec/get_data.html')
@csrf_exempt
@login_required
def get_data_ajax(request):
    """
    资产收集ajax请求
    :param request:
    :return:
    """
    if request.method == 'POST':
        task_obj=task.salt_api(request)
        data=task_obj.handle()
        return HttpResponse(json.dumps({'data':data}))
@csrf_exempt
@login_required
def exec_result(request):
    if request.method=='POST':
        id=request.POST.get("id")
        result=models.TaskExecResult.objects.filter(jobname=id).order_by("exec_hostname")
        result = serializers.serialize('json', result)
        return HttpResponse(result)