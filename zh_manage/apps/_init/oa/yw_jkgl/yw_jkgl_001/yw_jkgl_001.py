# -*- coding: utf-8 -*-
# Action: 监控管理-监控对象管理
# Author: fangch
# AddTime: 2015-04-20
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import os
import glob
import datetime
import traceback
import pickle
from sjzhtspj import ModSql
from sjzhtspj.common import get_strftime2,get_uuid,pickle_dumps
from sjzhtspj import logger


# 基类
class Base:
    def __init__(self,zjip,dxcjpzid):
        dxxx = []
        with sjapi.connection() as db:
            # 获取对象信息： ID, dxbm, sslbbm, dxmc, dxms, zt, czr, czsj
            dxxx = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_dxnr", {'dxcjpzid':dxcjpzid})
        if not dxxx:
            # 对于无法查询到数据的情况，为异常
            logger.info("无法获取到对象信息")
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
        result = pickle_dumps(result) if result else ''
        with sjapi.connection() as db:
            # 将文件信息登记到数据库 
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':result, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'ind_filedir_exist(wjml,rqcz)'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
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
                cx_wjxx = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_wjcldjb1", csxx)
            else:
                cx_wjxx = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_wjcldjb2", csxx)
            for wj in cx_wjxx:
                wjxx.append([wj['wjm'],wj['wjdx'],wj['djrq'],wj['djsj'],wj['pch'],wj['wjlx'],wj['zbs'],wj['zje']])
            wjxx = pickle_dumps(wjxx) if wjxx else ''
            # 将文件信息登记到数据库 
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':wjxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'ind_filedb_exist(zt,rqcz,ywlx)'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def findfiles(self,dirname,pattern):
        """
        获取指定目录下的文件信息
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
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':cpu, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'cpu', 'zbbm':'get_cpu()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_ram(self):
        """
        获取内存使用情况
        """
        com = """free |grep Mem |awk '{print "物理内存已使用"$3",未使用"$4}';free |grep Swap |awk '{print "交换分区已使用"$3",未使用"$4}';cat /proc/meminfo|grep VmallocTotal |awk '{print "虚拟内存总大小"$2}';cat /proc/meminfo|grep VmallocUsed |awk '{print "虚拟内存已使用"$2}'"""
        ram = os.popen(com).read()
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':ram, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'ncsy', 'zbbm':'get_ram()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_io(self):
        """
        获取磁盘I/O繁忙率
        """
        com = """iostat -d -x|awk 'NF'|awk 'NR>2{print $1":"$12"%"}'"""
        io = os.popen(com).read()
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':io, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'io', 'zbbm':'get_io()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
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
                ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_virtual(self):
        """
        获取虚拟内存使用情况
        """
        com = """cat /proc/meminfo|grep VmallocUsed |awk '{print "虚拟内存已使用"$2}'"""
        virtual = os.popen(com).read()
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':virtual, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'virtual', 'zbbm':'get_virtual()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_process(self):
        """
        获取进程信息
        """
        cjjgxx = {}  # 存采集结果信息，结构为：{进程名称：cjxx，进程名称2：cjxx，…}
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            jcxx_lst = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_jcxx", {'zjip':self.zjip})
            for jcxx in jcxx_lst:
                if not jcxx.get('ps_com'):
                    continue
                cjxx = os.popen(jcxx['ps_com']).read()
                cjjgxx[jcxx['jcmc']] = cjxx
            # 将获取到的信息登记到采集结果表中
            cjjgxx = pickle_dumps(cjjgxx) if cjjgxx else ''
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':cjjgxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'jccj', 'zbbm':'get_process()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)


# 通讯类别
class Commun(Base):
    def test_cominfcon(self,jym):
        """
        通讯接口是否联通
        """
        # todo调用核心接口执行流程
        # 组织发送给核心的报文
        #buf = {}
        #send_message_to_icm 更名为  call_jy_reply
        #from sjzhtspj.esb import call_jy_reply
        #buf_fk = call_jy_reply('FWDTEST',buf_data)  # FWDTEST为柜面服务端配置的通讯编码
        xyxx = ''
        with sjapi.connection() as db:
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':xyxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':jym, 'zbbm':'test_cominfcon(jym)'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)


# 数据库类别
class Database(Base):
    def get_tabinf(self, tab, tj="1=1", bkjmc="TSYW"):
        """
        获取数据表信息量
        """
        with sjapi.connection() as db:
            # 获取表信息量
            #bxxl = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_bxxl", {'tab':[tab],'bkjmc':[bkjmc],'tj':tj})
            sql = "select count(0) as count from %s.%s where %s"%(bkjmc,tab,tj)
            rs = db.execute(sql)
            bxxl = rs.fetchone()
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':bxxl['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'%s.%s'%(bkjmc,tab), 'zbbm':'get_tabinf(tab,tj="1=1",bkjmc="TSYW")'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_bkjsyl( self,bkjmc="TSYW" ):
        """
        获取某一数据表空间当前的使用率
        """
        with sjapi.connection() as db:
            # 获取表空间当前的使用率
            sylxx = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_bkjsyl", { 'bkjmc':bkjmc })
            syl_lst = ''
            if sylxx:
                syl_lst = [ sylxx[0]['tablespace_name'], sylxx[0]['sum_space(m)'], sylxx[0]['sum_blocks'], sylxx[0]['used_rate(%)'], sylxx[0]['free_space(m)'] ]
            syl = pickle_dumps(syl_lst) if syl_lst else ''
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':syl, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':bkjmc, 'zbbm':'get_bkjsyl(bkjmc="TSYW")'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_conversation(self):
        """
        获取数据库当前活动会话数
        """
        with sjapi.connection() as db:
            # 获取表空间当前的使用率
            hhs_lst = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_conversation")
            hhs = pickle_dumps(hhs_lst)
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':hhs, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'get_conversation', 'zbbm':'get_conversation()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_zxsj(self):
        """
        获取数据库SQL执行时间
        """
        with sjapi.connection() as db:
            # 获取数据库SQL执行时间
            zxsj_lst = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_zxsj")
            zxsjxx = ''
            if zxsj_lst:
                zxsjxx = pickle_dumps([zxsj_lst[0]['sql_text'],zxsj_lst[0]['elapsed_time']])
            
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':zxsjxx, 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':'get_zxsj', 'zbbm':'get_zxsj()'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)


# 业务类别
class Business(Base):
    def get_failtrans( self,jymlb, sbxymlb, min ):
        """
        获取交易失败笔数
        """
        # 获取当前日期时间
        dqrqsj = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
        dqrq = dqrqsj[:8]
        dqsj = dqrqsj[8:]
        # 获取前推的日期时间
        qtrqsj = (datetime.datetime.strptime(dqrqsj,'%Y%m%d%H:%M:%S') - datetime.timedelta(minutes=int(min))).strftime('%Y%m%d%H:%M:%S')
        qtrq = qtrqsj[:8]
        qtsj = qtrqsj[8:]
        # 响应码列表获取
        xym_str_lst = sbxymlb.split(',')
        # 交易码列表获取
        jym_str_lst = jymlb.split(',')
        with sjapi.connection() as db:
            params = {'xym_str_lst':xym_str_lst,'jym_str_lst':jym_str_lst,'dqrq':dqrq,'dqsj':dqsj,'qtrq':qtrq,'qtsj':qtsj}
            # 获取交易失败笔数
            sbbs = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_jysbbs", params)
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':sbbs[0]['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'get_failtrans(jymlb,sbxymlb,min)'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
    
    def get_firstrans( self,jymlb ):
        """
        获取业务第一笔交易
        """
        with sjapi.connection() as db:
            # 交易码列表获取
            jym_str_lst = jymlb.split(',')
            # 获取业务是否有第一笔交易
            ywcount = ModSql.yw_jkgl_001.execute_sql_dict(db, "get_dybjy", {'jym_str_lst':jym_str_lst})
            # 将信息登记到采集结果表中
            csxx = {'id':get_uuid(), 'ssdxid':self.dxid, 'nr':ywcount[0]['count'], 'jlsj':get_strftime2(), 'cjpzid':self.cjpzid, 'ip':self.zjip, 'cjmc':self.dxbm, 'zbbm':'get_firstrans(jymlb)'}
            ModSql.yw_jkgl_001.execute_sql_dict(db, "ins_cjjg", csxx)
