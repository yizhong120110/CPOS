# -*- coding: utf-8 -*-

import cx_Oracle,uuid,pickle,datetime

# 数据库连接( 各个项目自行修改数据连接(根据main.yaml) )
DB_CONSTR = dict( dsn = '127.0.0.1:1521/orcl' , user = 'tcr' , password = 'tcr' )

dqsj = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class Get_cursor:
    def __enter__(self):
        # 建立连接
        self.db1 = cx_Oracle.connect( **DB_CONSTR )
        # 获取游标
        self.cursor = self.db1.cursor()
        return self.cursor
    def __exit__(self, type, value,  traceback):
        self.db1.commit()
        self.cursor.close()
        self.db1.close()
    
def get_cpu_ave():
    nr = """import datetime,uuid
# 获取当前日期时间
dqrqsj = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# 获取前推时间
qtsj = (datetime.datetime.strptime(dqrqsj,"%Y%m%d%H%M%S") - datetime.timedelta(minutes=int(dwsj))).strftime("%Y%m%d%H%M%S")
# 存主机CPU使用率数据结构 {主机IP：[cpu使用率1，cpu使用率2…]}
cpu_dic = {}
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = "select ip, nr from gl_cjjgb where cjmc = 'cpu' and jlsj >= '%s' order by jlsj, ip" %qtsj
    cur.execute( sql )
    rs = cur.fetchall()
    for row in rs:
        # 内容格式："Cpu(s):  1.5%us,  3.0%sy,  0.0%ni, 5.5%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st"
        cpusyl = 100 - float(row[1].split(",")[3].split("%")[0])
        # 组织数据结构
        if cpu_dic.get(row[0]):
            cpu_dic[row[0]].append(cpusyl)
        else:
            cpu_dic[row[0]] = [cpusyl]
    # 对字典进行处理，算出cpu使用率是否超出阈值
    for ip, cpulst in cpu_dic.items():
        # 计算平均使用率
        cpusum = sum(cpulst)
        cpuave = cpusum/len(cpulst)
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(ip,"get_cpu()","cpu")
        cur.execute( del_sql )
        # 登记到日常巡检表中 
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,ip,"get_cpu()","cpu",yz,cpuave)
        cur.execute( ins_sql )
        # 判断使用率是否超过阈值
        if cpuave >= float(yz):
            return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_cpu_ave(dwsj=5,yz=75)','cpu利用率分析','单位时间内不允许超过（含）设定的阈值','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'dwsj','单位时间,默认为5min','1','%s','True','5','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值,默认为百分之75','1','%s','True','75','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]


def cjxx_zb():
    nr ="""from cpos.esb.basic.busimodel.dictlog import tlog
import datetime
sql_data = {'table_name':'gl_cjjgb'.upper(),'bak_table_name':'gl_cjjgb_his'.upper(),'table_space':table_space.upper()}
with connection() as con:
    cur = con.cursor()
    # 查看历史表是否存在
    sql = \"\"\"select count(0) as count
    from dba_tables
    where table_name = :1 and owner = :2\"\"\"
    tlog.log_info( '验证历史表是否存在:%s' % sql )
    cur.execute(sql,[sql_data['bak_table_name'],sql_data['table_space']])
    rs = cur.fetchone()
    if len(rs) > 0 and rs[0] == 0:
        # 如果历史表不存在，创建历史表。
        sql_create = \"\"\"create table %(table_space)s.%(bak_table_name)s as
        select * from %(table_space)s.%(table_name)s where 1=0\"\"\" % ( sql_data )
        tlog.log_info( '历史表不存在，创建历史表:%s' % sql_create )
        cur.execute( sql_create )
    # 转移数据
    sql_data['qtsj'] = (datetime.datetime.now() - datetime.timedelta(days=int(N))).strftime("%Y%m%d")
    # 首先删除历史表已有的备份数据
    sql_del = \"\"\" delete from %(table_space)s.%(bak_table_name)s where 
                id  in ( select id from %(table_space)s.%(table_name)s
                        where substr(jlsj,1,8) < '%(qtsj)s' 
                        )\"\"\" % sql_data
    cur.execute( sql_del )
    tlog.log_info( '首先删除历史表已有的备份数据:%s' % sql_del )
    # 将符合条件的数据转移到历史表中
    sql_insert = \"\"\"insert into %(table_space)s.%(bak_table_name)s
                select * from %(table_space)s.%(table_name)s
                where substr(jlsj,1,8) < '%(qtsj)s'\"\"\" % sql_data
    cur.execute( sql_insert )
    tlog.log_info( '将符合条件的数据转移到历史表中:%s' % sql_insert )
    # 删除正式表中已转移的数据
    sql_delete = \"\"\"delete from %(table_space)s.%(table_name)s
                where substr(jlsj,1,8) < '%(qtsj)s'\"\"\" % sql_data
    cur.execute( sql_delete )
    tlog.log_info( '删除正式表中已转移的数据:%s' % sql_delete )
return True"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','cjxx_zb(N=7,table_space="TSYW")','采集信息数据转表','将信息采集表中N天前的数据打包存放到mangodb中','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'N','天数:默认将N天前的数据打包转表，默认为7','1','%s','True','7','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_space','数据表所在表空间，默认为TSYW','1','%s','True','TSYW','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
        
def comm_dete():
    nr = """import uuid
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = \"\"\"
        select ip, nr 
        from (
            select ip, nr, rownum rn
            from (
                select ip, nr
                from gl_cjjgb
                where cjmc = '%s'
                and zbbm = 'test_cominfcon(jym,bwzfj="utf8")'
                order by jlsj desc
            )
        )
        where rn <= %s
        \"\"\" %(jybm,dwsj_cs)
    cur.execute( sql )
    rs = cur.fetchall()
# 失败次数
sb_cs_tmp = 0
ip = ''
# 失败响应码列表
sb_xym_lst = sb_xym.split(',') if sb_xym else []
for row in rs:
    ip = row[0]
    nr = eval( row[1] )
    # 若用户传送了自己设置的失败响应信息，按照用户设置的统计
    if len(sb_xym_lst) >0:
        if nr.get('code') in sb_xym_lst:
            sb_cs_tmp += 1
    # 若用户没有设置自己的响应码，则按照非000000处理
    else:
        if nr.get('code') != '000000':
            sb_cs_tmp += 1
# 3.比较失败次数
if sb_cs_tmp >= int(sb_cs):
    # 登记到日常巡检表中 
    with connection() as con:
        cur = con.cursor()
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(ip,'test_cominfcon(jym,bwzfj="utf8")',jybm)
        cur.execute( del_sql )
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,ip,'test_cominfcon(jym,bwzfj="utf8")',jybm,sb_cs,sb_cs_tmp)
        cur.execute( ins_sql )
    return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','comm_dete(jybm,dwsj_cs,sb_cs,sb_xym="")','通讯探测','探测某一通讯的连通性，若超过（包含）设置的失败次数，则就预警。SYS_YFSDBW格式应该为：{"info":"\u4ea4\u6613\u6210\u529f","code": "000000"}','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'jybm','交易编码，配置是哪个通讯的','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'dwsj_cs','单位时间_次数，获取从当前时间开始统计到设置的单位时间次数','1','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sb_cs','通讯失败次数设置，不允许超过（包含）设置的通讯失败次数','1','%s','False','','3')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs4 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sb_xym','失败响应码,以‘,’分割，为空时只要响应码不是‘000000’，都默认为失败','1','%s','True','','4')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2,ins_crs3,ins_crs4]
    
def failtrans_count():
    nr = """import uuid
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = \"\"\"
        select ip, nr 
        from (
            select ip, nr, rownum rn
            from (
                select ip, nr
                from gl_cjjgb
                where cjmc = '%s'
                and zbbm = 'get_failtrans(jymlb,sbxymlb,min)'
                order by jlsj desc
            )
        )
        where rn = 1
        \"\"\" %(ywbm)
    cur.execute( sql )
    row = cur.fetchone()
