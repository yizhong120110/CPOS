# -*- coding: utf-8 -*-
# Action: 监控管理-监控对象管理
# Author: fangch
# AddTime: 2015-04-20
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import os
import glob
import datetime
import traceback
import uuid
import json
# 数据库连接
import ops.core.rdb
from ops.core.utils import get_xtcs
from ops.core.rpc import call_jy_reply
from ops.core.logger import tlog
from ops.core.settings import settings


def get_strftime2():
    """
    # 获取当前时间(yyyyMMddHHmmss格式)
    """
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def get_uuid():
    """
    # 获取新的uuid
    """
    return uuid.uuid4().hex

# 基类
class Base:
    def __init__(self,zjip,dxcjpzid):
        dxxx = []
        with sjapi.connection() as db:
            # 获取对象信息： ID, dxbm, sslbbm, dxmc, dxms, zt, czr, czsj
            sql = """select a.id, a.dxbm, a.sslbbm, a.dxmc, a.dxms, a.zt, a.czr, a.czsj, b.sscjpzid
                    from gl_dxdy a, gl_dxcjpz b
                    where a.id = b.dxid
                    and b.id = %(dxcjpzid)s"""
            dxxx = db.execute_sql( sql ,{'dxcjpzid':dxcjpzid} ,"dict" )
        if not dxxx:
            # 对于无法查询到数据的情况，为异常
            raise Exception('无法获取到对象信息')
        # 初始化对象信息
        self.dxid = dxxx[0]['id']
        self.dxbm = dxxx[0]['dxbm']
        self.sslb = dxxx[0]['sslbbm']
        self.dxmc = dxxx[0]['dxmc']
        self.ms = dxxx[0]['dxms']
        self.zt = dxxx[0]['zt']
        self.czr = dxxx[0]['czr']
        self.czsj = dxxx[0]['czsj']
        self.cjpzid = dxxx[0]['sscjpzid']
        self.zjip = zjip


# 文件类别
class File(Base):
    def ind_filedir_exist(self,wjml,rqcz):
        """
        文件是否在指定目录存在
        """
        # 对日期差值进行转换为int型
        rqcz = int(rqcz)
        # 获取当前日期
        dqrq = get_strftime2()[:8]
        # 对文件名进行处理
        clwjm = (datetime.datetime.strptime(dqrq,'%Y%m%d') + datetime.timedelta(days= rqcz )).strftime(self.dxbm)
        # 获取结果信息 result格式[[文件名1，文件大小，文件生成时间]，[文件名2，文件大小，文件生成时间]，…]
        result = self.findfiles(wjml,clwjm)
        result = json.dumps(result) if result else ''
        with sjapi.connection() as db:
            # 将文件信息登记到数据库 
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':result, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'ind_filedir_exist(wjml,rqcz)'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def ind_filedb_exist(self,zt,rqcz,ywlx):
        """
        文件是否在文件处理登记表中存在
        """
        # 对日期差值进行转换为int型
        rqcz = int(rqcz)
        # 获取当前日期
        dqrq = get_strftime2()[:8]
        # 对文件名进行处理
        clwjm = (datetime.datetime.strptime(dqrq,'%Y%m%d') + datetime.timedelta(days=rqcz)).strftime(self.dxbm)
        if '*' in clwjm:
            # 将‘*’替换为‘%’,用于数据库查询
            clwjm = clwjm.replace('*','%')
        with sjapi.connection() as db:
            csxx = {'wjm':clwjm, 'zt':zt, 'ywlx':ywlx, 'djrq':dqrq}
            # 获取文件处理登记薄中信息
            # 文件信息格式：[[文件名1，文件大小，登记日期，登记时间，批次号，文件类型，总比数，总金额]，[文件名2，文件大小，登记日期，登记时间，批次号，文件类型，总比数，总金额]，…]
            wjxx = []
            cx_wjxx = [] # 存查询数据库获取的数据结构信息 wjm, wjdx, djrq, djsj, pch, wjlx, zbs, zje
            if '*' in self.dxbm:
                sql_get_wjcldjb1 = """select wjm, wjdx, djrq, djsj, pch, wjlx, zbs, zje from jy_wjcldjb 
                                where wjm like %(wjm)s 
                                and zt = %(zt)s
                                and ywlx = %(ywlx)s
                                and djrq = %(djrq)s"""
                cx_wjxx = db.execute_sql( sql_get_wjcldjb1, csxx, 'dict' )
            else:
                sql_get_wjcldjb2 = """select wjm, wjdx, djrq, djsj, pch, wjlx, zbs, zje from jy_wjcldjb 
                                where wjm = %(wjm)s 
                                and zt = %(zt)s
                                and ywlx = %(ywlx)s
                                and djrq = %(djrq)s"""
                cx_wjxx = db.execute_sql( sql_get_wjcldjb2, csxx, 'dict' )
            for wj in cx_wjxx:
                wjxx.append([wj['wjm'],wj['wjdx'],wj['djrq'],wj['djsj'],wj['pch'],wj['wjlx'],wj['zbs'],wj['zje']])
            wjxx = json.dumps(wjxx) if wjxx else ''
            # 将文件信息登记到数据库 
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':wjxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'ind_filedb_exist(zt,rqcz,ywlx)'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def findfiles(self,dirname,pattern):
        """
        获取指定目录下的文件信息( 不用于对外开发，知识类内部调用 )
        """
        cwd = os.getcwd() #保存当前工作目录
        if dirname:
            os.chdir(dirname)
        result = []
        for filename in glob.iglob(pattern): #此处可以用glob.glob(pattern) 返回所有结果
            size = os.path.getsize(filename)
            timestamp = os.path.getmtime(filename)
            date = datetime.datetime.fromtimestamp(timestamp)
            time = date.strftime('%Y-%m-%d %H:%M:%S')
            result.append([filename,size,time])
        #恢复工作目录
        os.chdir(cwd)
        return result


