# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import collections
import models
import json,StringIO
from capability import zabbix_mysql
from xlwt import *
from my_permission import check_permission

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

def permission(request):
    permission_list=models.group_onemenu_permission.objects.filter(user_group__group_member=request.user)
    # for i in permission_list:
    #     print i.onemenu_name,i.group_twomenu_permission_set.values()
    return permission_list


@login_required
def index(request):
    """
    网站首页
    :param request:
    :return:
    """
    if request.method=='GET':
        print request.user
        permission_list=permission(request)
        cc=zabbix_mysql.zabbix_mysql('10.251.2.27', 'zabbix', '123456', 'zabbix')
        hosts_count=cc.monitor_hosts()[0][0]
        items_count=cc.monitor_items()[0][0]
        service=len(models.Server.objects.all())
        network=len(models.NetworkDevice.objects.all())
        login_info=models.login_info.objects.all().order_by("-login_date")
        result=models.BusinessUnit.objects.all()
        data_dic={}
        for i in result:
            chsystem_obj=models.ChildrenSystem.objects.filter(business_unit=i)
            chsystem_name=models.ChildrenSystem.objects.filter(business_unit=i).values('name')
            network_obj=models.NetworkDevice.objects.filter(business_unit=i)
            data_dic[i]=[chsystem_name,network_obj,[]]
            for cc in chsystem_obj:
                service_obj=models.Server.objects.filter(children_system=cc).values('hostname')
                if service_obj:
                    for service_obj_i in service_obj:
                        data_dic[i][2].append(service_obj_i)
        return render(request,"index.html",{'login_info':login_info,'hosts_count':hosts_count,'items_count':items_count,'service':service,'network':network,'data_dic':data_dic,'permission_list':permission_list})
def acc_login(request):
    """
    登陆页
    :param request:
    :return:
    """
    login_err = ''
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            user=models.UserProfile.objects.get(email=username)
            models.login_info.objects.create(user=user)
            return HttpResponseRedirect('/')
        else:
            login_err = 'username or passwd wrong'
    return render(request, 'login.html', {'login_err': login_err})