if row and (int(row[1]) > int(fail_bs)):
    # 登记到日常巡检表中 
    with connection() as con:
        cur = con.cursor()
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_failtrans(jymlb,sbxymlb,min)',ywbm)
        cur.execute( del_sql )
        # 插入
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,row[0],'get_failtrans(jymlb,sbxymlb,min)',ywbm,fail_bs,row[1])
        cur.execute( ins_sql )
    return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','failtrans_count(ywbm,fail_bs)','交易失败笔数','检验某一业务下的交易失败笔数是否超过阈值','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'ywbm','业务编码，传递业务对象配置的对象编码','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'fail_bs','失败笔数，不允许超过该失败笔数','1','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
    
def firstrans_count():
    nr = """import datetime
# 获取当前日期
dqrq = datetime.datetime.now().strftime("%Y%m%d")
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = "select nr from gl_cjjgb where cjmc = '%s' and zbbm = 'get_firstrans(jymlb)' and substr(jlsj,1,8) = '%s' order by jlsj desc" %(ywbm,dqrq)
    cur.execute( sql )
    rs = cur.fetchall()
for row in rs:
    if int(row[0]) > 0:
        return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','firstrans_count(ywbm)','业务第一笔交易分析','校验业务下是否发起指定交易码的第一笔交易','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'ywbm','业务编码，传递业务对象配置的对象编码','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1]
    
def table_count():
    nr = """import uuid
# 将表名称转化为大写
table_name = table_name.upper()
# 若table_name没有加表空间，给其加上默认的表空间（特色业务管理平台表空间）
if '.' not in table_name:
    table_name = 'TSYW.'+table_name
# 获取采集结果表中最新的一条数据表的采集信息
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = \"\"\"
        select ip, nr 
        from (
            select ip, nr, rownum rn
            from (
                select ip, nr
                from gl_cjjgb
                where cjmc = '%s'
                and zbbm = 'get_tabinf(tab,tj="1=1",bkjmc="TSYW")'
                order by jlsj desc
            )
        )
        where rn = 1
        \"\"\" %(table_name)
    cur.execute( sql )
    row = cur.fetchone()
if row:
    if int(row[1]) >= int(yz):
        # 登记到日常巡检表中 
        with connection() as con:
            cur = con.cursor()
            # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
            del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_tabinf(tab,tj="1=1",bkjmc="TSYW")',table_name)
            cur.execute( del_sql )
            ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,row[0],'get_tabinf(tab,tj="1=1",bkjmc="TSYW")',table_name,yz,row[1])
            cur.execute( ins_sql )
        return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','table_count(table_name,yz)','数据表信息量','校验数据表信息量是否超过阈值','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_name','数据表名称，注意需要带表空间','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，设置最大允许数据表中的信息量的条数','1','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]

    
def collection_loss():
    """
    # 注意此函数目前暂时不实现，
    # 因为目前的数据采用的串行方式执行，一个采集执行完毕后等待N秒再执行下次采集，这种情况总时间是和每个采集执行时间息息相关的
    # 而原来设计时考虑要并行的，总时间和采集执行时间没关系，和发起频率有关
    # 所以目前暂不实现采集缺失率分析；
    """
    nr = """# 计算出前推时间
import uuid,datetime
dwsj = (datetime.datetime.now()-datetime.timedelta(seconds=int(dwsj_cs))).strftime("%Y%m%d%H%M%S")
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中相关的采集信息
    sql = "select count(0) count from gl_cjjgb where zbbm = '%s' and ip = '%s' and jlsj >= '%s' order by jlsj desc "%(col_name,ip,dwsj)
    # 获取该采集编码对应的频率，需计算正常的采集频率
    sql_pl = "select zdfqpz from gl_cjpzb where zbid = (select id from gl_jkzb where zbbm = '%s' ) and lx = '1' "%col_name
    cur.execute( sql )
    row = cur.fetchone()
    cur.execute( sql_pl )
    row2 = cur.fetchone()
    # 查询到数据
    if row and row2:
        # 计算正常频率 单位时间_传参/crontab配置
        nor_fra = int(dwsj_cs)/int(row2[0])
        # 计算是否超过阈值(采集丢失率计算：(正常频率-采集频率)/正常频率)
        if (float(nor_fra - int(row[0]) )/float(nor_fra))*100 > float(yz):
            # 登记到日常巡检表中 
            ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,ip,'采集丢失率分析',col_name,yz,'%d'%(float(nor_fra - int(row[0]) )/float(nor_fra)*100))
            cur.execute( ins_sql )
            return True
return False
"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','collection_loss(ip,col_name,dwsj_cs=300,yz=20)','采集丢失率分析','校验某一主机的指定采集指标在单位时间内的采集数据丢失率是否超过阈值','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'ip','主机IP','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'col_name','采集指标编码','1','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'dwsj_cs','单位时间_传参，单位为秒，默认为300秒','1','%s','True','300','3')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs4 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为百分之20','1','%s','True','20','4')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2,ins_crs3,ins_crs4]
    
def plan_task_into():
    nr = """import re, time, sys, datetime
import cpos.esb.basic.resource.rdb
from cpos.esb.basic.busimodel.dictlog import tlog
tlog.log_info('===================>>>>>>>>>计划任务展开')
#from Core.FDateTime.FDateTime import FDateTime

def get_struct_time(time_stamp_int):
    \"\"\"
    按整型时间戳获取格式化时间 分 时 日 月 周
    Args:
        time_stamp_int 为传入的值为时间戳(整形)，如：1332888820
        经过localtime转换后变成
        time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    Return:
        list____返回 分 时 日 月 周
    \"\"\"
    str_time = time.localtime(time_stamp_int)
    # 处理日期 星期信息：
    #   使用：tm_wday（weekday）0 - 6（0表示周日）
    #   正常：tm_wday（weekday）0 - 6（0表示周一）
    #   现在系统为“正常”，但是需要“使用”0 - 6（0表示周日）， 则人为的在原有的基础上加一
    tm_wday = str_time.tm_wday + 1 if str_time.tm_wday + 1 < 7 else 0
    return [str_time.tm_min, str_time.tm_hour, str_time.tm_mday, str_time.tm_mon, tm_wday]