# 主机类别
class Computer(Base):
    def get_cpu(self):
        """
        获取CPU使用情况
        """
        cpu = os.popen('top -bi -n 2 -d 0.02').read().split('\n\n\n')[1].split('\n')[2]
        if cpu:
            with sjapi.connection() as db:
                # 将信息登记到采集结果表中
                csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':cpu, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'cpu', 'zbbm':'get_cpu()'}
                sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
                values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
                db.execute_sql( sql ,csxx, 'dict' )
    
    def get_ram(self):
        """
        获取内存使用情况
        """
        com = """free |grep buffers/cache |awk '{print "物理内存已使用"$3",未使用"$4}';free |grep Swap |awk '{print "交换分区已使用"$3",未使用"$4}';cat /proc/meminfo|grep VmallocTotal |awk '{print "虚拟内存总大小"$2}';cat /proc/meminfo|grep VmallocUsed |awk '{print "虚拟内存已使用"$2}'"""
        ram = os.popen(com).read()
        if ram:
            with sjapi.connection() as db:
                # 将信息登记到采集结果表中
                csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':ram, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'ncsy', 'zbbm':'get_ram()'}
                sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
                values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
                db.execute_sql( sql ,csxx ,"dict" )
    
    def get_io(self):
        """
        获取磁盘I/O繁忙率
        """
        com = """iostat -d -x|awk 'NF'|awk 'NR>2{print $1":"$12"%"}'"""
        io = os.popen(com).read()
        # 有值才向采集配置表中插入信息
        if io:
            with sjapi.connection() as db:
                # 将信息登记到采集结果表中
                csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':io, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'io', 'zbbm':'get_io()'}
                sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
                values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
                db.execute_sql( sql ,csxx ,"dict" )
    
    def get_filesystem(self):
        """
        获取文件系统使用率
        """
        filesystem= os.popen(""" df -k|awk '{print $1"|"$2"|"$3"|"$4"|"$5}'""").read().split('\n')
        filesystem_lst = [] # 保存各个文件系统信息列表,格式为[[“filesystem”+ 文件系统名，文件系统信息字符串],[]]
        # 循环对filesystem进行逐行解析处理
        i = 0
        while i < len(filesystem):
            if not filesystem[i]:
                # 对行为空的不进行处理
                i += 1
                continue
            # 对每一行数据通过分隔符”|”进行拆分
            fs_lst = filesystem[i].split('|')
            # 如果拆分出的第二三四段字符串不为空，则将信息放到数据结构中
            if fs_lst[1]:
                # 只对第二字段字符串为数字的进行处理
                if fs_lst[1].isdigit():
                    substr = 'filesystem' + fs_lst[0]
                    filesystem_lst.append([substr,filesystem[i]])
                # 对第二字段不为数字的，表示为首行的说明行，无需处理
                i += 1
            # 如果拆分出的第二段字符串为空，则将filesystem下一行内容并入第一段文件系统名称字符串尾，中间插入分隔符”|”
            else:
                fs = filesystem[i+1]
                substr = 'filesystem' + fs_lst[0]
                wjxtxx = fs_lst[0] + '|' + fs
                filesystem_lst.append([substr,wjxtxx])
                i += 2
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            for wjxt in filesystem_lst:
                csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':wjxt[1], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':wjxt[0], 'zbbm':'get_filesystem()'}
                sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
                values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
                db.execute_sql( sql ,csxx ,"dict" )
    
    def get_virtual(self):
        """
        获取虚拟内存使用情况
        """
        com = """cat /proc/meminfo|grep VmallocUsed |awk '{print "虚拟内存已使用"$2}'"""
        virtual = os.popen(com).read()
        if virtual:
            with sjapi.connection() as db:
                # 将信息登记到采集结果表中
                csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':virtual, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'virtual', 'zbbm':'get_virtual()'}
                sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
                values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
                db.execute_sql( sql ,csxx ,"dict" )
    
    def get_process(self):
        """
        获取进程信息
        """
        cjjgxx = {}  # 存采集结果信息，结构为：{进程名称：cjxx，进程名称2：cjxx，…}
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            sql_get_jcxx = """select jcmc,ckml 
                            from gl_jcxxpz 
                            where sszj_ip = %(zjip)s
                            and zt = '1' """
            jcxx_lst = db.execute_sql( sql_get_jcxx,{'zjip':self.zjip} ,"dict" )
            for jcxx in jcxx_lst:
                if not jcxx.get('ckml'):
                    continue
                cjxx = os.popen(jcxx['ckml']).read()
                cjjgxx[jcxx['jcmc']] = cjxx
            # 将获取到的信息登记到采集结果表中( 进程信息总长度超过4000，所以保存到nr2（clob）中 )
            cjjgxx = json.dumps(cjjgxx) if cjjgxx else ''
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':cjjgxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'jccj', 'zbbm':'get_process()'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr2,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )


