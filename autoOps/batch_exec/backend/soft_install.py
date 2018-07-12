#!/usr/bin/env python
#coding:utf-8
import os,sys

BaseDir = "/".join( os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
print BaseDir
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autoOps.settings")
import django
import time
from django.core.exceptions import ObjectDoesNotExist
import salt.client
from django.utils import timezone
django.setup() #allow outsider scripts invoke django db models

from asset import models
def salt_install(task_id,hostname,cmd):
    try:
        type="list"
        local = salt.client.LocalClient()
        result_cmd = local.cmd(hostname, 'state.sls', [cmd], tgt_type=type)
        print result_cmd
        for k,v in result_cmd.items():
            if v:
                if not isinstance(v,dict):
                    result_cmd[k]=["false",v]
                else:
                    for i in v:
                        if v[i]["result"]:
                            result_cmd[k]=["success","安装成功"]
                        else:
                            result_cmd[k] = ["false",v[i]["changes"]["stderr"]]
            else:
                result_cmd[k]=["false","No minions matched the target. No command was sent, no jid was assigned."]
        print result_cmd
        for k,v in result_cmd.items():
            models.TaskExecResult.objects.filter(jobname_id=task_id,exec_hostname=k).update(
                exec_status=v[0],
                exec_result=v[1],
                result_date=timezone.now()
            )

    except Exception,e:
        print e
if __name__=='__main__':
    if len(sys.argv) != 4:
        sys.exit("4 arguments expected but %s given" % len(sys.argv))
    hostname=sys.argv[2].split(",")
    salt_install(sys.argv[1],hostname,sys.argv[3])