@login_required
def acc_logout(request):
    """
    登出
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('login.html')
@csrf_exempt
@login_required
def asset_get_choices(request):
    if request.method=="POST":
        asset_get_choices=models.Asset.device_type_choices
        return HttpResponse(json.dumps(asset_get_choices))
@csrf_exempt
@login_required
def asset_get_businessUnit(request):
    if request.method == "POST":
        asset_get_businessUnit_list=models.BusinessUnit.objects.all()
        asset_get_businessUnit_list=serializers.serialize('json',asset_get_businessUnit_list)
        return HttpResponse(asset_get_businessUnit_list)
@csrf_exempt
@login_required
def asset_get_hostgroup(request):
    if request.method == "POST":
        hostgroup_list=models.HostGroup.objects.all()
        hostgroup_list=serializers.serialize('json',hostgroup_list)
        return HttpResponse(hostgroup_list)
@csrf_exempt
@login_required
def asset_get_cabinetscolum(request):
    if request.method=="POST":
        cabinetscolum_list=models.CabinetsColum.objects.all()
        cabinetscolum_list=serializers.serialize('json',cabinetscolum_list)
        return HttpResponse(cabinetscolum_list)
@csrf_exempt
@login_required
def asset_get_chsystem(request):
    if request.method=="POST":
        id=request.POST.get("data")
        if id:
            BusinessUnit=models.BusinessUnit.objects.get(id=id)
            chsystem_list=models.ChildrenSystem.objects.filter(business_unit=BusinessUnit)
            chsystem_list = serializers.serialize('json', chsystem_list)
        else:
            chsystem_list = [{"model": "", "pk": None, "fields": {"name": "", "cabinet_num": None}}]
        return HttpResponse(chsystem_list)
@csrf_exempt
@login_required
def asset_get_cabinetsnum(request):
    if request.method=="POST":
        id=request.POST.get("data")
        if id:
            CabinetsColum=models.CabinetsColum.objects.get(id=id)
            CabinetsNum_list=models.CabinetsNum.objects.filter(cabinet_num=CabinetsColum)
            CabinetsNum_list = serializers.serialize('json', CabinetsNum_list)
        else:
            CabinetsNum_list=[{"model": "", "pk": None, "fields": {"name": "", "cabinet_num": None}}]
        return HttpResponse(CabinetsNum_list)
@csrf_exempt
@login_required
def asset_get_hostname(request):
    if request.method == "POST":
        hostname_list=models.Server.objects.all()
        hostname_list=serializers.serialize('json',hostname_list)
        return HttpResponse(hostname_list)
@csrf_exempt
@login_required
def asset_get_management_ip(request):
    if request.method == "POST":
        network_list=models.NetworkDevice.objects.all()
        network_list=serializers.serialize('json',network_list)
        return HttpResponse(network_list)
#########################业务线管理##########################
#@check_permission
@login_required
def asset_businessunit(request):
    """
    业务线管理
    :param request:
    :return:
    """
    if request.method=="GET":
        permission_list = permission(request)
        BusinessUnit_list=models.BusinessUnit.objects.all().order_by("id")
        return render(request,'asset/asset_businessunit.html',{'BusinessUnit_list':BusinessUnit_list,'permission_list':permission_list})
@csrf_exempt
@login_required
@transaction.atomic()
def asset_businessunit_add_save(request):
    """
    业务线管理ajax添加数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        name=request.POST.get("name")
        callback={"status":True,"mes":""}
        try:
            models.BusinessUnit.objects.create(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
        return HttpResponse(json.dumps(callback))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_businessunit_edit_save(request):
    """
    业务线管理ajax编辑数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        id=request.POST.getlist("name[]")[0]
        name=request.POST.getlist("name[]")[1]
        callback = {"status": True, "mes": ""}
        try:
            models.BusinessUnit.objects.filter(id=id).update(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
    return HttpResponse(json.dumps(callback))

#######################子系统管理##########################
#@check_permission
@login_required
def asset_childrensystem(request):
    """
    业务线管理
    :param request:
    :return:
    """
    if request.method=="GET":
        current_page = request.GET.get('p')
        permission_list = permission(request)
        if not current_page:
            current_page=1
        ChildrenSystem_list=models.ChildrenSystem.objects.all().order_by("id")
        paginator = CustomPaginator(current_page, 7, ChildrenSystem_list, 10)
        try:
            # Page对象
            posts = paginator.page(current_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(request, 'asset/asset_chsystem.html', {'posts':posts,'permission_list':permission_list})
@csrf_exempt
@login_required
def asset_chsystem_edit(request):
    """
    子系统编辑
    :param request:
    :return:
    """
    if request.method=="POST":
        id = request.POST.get("id")
        chsystem_list=models.ChildrenSystem.objects.filter(id=id).values('name',)
        return HttpResponse(json.dumps(chsystem_list[0]))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_chsystem_save(request):
    """
    子系统信息保存
    :param request:
    :return:
    """

    if request.method=="POST":
        callback = {"status": True, "mes": ""}
        edit_save_list=json.loads(request.POST["data"])
        id=request.POST["id"]
        if id:
            try:
                BusinessUnit_obj=models.BusinessUnit.objects.get(id=edit_save_list["asset__business_unit__name"])
                models.ChildrenSystem.objects.filter(id=id).update(
                    business_unit=BusinessUnit_obj,
                    name=edit_save_list["name"]
                )
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        else:
            try:
                BusinessUnit_obj=models.BusinessUnit.objects.get(id=edit_save_list["asset__business_unit__name"])
                models.ChildrenSystem.objects.create(
                    business_unit=BusinessUnit_obj,
                    name=edit_save_list["name"]
                )
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        return HttpResponse(json.dumps(callback))

##########################机柜列管理########################
#@check_permission
@login_required
def asset_Cabinets(request):
    if request.method=="GET":
        permission_list = permission(request)
        one_list=collections.OrderedDict()
        two_list=collections.OrderedDict()
        three_list=collections.OrderedDict()
        one=models.CabinetsNum.objects.filter(cabinet_num_id=1).all().order_by('name')
        for i in one:
            one_asset=models.Asset.objects.filter(cabinet_num=i).order_by('cabinet_order')
            one_list[i.name]=one_asset
        two=models.CabinetsNum.objects.filter(cabinet_num_id=2).all().order_by('name')
        for i in two:
            two_asset=models.Asset.objects.filter(cabinet_num=i).order_by('cabinet_order')
            two_list[i.name]=two_asset
        three=models.CabinetsNum.objects.filter(cabinet_num_id=3).all().order_by('name')
        for i in three:
            three_asset=models.Asset.objects.filter(cabinet_num=i).order_by('cabinet_order')
            three_list[i.name]=three_asset
        print two_list
        return render(request,'asset/asset_Cabinets.html',{"one_list":one_list,"two_list":two_list,"three_list":three_list,'permission_list':permission_list})
@login_required
def asset_cabinetscolum(request):
    if request.method=="GET":
        permission_list = permission(request)
        CabinetsColum_list=models.CabinetsColum.objects.all()
        return render(request,"asset/asset_cabinetscolum.html",{"CabinetsColum_list":CabinetsColum_list,'permission_list':permission_list})
@csrf_exempt
@login_required
@transaction.atomic()
def asset_cabinetscolum_add_save(request):
    """
    机柜列管理ajax添加数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        name=request.POST.get("name")
        callback={"status":True,"mes":""}
        try:
            models.CabinetsColum.objects.create(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
        return HttpResponse(json.dumps(callback))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_cabinetscolum_edit_save(request):
    """
    机柜列管理ajax编辑数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        id=request.POST.getlist("name[]")[0]
        name=request.POST.getlist("name[]")[1]
        callback = {"status": True, "mes": ""}
        try:
            models.CabinetsColum.objects.filter(id=id).update(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
    return HttpResponse(json.dumps(callback))

########################机柜管理###########################
#@check_permission
@login_required
def asset_cabinetsnum(request):
    """
    机柜管理
    :param request:
    :return:
    """
    if request.method=="GET":
        permission_list = permission(request)
        current_page = request.GET.get('p')
        if not current_page:
            current_page=1
        CabinetsNum_list=models.CabinetsNum.objects.all().order_by("id")
        paginator = CustomPaginator(current_page, 7, CabinetsNum_list, 10)
        try:
            # Page对象
            posts = paginator.page(current_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'asset/asset_cabinetsnum.html', {'posts':posts,'permission_list':permission_list})
@csrf_exempt
@login_required
def asset_cabinets_num_edit(request):
    """
    子系统编辑
    :param request:
    :return:
    """
    if request.method=="POST":
        id = request.POST.get("id")
        chsystem_list=models.CabinetsNum.objects.filter(id=id).values('name',)
        return HttpResponse(json.dumps(chsystem_list[0]))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_cabinets_num_save(request):
    """
    机柜管理保存
    :param request:
    :return:
    """
    if request.method=="POST":
        callback = {"status": True, "mes": ""}
        edit_save_list=json.loads(request.POST["data"])
        id=request.POST["id"]
        CabinetsColum_obj = models.CabinetsColum.objects.get(id=edit_save_list["cabinets_num_cabinet_num"])
        if id:
            try:
                models.CabinetsNum.objects.filter(id=id).update(
                    cabinet_num=CabinetsColum_obj,
                    name=edit_save_list["name"]
                )
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        else:
            try:
                models.CabinetsNum.objects.create(
                    cabinet_num=CabinetsColum_obj,
                    name=edit_save_list["name"]
                )
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        return HttpResponse(json.dumps(callback))
######################服务器管理===========================
#@check_permission
@login_required
def asset_server(request):
    """
    服务器管理
    :param request:
    :return:
    """
    if request.method=="GET":
        permission_list = permission(request)
        business_unit=request.GET.get("business_unit")
        hostname=request.GET.get("hostname")
        current_page = request.GET.get('p')
        if not current_page:
            current_page=1
        if hostname:
            server_list = models.Server.objects.filter(id=hostname)
            paginator = CustomPaginator(current_page, 7, server_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request, "asset/asset_server.html", {"posts": posts,"hostname": hostname,'permission_list':permission_list})
        elif business_unit:
            server_list=models.Server.objects.filter(children_system__business_unit_id=business_unit)
            paginator = CustomPaginator(current_page, 7, server_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request, "asset/asset_server.html", {"posts": posts, "business_unit": business_unit,'permission_list':permission_list})
        else:
            server_list=models.Server.objects.all().order_by("id")
            for i in server_list:

                print i.hostgroup.values('name')
            paginator = CustomPaginator(current_page, 7, server_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request,"asset/asset_server.html",{"posts":posts,'permission_list':permission_list})
@csrf_exempt
@login_required
def asset_server_edit(request):
    """
    服务器管理编辑，获取主机组列表
    :param request:
    :return:
    """
    if request.method=="POST":
        id=request.POST.get("id")
        Server_list=models.Server.objects.filter(id=id).values(
            "asset__cabinet_order",
            "asset__guarantee_time",
            "asset__buy_date",
            "hostname",
            "sn",
            "manufacturer",
            "model",
            "manage_ip",
            "work_ip",
            "os_platform",
            "os_version",
            "cpu_count",
            "cpu_amount",
            "cpu_model",
            "disk_capacity",
            "mem_capacity",
        )
        a=Server_list[0]["asset__buy_date"].strftime('%Y-%m-%d')
        Server_list=Server_list[0]
        Server_list["asset__buy_date"]=a
        return HttpResponse(json.dumps(Server_list))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_server_edit_save(request):
    """
    服务器信息保存
    :param request:
    :return:
    """

    if request.method=="POST":
        callback = {"status": True, "mes": ""}
        edit_save_list=json.loads(request.POST["data"])
        print edit_save_list
        id=request.POST["id"]
        if id:
            try:
                ChildrenSystem_obj = models.ChildrenSystem.objects.get(id=edit_save_list["server__children_system__name"])
                CabinetsNum_obj = models.CabinetsNum.objects.get(id=edit_save_list["asset__cabinet_num"])
                asset_id=models.Server.objects.filter(id=id).values("asset_id")[0]["asset_id"]
                models.Asset.objects.filter(id=asset_id).update(
                    device_type_id = edit_save_list["asset__device_type_id"],
                    cabinet_num = CabinetsNum_obj,
                    cabinet_order = int(edit_save_list["asset__cabinet_order"]),
                    buy_date = edit_save_list["asset__buy_date"],
                )
                models.Server.objects.filter(id=id).update(
                    hostname=edit_save_list["hostname"],
                    children_system=ChildrenSystem_obj,
                    sn=edit_save_list["sn"],
                    manufacturer=edit_save_list["manufacturer"],
                    model=edit_save_list["model"],
                    manage_ip=edit_save_list["manage_ip"],
                    work_ip=edit_save_list["work_ip"],
                    os_platform=edit_save_list["os_platform"],
                    os_version=edit_save_list["os_version"],
                    cpu_count=edit_save_list["cpu_count"],
                    cpu_amount=edit_save_list["cpu_amount"],
                    cpu_model=edit_save_list["cpu_model"],
                    disk_capacity=edit_save_list["disk_capacity"],
                    mem_capacity=edit_save_list["mem_capacity"],
                )
                for i in edit_save_list["hostgroup__name"]:
                    i_HostGroup_obj = models.HostGroup.objects.get(id=i)
                    models.Server.objects.get(id=id).hostgroup.add(i_HostGroup_obj)
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        else:
            try:
                ChildrenSystem_obj = models.ChildrenSystem.objects.get(id=edit_save_list["server__children_system__name"])
                CabinetsNum_obj=models.CabinetsNum.objects.get(id=edit_save_list["asset__cabinet_num"])
                Asset_obj=models.Asset()
                Asset_obj.device_type_id = edit_save_list["asset__device_type_id"]
                Asset_obj.cabinet_num=CabinetsNum_obj
                Asset_obj.cabinet_order=int(edit_save_list["asset__cabinet_order"])
                Asset_obj.buy_date=edit_save_list["asset__buy_date"]
                Asset_obj.save()
                Server_obj=models.Server.objects.create(
                    asset=Asset_obj,
                    hostname=edit_save_list["hostname"],
                    children_system=ChildrenSystem_obj,
                    sn=edit_save_list["sn"],
                    manufacturer=edit_save_list["manufacturer"],
                    model=edit_save_list["model"],
                    manage_ip=edit_save_list["manage_ip"],
                    work_ip=edit_save_list["work_ip"],
                    os_platform=edit_save_list["os_platform"],
                    os_version=edit_save_list["os_version"],
                    cpu_count=edit_save_list["cpu_count"],
                    cpu_amount=edit_save_list["cpu_amount"],
                    cpu_model=edit_save_list["cpu_model"],
                    disk_capacity=edit_save_list["disk_capacity"],
                    mem_capacity=edit_save_list["mem_capacity"],
                )
                for i in edit_save_list["hostgroup__name"]:
                    i_HostGroup_obj = models.HostGroup.objects.get(id=i)
                    Server_obj.hostgroup.add(i_HostGroup_obj)
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        return HttpResponse(json.dumps(callback))

#################################网络设备管理#############################
#@check_permission
@login_required
def asset_network(request):
    """
    网络设备管理
    :param request:
    :return:
    """
    if request.method=="GET":
        current_page = request.GET.get('p')
        business_unit = request.GET.get("business_unit")
        management_ip = request.GET.get("management_ip")
        permission_list=permission(request)

        if not current_page:
            current_page=1
        if management_ip:
            network_list=models.NetworkDevice.objects.filter(id=management_ip)
            paginator = CustomPaginator(current_page, 7, network_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request,"asset/asset_network.html",{"posts":posts,"management_ip":management_ip,"business_unit":business_unit,'permission_list':permission_list})
        elif business_unit:
            network_list = models.NetworkDevice.objects.filter(business_unit_id=business_unit)
            paginator = CustomPaginator(current_page, 7, network_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request, "asset/asset_network.html",{"posts": posts, "management_ip": management_ip, "business_unit": business_unit,'permission_list':permission_list})
        else:
            network_list = models.NetworkDevice.objects.all()
            paginator = CustomPaginator(current_page, 7, network_list, 10)
            try:
                # Page对象
                posts = paginator.page(current_page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return render(request, "asset/asset_network.html",{"posts": posts, "management_ip": management_ip, "business_unit": business_unit,'permission_list':permission_list})
@csrf_exempt
@login_required
def asset_network_edit(request):
    """
    网络设备管理编辑
    :param request:
    :return:
    """
    if request.method=="POST":
        id=request.POST.get("id")
        network_list=models.NetworkDevice.objects.filter(id=id).values(
            "asset__cabinet_order",
            "asset__guarantee_time",
            "asset__buy_date",
            "sn",
            "manufacture",
            "model",
            "management_ip",
            "vlan_ip",
            "intranet_ip",
            "port_num",
        )
        a=network_list[0]["asset__buy_date"].strftime('%Y-%m-%d')
        network_list=network_list[0]
        network_list["asset__buy_date"]=a
        return HttpResponse(json.dumps(network_list))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_network_save(request):
    """
    网络设备保存
    :param request:
    :return:
    """
    if request.method=="POST":
        callback = {"status": True, "mes": ""}
        edit_save_list=json.loads(request.POST["data"])
        id=request.POST["id"]
        print id
        if id:
            try:
                BusinessUnit_obj=models.BusinessUnit.objects.get(id=edit_save_list["business_unit__name"])
                CabinetsNum_obj = models.CabinetsNum.objects.get(id=edit_save_list["asset__cabinet_num"])
                asset_id=models.NetworkDevice.objects.filter(id=id).values("asset_id")[0]["asset_id"]
                models.Asset.objects.filter(id=asset_id).update(
                    device_type_id = edit_save_list["asset__device_type_id"],
                    cabinet_num = CabinetsNum_obj,
                    cabinet_order = int(edit_save_list["asset__cabinet_order"]),
                    buy_date = edit_save_list["asset__buy_date"],
                )
                models.NetworkDevice.objects.filter(id=id).update(
                    business_unit=BusinessUnit_obj,
                    management_ip=edit_save_list["management_ip"],
                    vlan_ip=edit_save_list["vlan_ip"],
                    intranet_ip=edit_save_list["intranet_ip"],
                    sn=edit_save_list["sn"],
                    manufacture=edit_save_list["manufacture"],
                    model=edit_save_list["model"],
                    port_num=edit_save_list["port_num"]
                )
            except Exception,e:
                callback["status"]=False
                callback["mes"]=str(e)
        else:
            try:
                BusinessUnit_obj = models.BusinessUnit.objects.get(id=edit_save_list["business_unit__name"])
                CabinetsNum_obj = models.CabinetsNum.objects.get(id=edit_save_list["asset__cabinet_num"])
                Asset_obj = models.Asset()
                Asset_obj.device_type_id = edit_save_list["asset__device_type_id"]
                Asset_obj.cabinet_num = CabinetsNum_obj
                Asset_obj.cabinet_order = int(edit_save_list["asset__cabinet_order"])
                Asset_obj.buy_date = edit_save_list["asset__buy_date"]
                Asset_obj.save()
                models.NetworkDevice.objects.create(
                    asset=Asset_obj,
                    business_unit=BusinessUnit_obj,
                    management_ip=edit_save_list["management_ip"],
                    vlan_ip=edit_save_list["vlan_ip"],
                    intranet_ip=edit_save_list["intranet_ip"],
                    sn=edit_save_list["sn"],
                    manufacture=edit_save_list["manufacture"],
                    model=edit_save_list["model"],
                    port_num=edit_save_list["port_num"],
                )
            except Exception, e:
                callback["status"] = False
                callback["mes"] = str(e)
        return HttpResponse(json.dumps(callback))
@csrf_exempt
@login_required
def asset_export(request):
    """
    表格导出
    :param request:
    :return:
    """
    network_list = models.NetworkDevice.objects.all().order_by('id')
    server_list=models.Server.objects.all().order_by('id')
    if network_list or server_list:
        # 创建工作薄
        ws = Workbook(encoding='utf-8')
        w = ws.add_sheet(u"网络设备报表")
        w.write(0, 0, "id")
        w.write(0, 1, u"业务线")
        w.write(0, 2, u"设备类型")
        w.write(0, 3, u"机柜列")
        w.write(0, 4, u"机柜号")
        w.write(0, 5, u"机柜中序号")
        w.write(0, 6, u"序列号")
        w.write(0, 7, u"厂商")
        w.write(0, 8, u"型号")
        w.write(0, 9, u"管理IP")
        w.write(0, 10, u"VlanIP")
        w.write(0, 11, u"内网IP")
        w.write(0, 12, u"端口个数")
        w.write(0, 13, u"购买时间")
        w.write(0, 14, u"质保期")

        # 写入数据

        excel_row = 1
        for obj in network_list:
            w.write(excel_row, 0, obj.id)
            w.write(excel_row, 1, obj.business_unit.name)
            w.write(excel_row, 2, obj.asset.get_device_type_id_display())
            w.write(excel_row, 3, obj.asset.cabinet_num.cabinet_num.name)
            w.write(excel_row, 4, obj.asset.cabinet_num.name)
            w.write(excel_row, 5, obj.asset.cabinet_order)
            w.write(excel_row, 6, obj.sn)
            w.write(excel_row, 7, obj.manufacture)
            w.write(excel_row, 8, obj.model)
            w.write(excel_row, 9, obj.management_ip)
            w.write(excel_row, 10, obj.vlan_ip)
            w.write(excel_row, 11, obj.intranet_ip)
            w.write(excel_row, 12, obj.port_num)
            w.write(excel_row, 13, obj.asset.buy_date)
            w.write(excel_row, 14, obj.asset.guarantee_time)
            excel_row += 1

        w1 = ws.add_sheet(u"服务器报表",cell_overwrite_ok=True)
        w1.write(0, 0, "id")
        w1.write(0, 1, u"业务线")
        w1.write(0, 2, u"子系统")
        w1.write(0, 3, u"设备类型")
        w1.write(0, 4, u"机柜列")
        w1.write(0, 5, u"机柜号")
        w1.write(0, 6, u"机柜中序号")
        w1.write(0, 7, u"主机名")
        w1.write(0, 8, u"主机组")
        w1.write(0, 9, u"序列号")
        w1.write(0, 10, u"厂商")
        w1.write(0, 11, u"型号")
        w1.write(0, 12, u"管理IP")
        w1.write(0, 13, u"业务IP")
        w1.write(0, 14, u"系统")
        w1.write(0, 15, u"CPU总核数")
        w1.write(0, 16, u"CPU数量")
        w1.write(0, 17, u"CPU型号")
        w1.write(0, 18, u"磁盘容量GB")
        w1.write(0, 19, u"内存容量MB")
        excel_row1 = 1
        for obj in server_list:
            w1.write(excel_row1, 0, obj.id)
            w1.write(excel_row1, 1, obj.children_system.business_unit.name)
            w1.write(excel_row1, 2, obj.children_system.name)
            w1.write(excel_row1, 3, obj.asset.get_device_type_id_display())
            w1.write(excel_row1, 4, obj.asset.cabinet_num.cabinet_num.name)
            w1.write(excel_row1, 5, obj.asset.cabinet_num.name)
            w1.write(excel_row1, 6, obj.asset.cabinet_order)
            w1.write(excel_row1, 7, obj.hostname)
            w1.write(excel_row1, 8, obj.hostgroup.name)
            w1.write(excel_row1, 9, obj.sn)
            w1.write(excel_row1, 10, obj.manufacturer)
            w1.write(excel_row1, 11, obj.model)
            w1.write(excel_row1, 12, obj.manage_ip)
            w1.write(excel_row1, 13, obj.work_ip)
            w1.write(excel_row1, 14, obj.os_platform)
            w1.write(excel_row1, 15, obj.cpu_count)
            w1.write(excel_row1, 16, obj.cpu_amount)
            w1.write(excel_row1, 17, obj.cpu_model)
            w1.write(excel_row1, 18, obj.disk_capacity)
            w1.write(excel_row1, 19, obj.mem_capacity)
            excel_row1 += 1
            # 检测文件是够存在
        # 方框中代码是保存本地文件使用，如不需要请删除该代码
        ###########################
        # file_name=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        # file_name='%s_%s.xls'%(request.user.email,file_name)
        # export_file = "/tmp/%s"%file_name
        # print export_file
        # ws.save(export_file)
        ############################

        sio = StringIO.StringIO()
        ws.save(sio)
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        # response['Content-Disposition'] = 'attachment; filename=%s'%file_name
        response['Content-Disposition'] = 'attachment;'
        response.write(sio.getvalue())
        return response


##################################主机组管理#################################
#@check_permission
@login_required
def asset_hostgroup(request):
    """
    主机组管理
    :param request:
    :return:
    """
    if request.method=="GET":
        HostGroup_list = models.HostGroup.objects.all().order_by("id")
        return render(request, 'asset/asset_hostgroup.html', {'HostGroup_list': HostGroup_list})
@csrf_exempt
@login_required
@transaction.atomic()
def asset_hostgroup_add_save(request):
    """
    业务线管理ajax添加数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        name=request.POST.get("name")
        callback={"status":True,"mes":""}
        try:
            models.HostGroup.objects.create(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
        return HttpResponse(json.dumps(callback))
@csrf_exempt
@login_required
@transaction.atomic()
def asset_hostgroup_edit_save(request):
    """
    业务线管理ajax编辑数据保存
    :param request:
    :return:
    """
    if request.method=="POST":
        id=request.POST.getlist("name[]")[0]
        name=request.POST.getlist("name[]")[1]
        callback = {"status": True, "mes": ""}
        try:
            models.HostGroup.objects.filter(id=id).update(name=name)
        except Exception,e:
            callback["status"]=False
            callback["mes"]=e
    return HttpResponse(json.dumps(callback))