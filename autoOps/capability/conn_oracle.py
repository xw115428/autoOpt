#!/usr/bin/env python
#coding:utf-8
import cx_Oracle
def conn_oracle():
    conn=cx_Oracle.connect('oracle/oracle@10.168.23.225/orcl')
    c=conn.cursor()
    a=c.execute("""
    SELECT * FROM (
    select 'Tablespace_name',t.tablespace_name ktablespace, 
           'Type',substr(t.contents, 1, 1) tipo, 
           'Used(MB)',trunc((d.tbs_size-nvl(s.free_space, 0))/1024/1024) ktbs_em_uso, 
           'ActualSize(MB)',trunc(d.tbs_size/1024/1024) ktbs_size, 
           'MaxSize(MB)',trunc(d.tbs_maxsize/1024/1024) ktbs_maxsize, 
           'FreeSpace(MB)',trunc(nvl(s.free_space, 0)/1024/1024) kfree_space, 
           'Space',trunc((d.tbs_maxsize - d.tbs_size + nvl(s.free_space, 0))/1024/1024) kspace, 
           'Perc',decode(d.tbs_maxsize, 0, 0, trunc((d.tbs_size-nvl(s.free_space, 0))*100/d.tbs_size)) kperc 
    from 
      ( select SUM(bytes) tbs_size, 
               SUM(decode(sign(maxbytes - bytes), -1, bytes, maxbytes)) tbs_maxsize, tablespace_name tablespace 
        from ( select nvl(bytes, 0) bytes, nvl(maxbytes, 0) maxbytes, tablespace_name 
        from dba_data_files 
        union all 
        select nvl(bytes, 0) bytes, nvl(maxbytes, 0) maxbytes, tablespace_name 
        from dba_temp_files 
        ) 
        group by tablespace_name 
        ) d, 
        ( select SUM(bytes) free_space, 
        tablespace_name tablespace 
        from dba_free_space 
        group by tablespace_name 
        ) s, 
        dba_tablespaces t 
        where t.tablespace_name = d.tablespace(+) and 
        t.tablespace_name = s.tablespace(+) 
        order by 8) 
        where  tipo <>'T' 
        and tipo <>'U'
    
    """)

    tablespace=a.fetchall()
    c.close()
    conn.close()


    return tablespace