def get_strptime(time_str, str_format):
    \"\"\"从字符串获取 整型时间戳
    Args:
        time_str 字符串类型的时间戳 如 '31/Jul/2013:17:46:01'
        str_format 指定 time_str 的格式 如 '%d/%b/%Y:%H:%M:%S'
    Return:
        返回10位整型(int)时间戳，如 1375146861
    \"\"\"
    return int(time.mktime(time.strptime(time_str, str_format)))

def get_str_time(time_stamp, str_format='%Y%m%d%H%M'):
    \"\"\"
    获取时间戳,
    Args:
        time_stamp 10位整型(int)时间戳，如 1375146861
        str_format 指定返回格式，值类型为 字符串 str
    Rturn:
        返回格式 默认为 年月日时分，如2013年7月9日1时3分 :201207090103
    \"\"\"
    return time.strftime("%s" % str_format, time.localtime(time_stamp))

def match_cont(patten, cont):
    \"\"\"
    正则匹配(精确符合的匹配)
    Args:
        patten 正则表达式
        cont____ 匹配内容
    Return:
        True or False
    \"\"\"
    res = re.match(patten, cont)
    if res:
        return True
    else:
        return False

def handle_num(val, ranges=(0, 100), res=list()):
    \"\"\"处理纯数字\"\"\"
    val = int(val)
    if val >= ranges[0] and val <= ranges[1]:
        res.append(val)
    return res

def handle_nlist(val, ranges=(0, 100), res=list()):
    \"\"\"处理数字列表 如 1,2,3,6\"\"\"
    val_list = val.split(',')
    for tmp_val in val_list:
        tmp_val = int(tmp_val)
        if tmp_val >= ranges[0] and tmp_val <= ranges[1]:
            res.append(tmp_val)
    return res

def handle_star(val, ranges=(0, 100), res=list()):
    \"\"\"处理星号\"\"\"
    if val == '*':
        tmp_val = ranges[0]
        while tmp_val <= ranges[1]:
            res.append(tmp_val)
            tmp_val = tmp_val + 1
    return res

def handle_starnum(val, ranges=(0, 100), res=list()):
    \"\"\"星号/数字 组合 如 */3\"\"\"
    tmp = val.split('/')
    val_step = int(tmp[1])
    if val_step < 1:
        return res
    #val_tmp = int(tmp[1])  # zlj 修改
    val_tmp = 0  # 每次都从0开始检索，分钟
    while val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res

def handle_range(val, ranges=(0, 100), res=list()):
    \"\"\"处理区间 如 8-20\"\"\"
    tmp = val.split('-')
    range1 = int(tmp[0])
    range2 = int(tmp[1])
    tmp_val = range1
    if range1 < 0:
        return res
    while tmp_val <= range2 and tmp_val <= ranges[1]:
        res.append(tmp_val)
        tmp_val = tmp_val + 1
    return res

def handle_rangedv(val, ranges=(0, 100), res=list()):
    \"\"\"处理区间/步长 组合 如 8-20/3 \"\"\"
    tmp = val.split('/')
    range2 = tmp[0].split('-')
    val_start = int(range2[0])
    val_end = int(range2[1])
    val_step = int(tmp[1])
    if (val_step < 1) or (val_start < 0):
        return res
    val_tmp = val_start
    while val_tmp <= val_end and val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res

def parse_conf(conf, ranges=(0, 100), res=list()):
    \"\"\"解析crontab 五个时间参数中的任意一个\"\"\"
    #去除空格，再拆分
    conf = conf.strip(' ').strip(' ')
    conf_list = conf.split(',')
    other_conf = []
    number_conf = []
    for conf_val in conf_list:
        #print('match_cont---',match_cont(PATTEN['number'], conf_val),PATTEN['number'],conf_val)
        if match_cont(PATTEN['number'], conf_val):
            #记录拆分后的纯数字参数
            number_conf.append(conf_val)
        else:
            #记录拆分后纯数字以外的参数，如通配符 * , 区间 0-8, 及 0－8/3 之类
            other_conf.append(conf_val)
    if other_conf:
        #处理纯数字外各种参数
        for conf_val in other_conf:
            for key, ptn in PATTEN.items():
                if match_cont(ptn, conf_val):
                    res = PATTEN_HANDLER[key](val=conf_val, ranges=ranges, res=res)
    if number_conf:
        if len(number_conf) > 1 or other_conf:
            #纯数字多于1，或纯数字与其它参数共存，则数字作为时间列表
            res = handle_nlist(val=','.join(number_conf), ranges=ranges, res=res)
        else:
            #只有一个纯数字存在，则数字为时间 间隔
            res = handle_num(val=number_conf[0], ranges=ranges, res=res)
    return res

def parse_crontab_time(conf_string):
    \"\"\"
    解析crontab时间配置参数
    Args:
        conf_string  配置内容(共五个值：分 时 日 月 周)
                     取值范围 分钟:0-59 小时:0-23 日期:1-31 月份:1-12 星期:0-6(0表示周日)
    Return:
    crontab_range     list格式，分 时 日 月 周 五个传入参数分别对应的取值范围
    \"\"\"
    time_limit    = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
    crontab_range = []
    clist = []
    conf_length = 5
    tmp_list = conf_string.split(' ')
    for val in tmp_list:
        if len(clist) == conf_length:
            break
        if val:
            clist.append(val)

    if len(clist) != conf_length:
        return -1, 'config error whith [%s]' % conf_string
    cindex = 0
    for conf in clist:
        res_conf = []
        res_conf = parse_conf(conf, ranges=time_limit[cindex], res=res_conf)
        if not res_conf:
            return -1, 'config error whith [%s]' % conf_string
        crontab_range.append(res_conf)
        cindex = cindex + 1
    return 0, crontab_range

def time_match_crontab(crontab_time, time_struct):
    \"\"\"
    将时间戳与crontab配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
    Args:
        crontab_time____crontab配置中的五个时间（分 时 日 月 周)参数对应时间取值范围
        time_struct____ 某个整型时间戳，如：1375027200 对应的 分 时 日 月 周
    Return:
    tuple 状态码, 状态描述
    \"\"\"
    cindex = 0
    for val in time_struct:
        if val not in crontab_time[cindex]:
            return 0, False
        cindex = cindex + 1
    return 0, True

def close_to_cron(crontab_time, time_struct):
    \"\"\"coron的指定范围(crontab_time)中 最接近 指定时间 time_struct 的值\"\"\"
    close_time = time_struct
    cindex = 0
    for val_struct in time_struct:
        offset_min = val_struct
        val_close = val_struct
        for val_cron in crontab_time[cindex]:
            offset_tmp = val_struct - val_cron
            if offset_tmp > 0 and offset_tmp < offset_min:
                val_close = val_struct
                offset_min = offset_tmp
        close_time[cindex] = val_close
        cindex = cindex + 1
    return close_time

