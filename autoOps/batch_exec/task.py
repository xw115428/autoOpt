#!/usr/bin/env python2.7
#coding:utf-8


import os,sys
# BaseDir = "/".join( os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])
reload(sys)
sys.setdefaultencoding('utf8')

# sys.path.append(BaseDir)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
# import django
from django.db import transaction
from asset import models
from django.core.exceptions import ObjectDoesNotExist
import salt.client
import subprocess
from autoOps import settings

# django.setup()

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
    def get_data(self):
        """
        根据传过来的hostname列表，进行系统信息收集
        """
        self.hostname = self.request.POST.get('task_hosts')
        self.hostname=self.hostname.split(",")
        print self.hostname
        mes={}
        try:
            data={}
            #采集任务入库
            task_job=models.TaskJob()
            task_job.exec_user=models.UserProfile.objects.get(email=self.user)
            task_job.task_type=self.task_type
            if self.hostname[0]:
                type='list'
                task_job.exec_info='salt -L %s,"grains.items"'%self.hostname
                task_job.save()
                grains=self.local.cmd(self.hostname,"grains.items",timeout=1,tgt_type=type)
                diskusage = self.local.cmd(self.hostname, "disk.usage",timeout=1,tgt_type=type)

                if not grains:
                    # mes['taskjob_id'] = task_job.id
                    for i in self.hostname:
                        grains[i]="Minion did not return. [No response]"
                        diskusage[i]="Minion did not return. [No response]"
            else:
                task_job.exec_info = 'salt "*","grains.items"'
                task_job.save()
                grains = self.local.cmd('*', "grains.items")
                diskusage = self.local.cmd('*', "disk.usage")

            #采集任务写入审计表

            for i in grains:
                if isinstance(grains[i],dict):
                    models.TaskExecResult.objects.create(jobname=task_job,exec_hostname=i,exec_command="grains.items",exec_result="True")
                else:
                    models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=i,exec_command="grains.items", exec_result=str(grains[i]))
            for disk in diskusage:
                if isinstance(diskusage[disk],dict):
                    models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=disk,exec_command="disk.usage",exec_result="True")
                else:
                    models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=disk,exec_command="disk.usage", exec_result=str(diskusage[disk]))

            data['grains']=grains
            data['disk']=diskusage
            self.data_save(data)

            mes["status"] = True
            mes['taskjob_id']=task_job.id
        except Exception, e:
            mes["status"] = False
            mes["mes"] = str(e)
            mes['taskjob_id'] = task_job.id
        return mes
    def exec_cmd(self):
        #执行命令任务写入TASKJOB
        mes={}
        try:
            self.hostname = list(set(self.request.POST.getlist('selected_hosts[]')))
            cmd_data='self.hostname, "cmd.run","[%s]", timeout=1, tgt_type=type'%self.input_command

            task_job = models.TaskJob()
            task_job.exec_user = models.UserProfile.objects.get(email=self.user)
            task_job.task_type = self.task_type
            task_job.exec_info = "对主机[%s]执行命令['%s']"%(",".join(self.hostname),self.input_command)
            task_job.save()
            #开始执行批量任务
            type = 'list'
            result_cmd = self.local.cmd(self.hostname,'cmd.run',[self.input_command],tgt_type=type)
            #任务执行结果写入TaskExecResult
            for i in result_cmd:
                models.TaskExecResult.objects.create(jobname=task_job, exec_hostname=i, exec_command=self.input_command,
                                                         exec_result=result_cmd[i])
        except Exception,e:
            mes["status"] = False
            mes["mes"] = str(e)
            mes["result_cmd"]=None
        else:
            if result_cmd:
                mes["status"] = True
                mes["mes"] = "任务执行成功"
                mes["result_cmd"]=result_cmd
            else:
                mes["status"] = False
                mes["mes"] = "No minions matched the target. No command was sent, no jid was assigned."
                mes["result_cmd"] = None
        return mes
    def data_save(self,data):
        """
        讲收集到的系统信息数据处理后写入数据库
        """
        data_dict = {}
        for i in data['grains']:
            if not isinstance(data['grains'][i], dict):
                continue
            data_dict[i] = {}
            #print data['grains'][i]['host']
            data_dict[i]['hostname'] = data['grains'][i]['host']
            data_dict[i]['sn'] = data['grains'][i]['serialnumber']
            data_dict[i]['manufacturer'] = data['grains'][i]['manufacturer']
            data_dict[i]['model'] = data['grains'][i]['productname']
            data_dict[i]['work_ip'] = data['grains'][i]['ipv4']
            data_dict[i]['os_platform'] = data['grains'][i]['os']
            data_dict[i]['os_version'] = data['grains'][i]['osrelease_info']
            data_dict[i]['cpu_count'] = data['grains'][i]['num_cpus']
            data_dict[i]['cpu_model'] = data['grains'][i]['cpu_model']
            data_dict[i]['mem_capacity'] = data['grains'][i]['mem_total']
        for i in data['disk']:
            if not isinstance(data['disk'][i], dict):
                continue
            disk_count = 0
            for disk in data['disk'][i]:
                if not data['disk'][i][disk]['1K-blocks']:
                    continue
                disk_count += int(data['disk'][i][disk]['1K-blocks'])
            data_dict[i]['disk_capacity'] = disk_count / 1024 / 1024
        for i in data_dict:
            obj_update=models.Server.objects.filter(hostname=data_dict[i]['hostname'])
            if obj_update:
                obj_update.update(sn=data_dict[i]['sn'])
                obj_update.update(manufacturer=data_dict[i]['manufacturer'])
                obj_update.update(model=data_dict[i]['model'])
                obj_update.update(work_ip=data_dict[i]['work_ip'])
                obj_update.update(os_platform=data_dict[i]['os_platform'])
                obj_update.update(os_version=data_dict[i]['os_version'])
                obj_update.update(cpu_count=data_dict[i]['cpu_count'])
                obj_update.update(cpu_model=data_dict[i]['cpu_model'])
                obj_update.update(mem_capacity=data_dict[i]['mem_capacity'])
                obj_update.update(disk_capacity=data_dict[i]['disk_capacity'])
            else:
                obj=models.Server()
                obj.hostname=data_dict[i]['hostname']
                obj.sn=data_dict[i]['sn']
                obj.manufacturer=data_dict[i]['manufacturer']
                obj.model=data_dict[i]['model']
                obj.work_ip=data_dict[i]['work_ip']
                obj.os_platform=data_dict[i]['os_platform']
                obj.os_version=data_dict[i]['os_version']
                obj.cpu_count=data_dict[i]['cpu_count']
                obj.cpu_model=data_dict[i]['cpu_model']
                obj.mem_capacity=data_dict[i]['mem_capacity']
                obj.disk_capacity=data_dict[i]['disk_capacity']
                obj_asset=models.Asset.objects.create(device_type_id='server')
                obj.asset=obj_asset
                obj.save()

    @transaction.atomic
    def exec_sls(self):
        mes={}
        #try:
        self.hostname = list(set(self.request.POST.getlist('selected_hosts[]')))
        #安装日志写入TaskJob表
        task_job = models.TaskJob()
        task_job.exec_user = models.UserProfile.objects.get(email=self.user)
        task_job.task_type = self.task_type
        task_job.exec_info = "对主机[%s]安装软件['%s']" % (",".join(self.hostname), self.input_command)
        task_job.save()
        #预写入详细安装记录表
        for i in self.hostname:
            TaskExecResult_obj=models.TaskExecResult(
                jobname=task_job,
                exec_hostname=i,
                exec_result="任务执行中"
            )
            TaskExecResult_obj.save()
        # 开始执行安装任务
        cmd="%s.%s"%(self.input_command,self.input_command)
        p = subprocess.Popen([
            'python',
            settings.MultiTaskScript,
            str(task_job.id),
            ",".join(self.hostname),
            cmd
        ], preexec_fn=os.setsid)
        return {'task_id': task_job.id}


