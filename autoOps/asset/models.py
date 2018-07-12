#!/usr/bin/env python
#coding:utf-8
from django.db import models
import datetime
# Create your models here.
from myauth import UserProfile

class BusinessUnit(models.Model):
    """
    业务线
    """
    name = models.CharField('业务线', max_length=64, unique=True)
    class Meta:
        verbose_name_plural = "业务线表"
    def __str__(self):
        return self.name
class ChildrenSystem(models.Model):
    """
    子系统
    """
    name=models.CharField('子系统',max_length=64)
    business_unit=models.ForeignKey('BusinessUnit',verbose_name='属于哪一个业务线', null=True, blank=True)
    class Meta:
        verbose_name_plural = "子系统表"
        unique_together = [
            ('name', 'business_unit'),
        ]
    def __str__(self):
        return "%s-%s" %(self.name,self.business_unit)
class HostGroup(models.Model):
    name=models.CharField('组名称',max_length=64,null=True, blank=True,unique=True)
    class Meta:
        verbose_name_plural = "主机组"
    def __str__(self):
        return self.name
class CabinetsColum(models.Model):
    """
    机柜列
    """
    name=models.CharField('机柜列',max_length=32,null=True,blank=True,unique=True)
    class Meta:
        verbose_name_plural = "机柜列"
    def __str__(self):
        return self.name
class CabinetsNum(models.Model):
    """
    机柜号
    """
    name=models.CharField("机柜号",max_length=16,null=True,blank=True)
    cabinet_num=models.ForeignKey('CabinetsColum',verbose_name='属于哪一排机柜', null=True, blank=True)
    class Meta:
        verbose_name_plural = "机柜号"
        unique_together = [
            ('name', 'cabinet_num'),
        ]
    def __str__(self):
        return "%s-%s" %(self.cabinet_num,self.name)
class Asset(models.Model):
    """
    资产信息表，所有资产公共信息（交换机，服务器，防火墙等）
    """
    device_type_choices = (
        ('server', '服务器'),
        ('Switch', '交换机'),
        ('router', '路由器'),
        ('safety', '安全设备'),
        ('store', '储存'),
    )
    device_type_id = models.CharField(choices=device_type_choices,max_length=64, default='server')
    cabinet_num = models.ForeignKey('CabinetsNum', verbose_name='属于哪一个机柜', null=True, blank=True)
    cabinet_order = models.PositiveIntegerField('机柜中的序号',null=True, blank=True)
    guarantee_time=models.CharField('质保期', max_length=64, null=True, blank=True,default="3年")
    buy_date = models.DateField(null=True, blank=True,default=datetime.datetime.strptime("2017-11-01", "%Y-%m-%d"))
    create_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "通用信息表"
    def __str__(self):
        return "%s,%s-%s" % (self.device_type_id,self.cabinet_num, self.cabinet_order)

class Server(models.Model):
    """
    服务器资产信息表
    """
    asset = models.OneToOneField('Asset')
    hostname = models.CharField(max_length=128, unique=True,db_index=True)
    children_system=models.ForeignKey('ChildrenSystem',verbose_name='属于哪一子系统',null=True, blank=True)
    hostgroup = models.ManyToManyField('HostGroup',verbose_name='属于的主机组')
    sn = models.CharField('序列号', max_length=64)
    manufacturer = models.CharField(verbose_name='制造商', max_length=64, null=True, blank=True)
    model = models.CharField('型号', max_length=64, null=True, blank=True)
    manage_ip = models.GenericIPAddressField('管理IP', null=True, blank=True)
    work_ip= models.CharField('业务IP', max_length=128,null=True, blank=True)
    os_platform = models.CharField('系统', max_length=16, null=True, blank=True)
    os_version = models.CharField('系统版本', max_length=16, null=True, blank=True)
    cpu_count = models.IntegerField('CPU总核数', null=True, blank=True)
    cpu_amount = models.IntegerField('CPU数量', null=True, blank=True)
    cpu_model = models.CharField('CPU型号', max_length=128, null=True, blank=True)
    disk_capacity = models.FloatField('磁盘容量GB', null=True, blank=True)
    mem_capacity = models.FloatField('内存容量MB', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True, blank=True)
    class Meta:
        verbose_name_plural = "服务器表"
    def __str__(self):
        return self.hostname