def cron_time_list(
        cron_time,time_tmp
        
    ):
    \"\"\"
    获取crontab时间配置参数取值范围内的所有时间点 的 时间戳
    Args:
        cron_time 符合crontab配置指定的所有时间点
        year_num____指定在哪一年内 获取
        limit_start 开始时间
    Rturn:
        List  所有时间点组成的列表(年月日时分 组成的时间，如2013年7月29日18时56分：201307291856)
    \"\"\"
    
    year_num=int(get_str_time(time_tmp, "%Y"))
    limit_start=get_str_time(time_tmp, "%Y%m%d%H%M")
    limit_end=get_str_time(time_tmp + 86400, "%Y%m%d%H%M")    
    #按小时 和 分钟组装
    hour_minute = []
    for minute in cron_time[0]:
        minute = str(minute)
        if len(minute) < 2:
            minute = '0%s' % minute
        for hour in cron_time[1]:
            hour = str(hour)
            if len(hour) < 2:
                hour = '0%s' % hour
            hour_minute.append('%s%s' % (hour, minute))
    #按天 和 小时组装
    day_hm = []
    for day in cron_time[2]:
        day = str(day)
        if len(day) < 2:
            day = '0%s' % day
        for hour_mnt in hour_minute:
            day_hm.append('%s%s' % (day, hour_mnt))
    #按月 和 天组装
    month_dhm = []
    #只有30天的月份
    month_short = ['02', '04', '06', '09', '11']
    for month in cron_time[3]:
        month = str(month)
        if len(month) < 2:
            month = '0%s' % month
        for day_hm_s in day_hm:
            if month == '02':
                if (((not year_num % 4 ) and (year_num % 100)) or (not year_num % 400)):
                    #闰年2月份有29天
                    if int(day_hm_s[:2]) > 29:
                        continue
                else:
                    #其它2月份有28天
                    if int(day_hm_s[:2]) > 28:
                        continue
            if month in month_short:
                if int(day_hm_s[:2]) > 30:
                    continue
            month_dhm.append('%s%s' % (month, day_hm_s))
    #按年 和 月组装
    len_start = len(limit_start)
    len_end = len(limit_end)
    month_dhm_limit = []
    for month_dhm_s in month_dhm:
        time_ymdhm = '%s%s' % (str(year_num), month_dhm_s)
        #开始时间\结束时间以外的排除
        if (int(time_ymdhm[:len_start]) < int(limit_start)) or \
         (int(time_ymdhm[:len_end]) > int(limit_end)):
            continue
        month_dhm_limit.append(time_ymdhm)
    if len(cron_time[4]) < 7:
        #按不在每周指定时间的排除
        month_dhm_week = []
        for time_minute in month_dhm_limit:
            str_time = time.strptime(time_minute, '%Y%m%d%H%M%S')
            # 处理日期 星期信息：
            #   使用：tm_wday（weekday）0 - 6（0表示周日）
            #   正常：tm_wday（weekday）0 - 6（0表示周一）
            #   现在系统为“正常”，但是需要“使用”0 - 6（0表示周日）， 则人为的在原有的基础上加一
            tm_wday = str_time.tm_wday + 1 if str_time.tm_wday + 1 < 7 else 0
            if tm_wday in cron_time[4]:
                month_dhm_week.append(time_minute)
        return month_dhm_week
    return month_dhm_limit


#crontab时间参数各种写法 的 正则匹配
PATTEN = {
    #纯数字
    'number':'^[0-9]+$',
    #数字列表,如 1,2,3,6
    'num_list':'^[0-9]+([,][0-9]+)+$',
    #星号 *
    'star':'^\*$',
    #星号/数字 组合，如 */3
    'star_num':'^\*\/[0-9]+$',
    #区间 如 8-20
    'range':'^[0-9]+[\-][0-9]+$',
    #区间/步长 组合 如 8-20/3
    'range_div':'^[0-9]+[\-][0-9]+[\/][0-9]+$'
    #区间/步长 列表 组合，如 8-20/3,21,22,34
    #'range_div_list':'^([0-9]+[\-][0-9]+[\/][0-9]+)([,][0-9]+)+$'
    }
#各正则对应的处理方法
PATTEN_HANDLER = {
    'number':handle_num,
    'num_list':handle_nlist,
    'star':handle_star,
    'star_num':handle_starnum,
    'range':handle_range,
    'range_div':handle_rangedv
}


def isdo(strs,tips=None):
    \"\"\"
    判断是否匹配成功！
    \"\"\"
    try:
        tips = tips==None and "文件名称格式错误：job_月-周-天-时-分_文件名.txt" or tips
        timer = strs.replace('@',"*").replace('%','/').split('_')[1]
        month,week,day,hour,mins = timer.split('-')
        conf_string = mins+" "+hour+" "+day+" "+month+" "+week
        res, desc = parse_crontab_time(conf_string)
        if res == 0:
            cron_time = desc
        else:
            return False

#        now =FDateTime.now()
#        now = FDateTime.datetostring(now, "%Y%m%d%H%M00")
#
#        time_stamp = FDateTime.strtotime(now, "%Y%m%d%H%M00")
#
        time_stamp = int(time.time())
        #解析 时间戳对应的 分 时 日 月 周
        time_struct = get_struct_time(time_stamp)
        match_res = time_match_crontab(cron_time, time_struct)
        return match_res[1]
        #return 0
    except:
        return False

def main(conf_string, rq=None, sj=None):
    \"\"\"测试用实例\"\"\"
    #crontab配置中一行时间参数
    #conf_string = '*/10 * * * * (cd /opt/pythonpm/devpapps; /usr/local/bin/python2.5 data_test.py>>output_error.txt)'
    #conf_string = '*/10 * * * *' # 每隔10分钟发起一次
    #conf_string = '10 * * * *'   # 每小时第10分钟发起
    #conf_string = '30 21 * * * '  # 每晚的21:30
    #conf_string = '10,20,30,40,50,00 * * * *'   # 10分钟发起
    #conf_string = '10 8,10,20 * * * *'   # 指定小时发起（8:10，10:10）
    #conf_string = '45 4 1,4,10,22 * *'   # 每月1、4,10、22日的4 : 45
    #conf_string = '10 1 * * 2,6,0'  # 每周六、周日的1 : 10
    #conf_string = '0,30 18-23 * * *' # 每天18 : 00至23 : 00之间每隔30分钟
    #conf_string = '0 23 * * 1' #每星期二的11 : 00 
    #conf_string = '* */1 * * *' # 每一小时
    #conf_string = '0 11-19/1 * * *' # 11点到19点之间，每隔一小时
    #conf_string = '0 11 4 * 0-2' #每月的4号与每周一到周三的11点
    #conf_string = '0 4 4 3 * ' # 一月一号的4点
    #conf_string = '*/15 8-16,3 * * *' # 
    
    now = time.time()
    rq = rq or get_str_time(now, str_format='%Y%m%d')
    sj = sj or '0000'
    timearray = time.strptime(rq+sj, "%Y%m%d%H%M")
    time_stamp = int(time.mktime(timearray))
    #解析crontab时间配置参数 分 时 日 月 周 各个取值范围
    res, desc = parse_crontab_time(conf_string)
    if res == 0:
        cron_time = desc
    else:
        sys, exit(-1)

    #解析 时间戳对应的 分 时 日 月 周
    time_struct = get_struct_time(time_stamp)

    #将时间戳与crontab配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
    match_res = time_match_crontab(cron_time, time_struct)

    #crontab配置设定范围中最近接近时指定间戳的一组时间
    most_close = close_to_cron(cron_time, time_struct)
    time_list = cron_time_list(cron_time,time_stamp)
    time_list.sort()
    return time_list
    