# 通讯类别
class Commun(Base):
    def test_cominfcon(self,jym,bwzfj="utf8"):
        """
        通讯接口是否联通
        """
        # 虚拟柜员，使用系统参数值
        XNGY = get_xtcs('XNGY')
        # 虚拟机构，使用系统参数值
        XNJGDM = get_xtcs('XNJGDM')
        # 组织发送给核心的报文
        fsxx = {'CZGY':XNGY,'JYJGM':XNJGDM}
        buf = '%s%s%s'%( str( len( fsxx ) + 20 ).ljust(4,' '), jym.ljust(16,' ') , json.dumps(fsxx) )
        # ZDFSSVR为柜面服务端配置的通讯编码
        buf_fk = call_jy_reply( 'ZDFSSVR',buf.encode(bwzfj) )
        # 解析
        buf_fk = buf_fk.decode(bwzfj)
        tlog.log_info('buf_fk---%s'%str(buf_fk))
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':buf_fk, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':jym, 'zbbm':'test_cominfcon(jym,bwzfj="utf8")'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )


# 数据库类别
class Database(Base):
    def get_tabinf(self, tab, tj="1=1", bkjmc="TSYW"):
        """
        获取数据表信息量
        """
        # 将表空间和表名称转化为大写
        bkjmc = bkjmc.upper()
        tab = tab.upper()
        with sjapi.connection() as db:
            # 获取表信息量
            sql = "select count(0) as count from %s.%s where %s"%(bkjmc,tab,tj)
            rs = db.execute(sql)
            bxxl = rs.fetchone()
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':bxxl['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'%s.%s'%(bkjmc,tab), 'zbbm':'get_tabinf(tab,tj="1=1",bkjmc="TSYW")'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def get_bkjsyl( self,bkjmc="TSYW" ):
        """
        获取某一数据表空间当前的使用率
        """
        # 将表空间名称转化为大写
        bkjmc = bkjmc.upper()
        with sjapi.connection() as db:
            # 获取表空间当前的使用率
            sql_get_bkjsyl = """SELECT D.TABLESPACE_NAME, SPACE || 'M' "SUM_SPACE(M)", BLOCKS "SUM_BLOCKS",  
                                       SPACE - NVL (FREE_SPACE, 0) || 'M' "USED_SPACE(M)", 
                                       ROUND ( (1 - NVL (FREE_SPACE, 0) / SPACE) * 100, 2) || '%' "USED_RATE(%)", 
                                       FREE_SPACE || 'M' "FREE_SPACE(M)"  
                                FROM 
                                (  
                                    SELECT TABLESPACE_NAME, ROUND (SUM (BYTES) / (1024 * 1024), 2) SPACE,  
                                         SUM (BLOCKS) BLOCKS  
                                    FROM DBA_DATA_FILES  
                                    GROUP BY TABLESPACE_NAME) D,  
                                ( 
                                    SELECT TABLESPACE_NAME, ROUND (SUM (BYTES) / (1024 * 1024), 2) FREE_SPACE  
                                    FROM DBA_FREE_SPACE  
                                    GROUP BY TABLESPACE_NAME) F  
                                WHERE D.TABLESPACE_NAME = F.TABLESPACE_NAME(+)  
                                and D.TABLESPACE_NAME = %(bkjmc)s
                                ORDER BY 1"""
            sylxx = db.execute_sql( sql_get_bkjsyl,{ 'bkjmc':bkjmc } ,"dict" )
            syl_lst = ''
            if sylxx:
                syl_lst = [ sylxx[0]['tablespace_name'], sylxx[0]['sum_space(m)'], sylxx[0]['sum_blocks'], sylxx[0]['used_rate(%)'], sylxx[0]['free_space(m)'] ]
            syl = json.dumps(syl_lst) if syl_lst else ''
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':syl, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':bkjmc, 'zbbm':'get_bkjsyl(bkjmc="TSYW")'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def get_conversation(self):
        """
        获取数据库当前活动会话数
        """
        with sjapi.connection() as db:
            # 获取表空间当前的使用率
            sql_get_conversation = """select username,count(0) as count
                                    from v$session
                                    where status = 'ACTIVE'
                                    and username is not null
                                    group by username"""
            if settings.DB_TYPE == "postgresql":
                sql_get_conversation = """select usename as username, count(0) as count 
                                    from pg_stat_activity 
                                    where state = 'active' 
                                    group by usename"""
            hhs_lst = db.execute_sql( sql_get_conversation,{} ,"dict" )
            hhs = json.dumps(hhs_lst)
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':hhs, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'get_conversation', 'zbbm':'get_conversation()'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def get_zxsj(self):
        """
        获取数据库SQL执行时间
        """
        with sjapi.connection() as db:
            # 获取数据库SQL执行时间
            sql_get_zxsj = """select sql_text, ELAPSED_TIME from
                            (select sql_text,ELAPSED_TIME from v$sql
                            where to_char(sysdate,'YYYY-MM-DD/HH24:MI:SS') >= last_load_time
                            and last_load_time >= to_char(sysdate -5/(24*60),'YYYY-MM-DD/HH24:MI:SS')
                            order BY ELAPSED_TIME DESC)
                            where 2 > rownum"""
            if settings.DB_TYPE == "postgresql":
                sql_get_zxsj = """select extract(epoch FROM (now() - start))*1000000 as elapsed_time, current_query as sql_text from 
                            (
                                select 
                                backendid, pg_stat_get_backend_pid(s.backendid) as procpid,
                                pg_stat_get_backend_activity_start(s.backendid) as start,
                                pg_stat_get_backend_activity(s.backendid) as current_query
                                from 
                                ( select pg_stat_get_backend_idset() as backendid ) as s
                            ) as s
                            where
                            current_query <> '<idle>'
                            and now() >= start and start >= now() - interval '5 minute'
                            order by elapsed_time  desc limit 1;"""
            zxsj_lst = db.execute_sql( sql_get_zxsj,{} ,"dict" )
            zxsjxx = ''
            if zxsj_lst:
                zxsjxx = json.dumps([zxsj_lst[0]['sql_text'],zxsj_lst[0]['elapsed_time']])
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':zxsjxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'get_zxsj', 'zbbm':'get_zxsj()'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )


