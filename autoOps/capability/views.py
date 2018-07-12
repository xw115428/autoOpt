# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import zabbix_mysql
import conn_oracle
# Create your views here.
@login_required
def graphs(request):
    """
    曲线图
    :param request:
    :return:
    """
    return render(request,'capability/graphs.html')
@login_required
def report_forms(request):
    """
    报表
    :param request:
    :return:
    """
    if request.method=='GET':
        result = zabbix_mysql.zabbix_mysql('10.251.2.27', 'zabbix', '123456', 'zabbix')
        result_hosts = result.host_list()
        return render(request,'capability/report_forms.html',{"result_hosts":result_hosts})
@csrf_exempt
@login_required
def report_froms_post(request):
    """
    性能统计-报表，ajax获取数据方法
    :param request:
    :return:
    """
    if request.method=='POST':
        values=request.POST.getlist("data[]")
        host=values[0]
        key=values[1]
        start_time=values[2]
        stop_time=values[3]
        try:
            p=int(values[4])
        except IndexError:
            p=1
        if  start_time:
            start_time = "and date_format(from_unixtime(e.clock),'%Y-%m-%d')>='" + start_time + "'"
        if  stop_time:
            stop_time = "and date_format(from_unixtime(e.clock),'%Y-%m-%d')<='" + stop_time + "'"
        if  key:
            key="and d.key_='"+key+"'"
        else:
            key="and d.key_ in ('system.cpu.util[,,avg5]','vm.memory.size[pused]')"
        if host:
            host= "and c.host='"+host+"'"
        result = zabbix_mysql.zabbix_mysql('10.251.2.27', 'zabbix', '123456', 'zabbix',start_time,stop_time)
        data=result.froms_data(key,host)
        # 定义页面显示几页
        dis_page = 5
        cc=ajax_pagination(request,data,dis_page,p)
        return HttpResponse(json.dumps(cc))
def ajax_pagination(request,data,dis_page,p):
    """
    ajax分页
    :param request:
    :param data:
    :param dis_page:
    :param p:
    :return:
    """
    data_count = int(len(data))
    # 总页数，每页显示10条数据
    if data_count % 10 == 0:
        page_count = data_count / 10
    else:
        page_count = data_count / 10 + 1
    middle_value = dis_page / 2
    if page_count <= dis_page:
        page_list = range(1, page_count + 1)
    else:
        if p:
            if p <= middle_value + 1:
                page_list = range(1, dis_page + 1)
            elif p >= page_count - middle_value:
                page_list = range(page_count - dis_page + 1, page_count + 1)
            elif p == page_count:
                page_list = range(page_count, page_count + 1)
            else:
                page_list = range(p - middle_value, p + middle_value + 1)
        else:
            p = 1
            page_list = range(1, dis_page + 1)
    data = data[(p - 1) * 10:p * 10]
    return {"data":data,'p':p,"page_count":page_count,"page_list":page_list,"dis_page":dis_page,"data_count":data_count}
@csrf_exempt
@login_required
def index_data(request):
    """
    首页-曲线图，ajax获取数据函数
    :param request:
    :return:
    """
    if request.method=='POST':
        cpu = zabbix_get_hitory(request, "cpu", '10.251.2.27', 'zabbix', '123456', 'zabbix', 'system.cpu.util[,,avg5]')
        mem = zabbix_get_hitory(request, "mem", '10.251.2.27', 'zabbix', '123456', 'zabbix', 'vm.memory.size[pused]')
        data={
              "cpu": cpu,
              "mem": mem,
              }
    return HttpResponse(json.dumps({"data":data}))
def zabbix_get_hitory(request,name,ip,user,passwd,dbname,item,index='',id='',start_time='',stop_time=''):
    """
    对zabbix_mysql获取的数据进行进一步处理---首页
    :param request:
    :param name:
    :param ip:
    :param user:
    :param passwd:
    :param dbname:
    :param item:
    :param index:
    :param id:
    :param start_time:
    :param stop_time:
    :return:
    """
    name = zabbix_mysql.zabbix_mysql(ip,user,passwd,dbname,start_time,stop_time)
    result_name = name.init_index_data(item)
    text_name = result_name.keys()[0]
    values_list_name = result_name.values()[0]
    for k, v in values_list_name.items():
        date_list_name = []
        for i, d in enumerate(v):
            date_list_name.append(d.keys()[0])
            v[i] = d.values()[0]
    return {"text": text_name, "date_list": date_list_name, "data": values_list_name,"index":index,"id":id}


@csrf_exempt
@login_required
def monitor_data(request):
    """
    性能统计-曲线图
    :param request:
    :return:
    """
    if request.method=='POST':
        index=request.POST.get("index")
        id=request.POST.get("id")
        start_time=request.POST.get("start_time")
        stop_time=request.POST.get("stop_time")
        if  start_time:
            start_time = "and date_format(from_unixtime(e.clock),'%Y-%m-%d')>='" + start_time + "'"
        if  stop_time:
            stop_time = "and date_format(from_unixtime(e.clock),'%Y-%m-%d')<='" + stop_time + "'"
        cpu = monitor_data_hitory(request, "cpu", '10.251.2.27', 'zabbix', '123456', 'zabbix', 'system.cpu.util[,,avg5]',index,id,start_time,stop_time)
        mem = monitor_data_hitory(request, "mem", '10.251.2.27', 'zabbix', '123456', 'zabbix', 'vm.memory.size[pused]',index,id,start_time,stop_time)
        data={
              "1-cpu": cpu,
              "2-mem": mem,
              }
    return HttpResponse(json.dumps({"data":data}))

def monitor_data_hitory(request,name,ip,user,passwd,dbname,item,index='',id='',start_time='',stop_time=''):
    """
    对zabbix_mysql获取的数据进行进一步处理---性能统计
    :param request:
    :param name:
    :param ip:
    :param user:
    :param passwd:
    :param dbname:
    :param item:
    :param index:
    :param id:
    :param start_time:
    :param stop_time:
    :return:
    """
    name = zabbix_mysql.zabbix_mysql(ip,user,passwd,dbname,start_time,stop_time)
    result_name = name.init_sel(item)
    text_name = result_name.keys()[0]
    values_list_name = result_name.values()[0]
    for k, v in values_list_name.items():
        date_list_name = []
        for i, d in enumerate(v):
            date_list_name.append(d.keys()[0])
            v[i] = d.values()[0]
    return {"text": text_name, "date_list": date_list_name, "data": values_list_name,"index":index,"id":id}

@login_required
def database_forms(request):
    if request.method=="GET":
        return render(request, 'capability/database_forms.html')
@csrf_exempt
@login_required
def database_search_post(request):
    if request.method=="POST":
        hosts=request.POST['hosts']
        oracle_tablespace = conn_oracle.conn_oracle()
        print hosts
        print oracle_tablespace
        tablespace_list=""
        for value in range(0, len(oracle_tablespace[0]), 2):
            tablespace_list+=format(oracle_tablespace[0][value],"<16")
        tablespace_list=tablespace_list+"\n"

        for i in oracle_tablespace:
            for value in range(1, len(i), 2):

                tablespace_list+=format(str(i[value]),"<16")
            tablespace_list = tablespace_list + "\n"
        print tablespace_list
        oracle_list={"10.168.23.225":tablespace_list}

        return HttpResponse(json.dumps(oracle_list))