def crontab_cj(ct, rq=None, sj=None):
    \"\"\"
    # 对crontab拆解
    # 根据传入的日期和时间进行拆分，若传入的时间为空，则默认从指定日期的当前时间拆分到指定日期的24点；
    # 若传入的时间不为空，则从指定日期指定时间拆分到指定日。
    # ct: crontab字符串
    # rq: 开始日期YYYYmmdd，默认为当前日期
    # sj: 开始时间HHMM，默认为当前时间
    \"\"\"
    limit_end = datetime.datetime.now().strftime('%Y%m%d') + '235959'
    if rq:
        limit_end = rq + '235959'
    return [k[8:12] for k in main(ct, rq, sj) if k <= limit_end]

def man_____():
    import uuid
    # 获取次日时间
    crrq = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y%m%d")
    try:
        with connection() as con:
            cur = con.cursor()
            # 校验当日计划表中是否已有次日数据
            sql_jy = "select count(0) from gl_drzxjhb where rq = '%s'"%crrq
            cur.execute( sql_jy )
            r = cur.fetchone()
            if not r:
                return False
            # 检索计划任务表，获取所有状态为启用的任务
            sql = "select id, zdfqpz, zdfqpzsm, rwlx, ssid, ip, sfkbf from gl_jhrwb where zt = '1'"
            cur.execute( sql )
            rs = cur.fetchall()
            # 循环数据列表，依次解析crontab，拆分出次日的任务
            for row in rs:
                # 先删除，防止重复操作
                sql_del = " delete from gl_drzxjhb where ssid = '%s' and rq = '%s' and zt = '0' " % ( row[0], crrq )
                cur.execute( sql_del )
                # 获取时间戳
                cron_lst = crontab_cj(row[1],crrq,"0000")
                # 插入信息
                for cron in cron_lst:
                    from ops.core.rdb_jr import get_lsh2con
                    # 流水号应为 日期yyyymmddhhmmss+六位递增数 需与核心登记一致
                    xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000, con = con )
                    lsh = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
                    ins_sql = "insert into gl_drzxjhb (id,lsh,rwlx,ssid,zdfqpz,ip,rq,jhfqsj,zt,sfkbf) values( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '0', '%s' )"%(uuid.uuid4().hex,lsh,row[3],row[0],row[1],row[5] if row[5] else '',crrq,cron,row[6] if row[6] else '0') # todo 流水号应为 日期yyyymmddhhmmss+六位递增数 需与核心登记一致
                    cur.execute( ins_sql )
        return True
    except:
        import sys,traceback
        e = sys.exc_info()
        lst = traceback.format_exception( *e )
        from cpos.esb.basic.busimodel.dictlog import tlog
        tlog.log_info( "抛出异常:[%s]", ( '\\n'.join( lst ) ) )
        return False
return man_____()"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','plan_task_into()','计划任务展开','将计划任务展开插入到当日执行计划表中，执行成功，返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}]]
    
def get_mem_use():
    nr = """import uuid,datetime
# 获取当天日期
rq = datetime.datetime.now().strftime("%Y%m%d")
with connection() as con:
    cur = con.cursor()
    # 检索采集结果表，获取当天每台主机最新一条内存采集信息
    sql = \"\"\"
            select a.ip, a.nr 
            from gl_cjjgb a ,
            (
                select max(jlsj) as jlsj, ip
                from gl_cjjgb
                where substr(jlsj,1,8) = '%s'
                and cjmc = 'ncsy' 
                group by ip ) b
            where a.ip = b.ip 
            and a.cjmc = 'ncsy'
            and a.jlsj = b.jlsj
            order by ip
        \"\"\"%rq
    cur.execute( sql )
    rs = cur.fetchall()
    # 将数据列表转换为字典
    jx_dic = {}
    # 循环处理各个主机信息
    for r in rs:
        # 处理每一行信息
        ncxx = r[1].split('\\n')
        ncxx_dic = {}
        for nc in ncxx:
            # 处理每一行中信息，将汉字替换
            clh = nc.replace('物理内存已使用','').replace('交换分区已使用','').replace('虚拟内存总大小','').replace('虚拟内存已使用','')
            if '物理内存已使用' in nc:
                ncxx_dic['p_use'] = clh[:clh.find(',')]
                ncxx_dic['p_un_use'] = clh[clh.find('未使用'):].replace('未使用','')
            if '交换分区已使用' in nc: 
                ncxx_dic['s_use'] = clh[:clh.find(',')]
                ncxx_dic['s_un_use'] = clh[clh.find('未使用'):].replace('未使用','')
            if '虚拟内存总大小' in nc:
                ncxx_dic['v_total'] = clh
            if '虚拟内存已使用' in nc:
                ncxx_dic['v_use'] = clh
        jx_dic[r[0]] = ncxx_dic
    # 循环字典，计算每一个主机IP是否有超出设定的阈值
    flag = 0
    for ip,cjxx in jx_dic.items():
        # 比对物理内存是否超过阈值 当前物理内存阈值 = (float(物理内存已使用)/(物理内存已使用+未使用))*100
        dqwlncyz = (float(cjxx.get('p_use','0'))/(float(cjxx.get('p_use','0'))+float(cjxx.get('p_un_use','0'))))*100
        # 登记到日常巡检表中
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(ip,'get_ram()','内存使用率')
        cur.execute( del_sql )
        # 插入
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%.2f')"%(uuid.uuid4().hex,ip,'get_ram()','内存使用率',p_use,dqwlncyz)
        cur.execute( ins_sql )
        if dqwlncyz >= float(p_use):
            flag = 1
        # 比对虚拟内存是否超过阈值 当前虚拟内存阈值 = (float(虚拟内存已使用)/(虚拟内存总大小))*100
        dqxnncyz = (float(cjxx.get('v_use','0'))/float(cjxx.get('v_total','0')))*100
        if dqxnncyz >= float(v_use):
            flag = 1
        # 比对交换分区是否超过阈值 当前交换分区阈值 = (float(交换分区已使用)/(交换分区已使用+未使用))*100
        dqjhfqyz = (float(cjxx.get('s_use','0'))/(float(cjxx.get('s_use','0'))+float(cjxx.get('s_un_use','0'))))*100
        if dqjhfqyz >= float(s_use):
            flag = 1
    if flag == 1:
        return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_mem_use(p_use=60,v_use=60,s_use=60)','内存使用率分析','获取内存使用率，若物理内存/虚拟内存/交换分区的使用率其中有一项超过（含）百分之60，则返回TRUE','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'p_use','物理内存使用率，默认为百分之60,若超过（含）60,则返回True','1','%s','True','60','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'v_use','虚拟内存使用率','1','%s','True','60','2')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 's_use','交换分区使用率','1','%s','True','60','3')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2,ins_crs3]
    
def get_io_use():
    nr = """import uuid,datetime