# 业务类别
class Business(Base):
    def get_failtrans( self,jymlb, sbxymlb, min ):
        """
        获取交易失败笔数
        """
        # 获取当前日期时间
        dqrqsj = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        dqrq = dqrqsj[:8]
        dqsj = dqrqsj[8:]
        # 获取前推的日期时间
        qtrqsj = (datetime.datetime.strptime(dqrqsj,'%Y%m%d%H%M%S') - datetime.timedelta(minutes=int(min))).strftime('%Y%m%d%H%M%S')
        qtrq = qtrqsj[:8]
        qtsj = qtrqsj[8:]
        # 响应码列表获取
        xym_str_lst = sbxymlb.split(',')
        # 交易码列表获取
        jym_str_lst = jymlb.split(',')
        with sjapi.connection() as db:
            params = {'dqrq':dqrq,'dqsj':dqsj,'qtrq':qtrq,'qtsj':qtsj}
            # 获取交易失败笔数
            sql_get_jysbbs = """select count(0) as count 
                            from jy_ls 
                            where xym in ( '%s' )
                            and jym in ( '%s' )
                            and '%s' >= jyfqsj
                            and jyfqsj >= '%s'""" % ( 
                            "','".join( xym_str_lst ), "','".join( jym_str_lst ),
                            dqrqsj, qtrqsj )
            sbbs = db.execute_sql( sql_get_jysbbs )
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':sbbs[0]['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'get_failtrans(jymlb,sbxymlb,min)'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )
    
    def get_firstrans( self,jymlb ):
        """
        获取业务第一笔交易
        """
        with sjapi.connection() as db:
            # 交易码列表获取
            jym_str_lst = jymlb.split(',')
            # 获取业务是否有第一笔交易
            sql_get_dybjy = """select count(0) as count
                                from jy_ls
                                where jym in ( '%s' )""" % ( "','".join( jym_str_lst ) )
            ywcount = db.execute_sql( sql_get_dybjy )
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':ywcount[0]['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'get_firstrans(jymlb)'}
            sql = """insert into gl_cjjgb(id,ssdxid,nr,jlsj,cjpzid,ip,cjmc,zbbm)
            values (%(id)s,%(ssdxid)s,%(nr)s,%(jlsj)s,%(cjpzid)s,%(ip)s,%(cjmc)s,%(zbbm)s)"""
            db.execute_sql( sql ,csxx ,"dict" )