class NetworkDevice(models.Model):
    asset = models.OneToOneField('Asset')
    business_unit = models.ForeignKey('BusinessUnit', verbose_name='属于的业务线', null=True, blank=True)
    management_ip = models.CharField('管理IP', max_length=64, blank=True, null=True)
    vlan_ip = models.CharField('VlanIP', max_length=255, blank=True, null=True)
    intranet_ip = models.CharField('内网IP', max_length=255, blank=True, null=True)
    sn = models.CharField('SN号', max_length=64, unique=True)
    manufacture = models.CharField(verbose_name=u'制造商', max_length=128, null=True, blank=True)
    model = models.CharField('型号', max_length=128, null=True, blank=True)
    port_num = models.SmallIntegerField('端口个数', null=True, blank=True)
    #device_detail = models.CharField('设置详细配置', max_length=255, null=True, blank=True)
    class Meta:
        verbose_name_plural = "网络设备"
    def __str__(self):
        return self.model


class NIC(models.Model):
    """
    网卡信息
    """
    name = models.CharField('网卡名称', max_length=128)
    hwaddr = models.CharField('网卡mac地址', max_length=64)
    netmask = models.CharField(max_length=64)
    ipaddrs = models.CharField('ip地址', max_length=256)
    up = models.BooleanField(default=False)
    server_obj = models.ForeignKey('Server')
    class Meta:
        verbose_name_plural = "网卡表"
    def __str__(self):
        return self.name

class TaskJob(models.Model):
    """
    任务执行记录表，记录所有执行的批量命令
    """
    task_type_choices = (('get_data', "数据采集"), ('exec_cmd', "cmd"), ('exec_sls', "软件部署"))
    task_type = models.CharField(choices=task_type_choices, max_length=50)
    exec_user=models.ForeignKey('UserProfile',max_length=16)
    exec_info=models.CharField(max_length=128,null=True,blank=True)
    exec_date=models.DateTimeField(auto_now_add=True)
    exec_result=models.CharField(max_length=128,null=True,blank=True,default="执行完毕")
    class Meta:
        verbose_name_plural = "任务记录表"
    def __str__(self):
        return self.exec_info

class TaskExecResult(models.Model):
    jobname=models.ForeignKey('TaskJob')
    exec_hostname=models.CharField(max_length=32)
    exec_status_choices=(
        ('false', '失败'),
        ('success', '成功'),
        ('null', '未知'),
    )
    exec_status=models.CharField(choices=exec_status_choices,max_length=32,default='null')
    exec_command=models.CharField(max_length=128,null=True,blank=True)
    exec_result=models.TextField()
    result_date=models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "任务执行结果表"
    def __str__(self):
        return self.exec_hostname
class ErrorLog(models.Model):
    """
    错误日志,如：agent采集数据错误 或 运行错误
    """
    asset_obj = models.ForeignKey('Asset', null=True, blank=True)
    title = models.CharField(max_length=16)
    content = models.TextField()
    create_da = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "错误日志表"
    def __str__(self):
        return self.title

class login_info(models.Model):
    user=models.ForeignKey('UserProfile',null=True,blank=True)
    login_date=models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "登陆日志表"

class user_group(models.Model):
    name=models.CharField(max_length=64,null=True,blank=True)
    group_member=models.ManyToManyField('UserProfile',null=True,blank=True)
    class Meta:
        verbose_name_plural="用户组表"
    def __str__(self):
        return self.name

class group_onemenu_permission(models.Model):
    user_group=models.ManyToManyField('user_group',null=True,blank=True)
    onemenu_name=models.CharField(max_length=128,null=True,blank=True)
    class Meta:
        verbose_name_plural="一级菜单权限"
    def __str__(self):
        return "%s-%s" %(self.user_group.values('name')[0]['name'],self.onemenu_name)


class group_twomenu_permission(models.Model):
    group_onemenu_permission=models.ForeignKey('group_onemenu_permission',null=True,blank=True)
    twomenu_name=models.CharField(max_length=128,null=True,blank=True)
    twomenu_url=models.CharField(max_length=256,null=True,blank=True)
    chioces = ((1, 'GET'), (2, 'POST'))
    per_method = models.SmallIntegerField('请求方法', choices=chioces, default=1)
    class Meta:
        verbose_name_plural="二级菜单权限"
    def __str__(self):
        return '%s-%s' %(self.group_onemenu_permission,self.twomenu_name)

class group_threebutton_permission(models.Model):
    threebutton=models.ManyToManyField('group_twomenu_permission',null=True,blank=True)
    threebutton_name=models.CharField('按钮的名字',max_length=64,null=True,blank=True)
    threebutton_url=models.CharField('按钮id',max_length=16,null=True,blank=True)
    class Meta:
        verbose_name_plural="按钮的权限"

    def __str__(self):
        return '%s-%s-%s-%s' %(self.threebutton.values('group_onemenu_permission__user_group__name')[0]['group_onemenu_permission__user_group__name'],self.threebutton.values('twomenu_name')[0]['twomenu_name'],self.threebutton_name,self.threebutton_url)