# 获取当前日期时间
dqrqsj = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# 根据获取的当前时间往前推单位时间的记录时间
qtsj = (datetime.datetime.strptime(dqrqsj,"%Y%m%d%H%M%S") - datetime.timedelta(minutes=int(dwsj))).strftime("%Y%m%d%H%M%S")
with connection() as con:
    cur = con.cursor()
    # 获取采集结果表中信息
    sql = "select ip, nr from gl_cjjgb where cjmc = 'io' and jlsj >= '%s' order by jlsj, ip" %qtsj
    cur.execute( sql )
    rs = cur.fetchall()
    # 定义数据结构 {(主机ip,磁盘名称(例如：sdb)):[io繁忙率值1，io繁忙率值2]}
    fml_dic = {} 
    for r in rs:
        # 获取每一个磁盘IO信息
        cpxx_lst = r[1].split('\\n')
        for cpxx in cpxx_lst:
            if cpxx:
                # 分解结构，后续使用
                cpxxlb = cpxx.split(':')
                cpmc = cpxxlb[0].strip()
                if fml_dic.get((r[0],cpmc)):
                    fml_dic[(r[0],cpmc)].append(float(cpxxlb[1].strip()[:-1]))
                else:
                    fml_dic[(r[0],cpmc)] = [float(cpxxlb[1].strip()[:-1])]
    flag = 0
    for key in fml_dic.keys():
        # 计算每台主机每个磁盘的平均繁忙率 (float(数据字典1[key]之和)/len(数据字典1[key]))
        tmp_fml = (sum(fml_dic[key])/len(fml_dic[key]))
        # 登记到日常巡检表中 
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(key[0],'get_io()',key[1])
        cur.execute( del_sql )
        # 插入
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%.2f')"%(uuid.uuid4().hex,key[0],'get_io()',key[1],yz,float(tmp_fml))
        cur.execute( ins_sql )
        if tmp_fml >= float(yz):
            flag = 1
    if flag == 1:
        return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_io_use(dwsj=15,yz=70)','I/O磁盘繁忙率分析','若单位时间内的平均繁忙率超出（含）阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'dwsj','单位时间，默认为15min','1','%s','True','15','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为百分之70','1','%s','True','70','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
    
def get_filesystem_use():
    nr = """import uuid,datetime
str_filesystem = "filesystem"+filesystem
rq = datetime.datetime.now().strftime("%Y%m%d")
with connection() as con:
    cur = con.cursor()
    # 检索采集结果表信息
    sql = \"\"\"
            select a.ip, a.nr 
            from gl_cjjgb a,
            (
                select max(jlsj) as jlsj, ip
                from gl_cjjgb
                where substr(jlsj,1,8) = '%s'
                and cjmc = '%s' 
                group by ip ) b
            where a.ip = b.ip
            and a.cjmc = '%s' 
            and a.jlsj = b.jlsj
            order by ip
        \"\"\"%(rq,str_filesystem,str_filesystem)
    cur.execute( sql )
    rs = cur.fetchall()
    flag = 0
    for row in rs:
        # 对内容进行处理，取最后一个阈值,内容格式：/dev/mapper/vg_sj236-lv_root|51606140|9038056|39946644|19%|
        lst = row[1].split('|')
        act_yz = lst[-1][:-1] if '%' in lst[-1] else lst[-2][:-1]
        # 登记到日常巡检表中
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_filesystem()',filesystem)
        cur.execute( del_sql )
        # 插入
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,row[0],'get_filesystem()',filesystem,yz,act_yz)
        cur.execute( ins_sql )
        if float(act_yz) >= float(yz):
            flag = 1
if flag == 1:
    return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_filesystem_use(filesystem,yz=70)','文件系统使用率','若指定的文件系统超出（含）阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'filesystem','文件系统','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为百分之70','1','%s','True','70','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
                
def get_virtual_use():
    nr = """import uuid,datetime
# 获取当天日期
dqrq = datetime.datetime.now().strftime('%Y%m%d')
# 计算出昨天日期
zrrq = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y%m%d')
with connection() as con:
    cur = con.cursor()
    # 查询今天的虚拟内存
    sql_dt = "select ip, nr from gl_cjjgb where substr(jlsj,1,8) = '%s' and cjmc = 'virtual' "%dqrq
    # 查询昨天的虚拟内存
    sql_zt = "select ip, nr from gl_cjjgb where substr(jlsj,1,8) = '%s' and cjmc = 'virtual' "%zrrq
    cur.execute( sql_dt )
    rs = cur.fetchall()
    cur.execute( sql_zt )
    rs2 = cur.fetchall()
    t_v_dic = {}  # 存当天使用虚拟内容情况 {主机IP：[今天的虚拟内存累计相加之和,今天虚拟内存个数]}
    y_v_dic = {}  # 存昨天使用虚拟内容情况 {主机IP：[昨天的虚拟内存累计相加之和,昨天虚拟内存个数]}
    # 对结果集进行转换 内容格式为：虚拟内存已使用308696
    for row in rs:
        ysync = row[1].replace('虚拟内存已使用','')
        if t_v_dic.get(row[0]):
            t_v_dic[row[0]][0] = t_v_dic[row[0]][0] + float(ysync)
            t_v_dic[row[0]][1] = t_v_dic[row[0]][1] + 1
        else:
            t_v_dic[row[0]] = [float(ysync),1]
    for row in rs2:
        ysync = row[1].replace('虚拟内存已使用','')
        if y_v_dic.get(row[0]):
            y_v_dic[row[0]][0] = y_v_dic[row[0]][0] + float(ysync)
            y_v_dic[row[0]][1] = y_v_dic[row[0]][1] + 1
        else:
            y_v_dic[row[0]] = [float(ysync),1]
    # 循环结果集,并查看是否超过阈值
    flag = 0
    for ip, xnnc_lst in t_v_dic.items():
        # 对于昨日未获取到的采集信息，跳过
        if not y_v_dic.get(ip):
            continue
        # 计算虚拟内存日增长率（今天-昨天/昨天）
        t_v = xnnc_lst[0]/xnnc_lst[1]
        y_v = y_v_dic[ip][0]/y_v_dic[ip][1]
        v_da_r = (float(t_v - y_v)/y_v)*100
        # 登记到日常巡检表中 
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(ip,'get_virtual()','virtual')
        cur.execute( del_sql )
        # 插入信息
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%.2f')"%(uuid.uuid4().hex,ip,'get_virtual()','virtual',yz,v_da_r)
        cur.execute( ins_sql )
        if float(v_da_r) >= float(yz):
            flag = 1
    if flag == 1:
        return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_virtual_use(yz=15)','虚拟内存日增长率','虚拟内存日增长率分析：今天的平均虚拟内存使用情况-昨天平均虚拟内存使用情况/昨天平均虚拟内存使用情况，若虚拟内存日增长率超出（含）阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为百分之15','1','%s','True','15','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1]