if __name__ == '__main__':
    pass
#    # File
#    # ind_filedir_exist()
#    zj = File('txxx','28f8adde01a541788e7586703d81ada1')
#    zj.ind_filedir_exist('/home/sjdev/test/','1')
#    # ind_filedb_exist
#    zj = File('txxx','7ba60bec55b64f0a9c5ec66613f4197b')
#    zj.ind_filedb_exist('10', '0', 'ETC')
#    zj = File('txxx','892c51d839854a4a9294cb04ae295739')
#    zj.ind_filedb_exist('10', '0', 'ETC')
#    # Computer
#    # get_cpu()
#    zj = Computer('tsgl','ba5c5656ddf644018073d570de0ca93f')
#    zj.get_cpu()
#    # get_ram()
#    zj = Computer('tsgl','dfc920d0e6654923a993573ed9f6ee19')
#    zj.get_ram()
#    # get_virtual()
#    zj = Computer('tsgl','7308f13ae5aa47b1936ee21a9ed67499')
#    zj.get_virtual()
#    # get_filesystem()
#    zj = Computer('tsgl','f5dfa0454a71468a81100d6c4423172e')
#    zj.get_filesystem()
#    # get_io()
#    zj = Computer('tsgl','8c62904b1f1948db8631dc74fd2f59d8')
#    zj.get_io()
#    # get_process()
#    zj = Computer('tsgl','ce1700f724574fd8a098f6e4fbd02540')
#    zj.get_process()
#    # Commun(Base):
#    # test_cominfcon(self,jym)
#    zj = Commun('txxx','fad68c6a44f145a9a65883f3ffc7df9b')
#    zj.test_cominfcon('gt0001')
#    # Database(Base):
#    # get_zxsj(self,jym)
#    zj = Database('txxx','c970bf08b03f42b6834da56c3cb5b800')
#    zj.get_zxsj()
#    #get_conversation()
#    zj = Database('txxx','2457eb9717eb4cfb91913aad18d68ffb')
#    zj.get_conversation()
#    #get_tabinf()
#    zj = Database('txxx','8281ff70a74d44d9870ab8b64cc0b1e3')
#    zj.get_tabinf('gl_hydy',tj="1=1",bkjmc="JNGT")
#    #get_bkjsyl()
#    zj = Database('txxx','5722bc9c899d4b8ea81ebc3c3862b3ca')
#    zj.get_bkjsyl(bkjmc="TSYW")
#    # Business(Base):
#    # get_failtrans
#    zj = Business('txxx','14bfef011c5d4ad4b45284e460ee0d0a')
#    zj.get_firstrans('gt0001,gt0002,gt0003')
#    # get_failtrans
#    zj = Business('txxx','b307c15264194ed1ab9e9065a02a26a4')
#    zj.get_failtrans('gt0001,gt0002,gt0003','TS0008,TS9999,TS0004','14400')
