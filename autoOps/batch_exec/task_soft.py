#!/usr/bin/env python2.7
#coding:utf-8


import os,sys
BaseDir = "/".join( os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
import django
from django.db import transaction
from asset import models
import salt.client
django.setup()

class salt_api(object):
    def __init__(self,request):
        self.request = request
        self.task_type = self.request.POST.get('task_type')
        self.input_command=self.request.POST.get("input_command")
        self.user=request.user.email
        self.local = salt.client.LocalClient()
    def handle(self):
        if self.task_type:
            if hasattr(self,self.task_type):
                func = getattr(self,self.task_type)
                return func()
            else:
                raise TypeError

    @transaction.atomic
    def exec_sls(self):
        mes={}
        #try:
        self.hostname = list(set(self.request.POST.getlist('selected_hosts[]')))
        task_job = models.TaskJob()
        task_job.exec_user = models.UserProfile.objects.get(email=self.user)
        task_job.task_type = self.task_type
        task_job.exec_info = "对主机[%s]安装软件['%s']" % (",".join(self.hostname), self.input_command)
        task_job.save()
        # 开始执行安装任务
        type = 'list'
        cmd="%s.%s"%(self.input_command,self.input_command)
        result_cmd = self.local.cmd_async(self.hostname, 'state.sls', [cmd], tgt_type=type)
        while True:
            if  isinstance(result_cmd, basestring):
                task_job.exec_result="命令执行中"
            else:
                task_job.exec_result = "命令执行完毕"
                #任务执行结果写入TaskExecResult
                for i in result_cmd:
                    models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=i, exec_command=self.input_command,
                                                         exec_result=result_cmd[i])
            break
        #print type(result_cmd)
        return result_cmd
            # 任务执行结果写入TaskExecResult
            # for i in result_cmd:
            #     models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=i, exec_command=self.input_command,
            #                                          exec_result=result_cmd[i])