def get_bkjsyl_use():
    nr = """import uuid,datetime
# 获取当天日期
rq = datetime.datetime.now().strftime("%Y%m%d")
with connection() as con:
    cur = con.cursor()
    # 检索采集结果表信息
    sql = \"\"\"
            select a.ip, a.nr 
            from gl_cjjgb a,
            (
                select max(jlsj) as jlsj, ip
                from gl_cjjgb
                where substr(jlsj,1,8) = '%s'
                and cjmc = '%s'
                and zbbm = '%s'
                group by ip ) b
            where a.ip = b.ip
            and a.zbbm = '%s'
            and a.jlsj = b.jlsj
            order by ip
        \"\"\"%(rq,table_space,'get_bkjsyl(bkjmc="TSYW")','get_bkjsyl(bkjmc="TSYW")')
    cur.execute( sql )
    row = cur.fetchone()
    if row:
        conversation_lst = eval(row[1]) if row[1] else ''
        act_table_s = conversation_lst[3].replace( '%', '' ) if conversation_lst[3] else '0'
        # 登记到日常巡检表中
        # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
        del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_bkjsyl(bkjmc="TSYW")','数据库表空间使用率')
        cur.execute( del_sql )
        # 插入
        ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,row[0],'get_bkjsyl(bkjmc="TSYW")','数据库表空间使用率',yz,act_table_s)
        cur.execute( ins_sql )
        if float(act_table_s) >= float(yz):
            return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_bkjsyl_use(yz=80,table_space="TSYW")','数据库表空间使用率','若数据库表空间超出（含）阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为百分之80','1','%s','True','80','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_space','表空间，默认为：特色业务管理平台表空间','1','%s','True','TSYW','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
    
def get_conversation_use():
    nr = """import uuid,datetime
# 获取当天日期
rq = datetime.datetime.now().strftime("%Y%m%d")
content = {}
with connection() as con:
    cur = con.cursor()
    # 检索采集结果表信息
    sql = \"\"\"
            select a.ip, a.nr 
            from gl_cjjgb a,
            (
                select max(jlsj) as jlsj, ip
                from gl_cjjgb
                where substr(jlsj,1,8) = '%s'
                and cjmc = 'get_conversation'
                group by ip ) b
            where a.ip = b.ip
            and a.cjmc = 'get_conversation'
            and a.jlsj = b.jlsj
            order by ip
        \"\"\"%(rq)
    cur.execute( sql )
    row = cur.fetchone()
    if row:
        content = eval(row[1]) if row[1] else ''
        content = dict( [ ( obj['username'], obj['count'] ) for obj in content ] )
        act_sess = 0
        # 若username有值，则会话数act_sess = 指定username的会话数
        if username:
            act_sess = content.get(username,0)
        # 若username没值，则会话数act_sess = content中的会话数之和
        else:
            act_sess = sum([float(x) for x in content.values()])
        if float(act_sess) >= float(yz):
            # 登记到日常巡检表中
            # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
            del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc is null"%(row[0],'get_conversation()')
            if username:
                del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_conversation()',username)
            cur.execute( del_sql )
            # 插入
            ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,row[0],'get_conversation()',username,yz,act_sess)
            cur.execute( ins_sql )
            return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_conversation_use(yz=100,username="")','Oracle活动会话数','若会话数超出（含）阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'yz','阈值，默认为100(若超过100个会话数（含），则返回True','1','%s','True','100','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'username','用户名称，若没有，统计的是全部的会话数','1','%s','True','','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2]
    
def get_zxsj_use():
    nr = """import uuid,datetime
rq = datetime.datetime.now().strftime("%Y%m%d")
content = []
with connection() as con:
    cur = con.cursor()
    # 检索采集结果表信息
    sql = \"\"\"
            select a.ip, a.nr 
            from gl_cjjgb a,
            (
                select max(jlsj) as jlsj, ip
                from gl_cjjgb
                where substr(jlsj,1,8) = '%s'
                and zbbm = 'get_zxsj()' 
                group by ip ) b
            where a.ip = b.ip
            and a.jlsj = b.jlsj
            and a.zbbm = 'get_zxsj()'
            order by ip
        \"\"\"%(rq)
    cur.execute( sql )
    row = cur.fetchone()
    if row:
        content = eval(row[1])
        # 由微秒换算成秒
        us = float(content[1])/1000/1000
        if us >= float(zxsj):
            # 登记到日常巡检表中
            # 先删除后，再进行插入（ jkzj_ip + jkdxlx + dxmc  总是保存最新的 ）
            del_sql = "delete from gl_rcxjjgb where jkzj_ip = '%s' and jkdxlx = '%s' and dxmc = '%s'"%(row[0],'get_zxsj()','sql执行时间')
            cur.execute( del_sql )
            # 插入
            ins_sql = "insert into gl_rcxjjgb(id,jkzj_ip,jkdxlx,dxmc,yz,jkqk) values('%s','%s','%s','%s','%s','%.2f')"%(uuid.uuid4().hex,row[0],'get_zxsj()','sql执行时间',zxsj,us)
            cur.execute( ins_sql )
            return True
return False"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','get_zxsj_use( zxsj=300 )','Sql执行时间','若sql执行时间超出阈值，则返回True','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'zxsj','执行时间，单位秒，默认为300秒(若sql执行时间超过300秒（含），则返回True','1','%s','True','300','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1]

def remove_file():
    nr = """import os,datetime
from cpos.esb.basic.busimodel.dictlog import tlog
tlog.log_info( '===>>清理指定目录下文件开始：wjml[%s],wjmc[%s],rqcz[%s],space_num[%s]' % ( wjml, wjmc, str(rqcz), str(space_num) ) )
# 对日期差值进行转换为int型
rqcz = int(rqcz)
# 对操作天数进行转换为int型
space_num = int('1' if space_num == '0' or space_num == 0 else space_num)
# 获取当前日期
dqrq = datetime.datetime.now().strftime('%Y%m%d')
#如果文件名称中存在时间格式，则进行处理，不存在，则直接删除文件
clwjm_lst = [wjmc]
if wjmc.find( '%Y%m%d' ) >= 0:
    clwjm_lst = []
    for i in range(space_num):
        delta = rqcz + i
        wjm = (datetime.datetime.strptime(dqrq,'%Y%m%d') - datetime.timedelta(days= delta )).strftime(wjmc)
        clwjm_lst.append( wjm )
