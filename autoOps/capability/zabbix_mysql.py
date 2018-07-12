#!/usr/bin/python
#coding:utf-8

import MySQLdb
import traceback
import collections
import json
class zabbix_mysql:
    def __init__(self,ip,user,password,dbname,start_time='',stop_time=''):
        self.con = None
        self.ip=ip
        self.user=user
        self.password=password
        self.dbname=dbname
        self.start_time=start_time
        self.stop_time=stop_time
    def host_list(self):
        sql="""
        select host
        from groups a,hosts_groups b,hosts c
        where a.name='jct_groups' 
        and a.groupid=b.groupid 
        and c.status<>3
        and c.hostid=b.hostid;
        
        """
        conn=MySQLdb.connect(self.ip,self.user,self.password,self.dbname,charset = 'utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data
    def froms_data(self,key,host):
        sql="""select c.host,
            date_format(from_unixtime(e.clock),'%Y-%m-%d'),
            d.name,round(avg(e.value),2),
            round(max(e.value),2),
            round(min(e.value),2)  
            from groups a,hosts_groups b,hosts c,items d,history e
            where 
            a.name='jct_groups' 
            """+key+"""
            """+host+"""
            and a.groupid=b.groupid 
            and c.status<>3
            and c.hostid=b.hostid
            and c.hostid=d.hostid
            and d.itemid=e.itemid
            """+self.start_time+"""
            """+self.stop_time+"""
            group by date_format(from_unixtime(e.clock),'%Y-%m-%d'),c.host,d.itemid,d.name
            order by date_format(from_unixtime(e.clock),'%Y-%m-%d') desc;"""
        conn = MySQLdb.connect(self.ip, self.user, self.password, self.dbname, charset='utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data

    def sel_data(self,key):
        sql="""select c.host,
            date_format(from_unixtime(e.clock),'%Y-%m-%d'),
            d.name,round(avg(e.value),2),
            round(max(e.value),2),
            round(min(e.value),2)  
            from groups a,hosts_groups b,hosts c,items d,history e
            where d.key_='"""+key+"""'
            and a.name='jct_groups' 
            and a.groupid=b.groupid 
            and c.status<>3
            and c.hostid=b.hostid
            and c.hostid=d.hostid
            and d.itemid=e.itemid
            """+self.start_time+"""
            """+self.stop_time+"""
            group by date_format(from_unixtime(e.clock),'%Y-%m-%d'),c.host,d.itemid,d.name
            order by host,date_format(from_unixtime(e.clock),'%Y-%m-%d');"""

        conn=MySQLdb.connect(self.ip,self.user,self.password,self.dbname,charset = 'utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data
    def index_data(self,key):
        sql="""select c.host,
            date_format(from_unixtime(e.clock),'%Y-%m-%d'),
            d.name,round(avg(e.value),2),
            round(max(e.value),2),
            round(min(e.value),2)  
            from groups a,hosts_groups b,hosts c,items d,history e
            where d.key_='"""+key+"""'
            and a.name='jct_groups' 
            and a.groupid=b.groupid 
            and c.status<>3
            and c.hostid=b.hostid
            and c.hostid=d.hostid
            and d.itemid=e.itemid
            and SUBDATE(CURDATE(),INTERVAL 7 Day) < date_format(from_unixtime(e.clock),'%Y-%m-%d')
            group by date_format(from_unixtime(e.clock),'%Y-%m-%d'),c.host,d.itemid,d.name
            order by host,date_format(from_unixtime(e.clock),'%Y-%m-%d');"""

        conn=MySQLdb.connect(self.ip,self.user,self.password,self.dbname,charset = 'utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data
    def init_index_data(self,key):
        """
        初始化index_data数据
        :param key:
        :return:
        """
        ip_dict = collections.defaultdict(list)
        cpu_data = self.index_data(key)
        key_dict = {cpu_data[0][2]: ip_dict}
        for i in cpu_data:
            ip_dict[i[0]].append({i[1]: [i[3], i[4], i[5]]})
        time_list = []
        for k, j in ip_dict.items():
            for time in j:
                time_list.append(time.keys()[0])
        time_list = list(set(time_list))
        for k, j in ip_dict.items():
            cc_list = []
            for time in j:
                cc_list.append(time.keys()[0])
            for i in time_list:
                if i in cc_list:
                    continue
                j.append({i: ['null', 'null', 'null']})
        for k, j in ip_dict.items():
            ip_dict[k] = sorted(j)
        return key_dict

    def monitor_hosts(self):
        """
        首页监控主机数量统计
        :return:
        """
        sql="""
            select count(distinct c.host)
            from groups a,hosts_groups b,hosts c
            where 
            a.groupid=b.groupid 
            and c.status<>3
            and c.hostid=b.hostid;
        """
        conn = MySQLdb.connect(self.ip, self.user, self.password, self.dbname, charset='utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data
    def monitor_items(self):
        """
        首页监控项统计
        :return:
        """
        sql="""
        select count(1)
            from groups a,hosts_groups b,hosts c,items d
            where a.groupid=b.groupid 
            and c.status<>3
            and d.status=0
            and c.hostid=b.hostid
            and c.hostid=d.hostid;
        """
        conn = MySQLdb.connect(self.ip, self.user, self.password, self.dbname, charset='utf8')
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except:
            traceback.print_exc()
        finally:
            conn.close()
        return data
    def init_sel(self,key):
        """
        初始化sel_data查询数据
        :param key:
        :return:
        """
        ip_dict = collections.defaultdict(list)
        cpu_data=self.sel_data(key)
        key_dict = {cpu_data[0][2]: ip_dict}
        for i in cpu_data:
            ip_dict[i[0]].append({i[1]: [i[3], i[4], i[5]]})
        time_list=[]
        for k,j in ip_dict.items():
            for time in j:
                time_list.append(time.keys()[0])
        time_list=list(set(time_list))
        for k,j in ip_dict.items():
            cc_list = []
            for time in j:
                cc_list.append(time.keys()[0])
            for i in time_list:
                if i in cc_list:
                    continue
                j.append({i:['null','null','null']})
        for k, j in ip_dict.items():
            ip_dict[k]=sorted(j)
        return key_dict
if __name__=='__main__':
    cc = zabbix_mysql('10.251.2.27', 'zabbix', '123456', 'zabbix','system.cpu.util[,,avg5]')
    result=cc.init_sel()



    values_list=result.values()[0]
    date_list = []
    for k,v in  values_list.items():

        for i,d in enumerate(v):
            date_list = []
            date_list.append(d.keys()[0])
            v[i]=d.values()[0]
    date_list=list(set(date_list))