# 删除文件
for cz_wjm in clwjm_lst:
    zxml = "rm %s" % os.path.join( wjml,cz_wjm )
    tlog.log_info( '执行删除文件命令：%s' % ( zxml ) )
    try:
        os.system( zxml )
    except:
        tlog.log_info( '删除出现异常：%s' % ( traceback.format_exc() ) )

return True"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj) values('%s','remove_file(wjml,wjmc,rqcz=0,space_num=0)','清理指定目录指定格式文件','eg:wjmc：如字段说明|rqcz：1|space_num：2.如果当前日期为20151003，清理数据：eg_20151002_*.txt,eg_20151001_*.txt','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)
    
    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""
    
    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'wjml','文件目录','1','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '"""+ uuid.uuid4().hex +"""', 'wjmc','文件名称(eg:test_%Y%m%d_*.txt)','1','"""+ hsxxid +"""','False','','2')"""
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'rqcz','删除前几天的数据(大于等于零的数字)','1','%s','True','0','3')"""%(uuid.uuid4().hex,hsxxid)
    ins_crs4 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'space_num','删除前几天再向前推几天内的数据(大于等于零的数字)','1','%s','True','0','4')"""%(uuid.uuid4().hex,hsxxid)
    
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}],ins_crs1,ins_crs2,ins_crs3,ins_crs4]

def round_reverse():
    nr = """# 轮循检索出可发起冲正信息
import datetime
from cpos.esb.basic.busimodel.dictlog import tlog
from ops.core.rpc import send_jr

tlog.log_info('===================>>>>>>>>>循检索出可发起冲正信息')
# 当前日期
now_date = datetime.datetime.now().strftime('%Y%m%d')
with connection() as con:
    cur = con.cursor()
    # 查询：YWZJ_IP 业务主机hostname
    sql_ip = " select value from gl_csdy where lx = '1' and csdm = 'YWZJ_IP' "
    cur.execute( sql_ip )
    rs_ip = cur.fetchone()
    hostname = ''
    if rs_ip:
        hostname = rs_ip[0]
        tlog.log_info( '===================>>>>>>>>>业务主机hostname：%s' % hostname )
    else:
        tlog.log_info( '===================>>>>>>>>>系统未定义业务主机hostname' )
        return False
    
    # 查询：CZ_COUNT_MAX 冲正最大笔数
    sql_ip = " select value from gl_csdy where lx = '1' and csdm = 'CZ_COUNT_MAX' "
    cur.execute( sql_ip )
    rs_ip = cur.fetchone()
    cz_count_max = 100
    if rs_ip:
        cz_count_max = int( rs_ip[0] )
        tlog.log_info( '===================>>>>>>>>>冲正最大笔数：%s' % str(cz_count_max) )
    else:
        # 新增 冲正最大笔数
        sql_insert = "insert into gl_csdy (id,csdm,csms,value,lx,zt,ly) values( 'CZ_COUNT_MAX', 'CZ_COUNT_MAX', '冲正最大笔数', '100', '1','1','2' )"
        cur.execute( sql_insert )
        tlog.log_info( "===================>>>>>>>>>冲正最大笔数未定义新增：%s " % sql_insert )
    
    # 计算符合条件的冲正流水
    sql = " select ylsh, czlsh, rq, cs from jy_cz where rq = '%s' and cs < 3 and zt = '0' order by ylsh" % now_date
    cur.execute( sql )
    rs = cur.fetchall()
    for obj in rs[:cz_count_max]:
        # 原流水号
        ylsh = obj[0]
        tlog.log_info( "冲正操作，原流水号:[%s]"  % str( ylsh ) )
        # 判断原交易流水状态是否为：10交易失败 98冲正失败 88异常
        sql_jyls = " select count(1) from jy_ls where jyrq = '%s' and lsh = %s and zt in ( '10', '98', '88' ) " % ( obj[2], str( ylsh ) )
        rs = cur.execute( sql_jyls ).fetchone()
        if rs[0] > 0:
            # 对应原交易流水状态非正常
            tlog.log_info( "原交易流水[%s]状态为：10交易失败 或 98冲正失败 或 88异常"  % str( ylsh ) )
            # 冲正流水号
            czlsh = obj[1] if obj[1] else ''
            content = { "ylsh": ylsh,"czlsh": czlsh }
            source = 'cz'
            # 更新流水状态为冲正中
            sql_upd = " update jy_cz set zt = '1' where rq = '%s' and ylsh = %s " % ( now_date, str( ylsh ) )
            cur.execute( sql_upd )
            # 调用函数发起冲正
            tlog.log_info( "===================>>>>>>>>>调用send_jr传入信息content：%s " % str( content ) )
            result_msg = send_jr( content, hostname, source )
            tlog.log_info( "===================>>>>>>>>>调用send_jr返回值：%s " % str( result_msg ) )
        else:
            tlog.log_info( "原交易流水[%s]状态非：10交易失败 或 98冲正失败 或 88异常 或未找到对应的原交易" % str( ylsh ) )
            # 更新冲正流水次数
            cs = obj[3] + 1
            zt = '9' if cs >= 3 else '0'
            sql_upd = " update jy_cz set cs = %d, zt = '%s' where rq = '%s' and ylsh = %s " % ( cs, zt, now_date, str( ylsh ) )
            tlog.log_info( "更新冲正流水状态：%s" % sql_upd )
            cur.execute( sql_upd )
        
    return True"""
    
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj) values('%s','round_reverse()','轮循检索出可发起冲正信息','轮循检索出可发起冲正信息','%s','1','1','gz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)
    
    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','','',:nr)"""
    
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr)}]]

if __name__=='__main__':
    lst = []
    lst += get_cpu_ave()
    lst += cjxx_zb()
    lst += comm_dete()
    lst += failtrans_count()
    lst += firstrans_count()
    lst += table_count()
    # 暂时不实现，目前的间隔采集方式不适用
    #lst += collection_loss()
    lst += plan_task_into()
    lst += get_mem_use()
    lst += get_io_use()
    lst += get_filesystem_use()
    lst += get_virtual_use()
    lst += get_bkjsyl_use()
    lst += get_conversation_use()
    lst += get_zxsj_use()
    lst += remove_file()
    lst += round_reverse()
    with Get_cursor() as cursor:
        sql = "select id from gl_hsxxb where hsmc in ('get_cpu_ave(dwsj=5,yz=75)','get_virtual_use(yz=15)')"
        cursor.execute(sql)
        rs = cursor.fetchall()
        count = cursor.rowcount
        if count > 0:
            print ("数据库中已存在预置分析规则函数，不允许再次导入")
        else:
            print ("预置分析规则导入开始...")
            for sql in lst:
                if isinstance(sql,list):
                    cursor.execute(sql[0],sql[1])
                else:
                    cursor.execute(sql)
            print ("预置分析规则导入结束...")
            # 注意此文件添加的分析规则为空，如果有变动唯一码会有值，那也能启动wym的作用
