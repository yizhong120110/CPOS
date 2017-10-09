# -*- coding: utf-8 -*-
# 获取短信的机构代码和短信文件存放目录还未完成。
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
    
def excute_cmd():
    nr ="""from cpos.esb.basic.busimodel.dictlog import tlog
tlog.log_info('=================>>>>>执行系统命令开始')
import os
try:
    tlog.log_info('执行命令：[%s]' % str(cmd))
    os.system(cmd)
    tlog.log_info('执行命令完成')
except:
    import sys,traceback
    e = sys.exc_info()
    lst = traceback.format_exception( *e )
    tlog.log_info( "抛出异常:[%s]", ( '\\n'.join( lst ) ) )"""
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)
    values('%s','exec_syscmd(cmd)','执行系统命令','执行系统命令，如重启进程、停止进程等。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'cmd','要执行的系统命令','2','%s','True','','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1]
   
def tab_change():
    nr = """
with connection() as con:
    sql_data = {'table_name':table_name.upper(),'bak_table_name':bak_table_name.upper(),'sel_que':sel_que.upper(),'table_space':table_space.upper()}
    cur = con.cursor()
    # 查看历史表是否存在
    sql = \"\"\"select count(0) as count
    from dba_tables
    where table_name = :1 and owner = :2\"\"\"
    cur.execute(sql,[sql_data['bak_table_name'],sql_data['table_space']])
    rs = cur.fetchone()
    if len(rs) > 0 and rs[0] == 0:
        # 如果历史表不存在，创建历史表。
        sql_create = \"\"\"create table %(table_space)s.%(bak_table_name)s as
        select * from %(table_space)s.%(table_name)s where 1=0\"\"\" % ( sql_data )
        cur.execute( sql_create )
    # 将原表信息插入到历史表中
    sql_insert = \"\"\"insert into %(table_space)s.%(bak_table_name)s
    select * from %(table_space)s.%(table_name)s where %(sel_que)s\"\"\" % ( sql_data )
    cur.execute( sql_insert )
    # 将原表数据删除
    sql_del = \"\"\"delete from %(table_space)s.%(table_name)s where %(sel_que)s\"\"\" % ( sql_data )
    cur.execute( sql_del )"""
    
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','tab_change(table_name,bak_table_name,sel_que=\"1=1\",table_space=\"TSYW\")','转移数据表信息','将指定数据表数据转移到历史表中。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_name','数据表名称','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'bak_table_name','历史表名称','2','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sel_que','查询条件','2','%s','True','1=1','3')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs4 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_space','数据表所在表空间','2','%s','True','TSYW','4')"""%(uuid.uuid4().hex,hsxxid)
    
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1,ins_crs2,ins_crs3,ins_crs4]
    
def back_table():
    nr ="""import datetime,os,subprocess
from cpos.esb.basic.busimodel.dictlog import tlog
tlog.log_info( '======>备份数据表信息开始' )
# 密码
ORACLE_DBPW = os.environ['ORACLE_DBPW']
# 用户名
ORACLE_DBU = os.environ['ORACLE_RDBU']
dqsj = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
# 定义备份文件生成目录及名称
bakfilename = os.path.join( filesdir, 'data-%s-%s.dmp' % ( dqsj, '%s.%s' % ( table_space, table_name ) ) )
# 组织备份命令
cmd = 'exp %s/%s TABLES=%s COMPRESS=y file=%s' % (ORACLE_DBU, ORACLE_DBPW, '%s.%s' % ( table_space, table_name ), bakfilename)
if sel_que:
    cmd = 'exp %s/%s TABLES=%s COMPRESS=y file=%s query="where %s "' % (ORACLE_DBU, ORACLE_DBPW, '%s.%s' % ( table_space, table_name ), bakfilename, sel_que)
tlog.log_info( '备份命令[%s]' % cmd )
# 执行备份命令并获取执行结果
res = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
res_tmp = res.stdout.readlines()
# 整理校验信息
last_line = ''
if res_tmp:
    last_line = res_tmp[-1]
last_line = last_line.decode('utf8')
if 'unsuccessfully' in last_line or 'with warnings' in last_line:
    # 若执行结果失败,登记失败日志。
    tlog.log_info( '备份数据表失败，异常信息: %s ' % str( res_tmp ) )
else:
    tlog.log_info( '备份数据表成功，备份文件为：%s ' % bakfilename )"""
    
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)
    values('%s','tab_backup(table_name,filesdir, sel_que=\"\",table_space=\"TSYW\")','备份数据表信息','备份数据表信息','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_name','数据表名称','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'filesdir','备份文件目录','2','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sel_que','查询条件','2','%s','True','','3')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs4 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_space','数据表所在表空间','2','%s','True','TSYW','4')"""%(uuid.uuid4().hex,hsxxid)
    
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1,ins_crs2,ins_crs3,ins_crs4]
    
def del_tabdata():
    nr ="""from cpos.esb.basic.busimodel.dictlog import tlog
tlog.log_info( '===>>删除数据表信息开始' )
with connection() as con:
    cur = con.cursor()
    # 组织删除sql
    del_sql ="delete from %s where %s "%( '%s.%s' % ( table_space, table_name ), sel_que )
    tlog.log_info( '执行sql：%s' % del_sql )
    # 执行
    cur.execute( del_sql )
    tlog.log_info( '执行删除sql成功' )"""
    
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)values('%s','del_tabdata(table_name, sel_que="1=1",table_space="TSYW")','删除数据表信息','删除数据表信息。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_name','数据表名称','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sel_que','查询条件','2','%s','True','1=1','2')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs3 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'table_space','数据表所在表空间','2','%s','True','TSYW','3')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1,ins_crs2,ins_crs3]
    
def trans_pause():
    nr = """from ops.zh_manage.manage_common import update_wym
from cpos.esb.basic.busimodel.dictlog import tlog
import datetime
with connection() as con:
    dqsj = datetime.datetime.now().strftime('%Y%m%d')
    jhfqqsj = datetime.datetime.now().strftime('%H%M')
    tlog.log_info( '更新交易状态为禁用' )
    cur = con.cursor()
    # 将指定的监控配置状态改为禁用
    sql = \"\"\"update gl_jydy set zt = '0' where jym = '%s' \"\"\" %(jym)
    cur.execute(sql)
    # 获取交易ID和自动发起配置信息
    sql = \"\"\"select id,zdfqpz from gl_jydy where jym = '%s'\"\"\" %(jym)
    cur.execute(sql)
    rs = cur.fetchall()
    # 调用公共函数update_wym，将类型（jy-交易）和交易ID传入函数，由函数更新唯一码
    tlog.log_info( '更新交易唯一码' )
    update_wym( cur,'jy',rs[0][0])
    # 判断交易是否为自动发起交易，若获取的自动发起配置为空，则直接结束处理
    tlog.log_info( '判断交易是否有配置自动发起' )
    if rs[0][1]:
        tlog.log_info( '交易有配置自动发起交易：需要将对应的计划任务表数据禁用，删除当前时间向后退且未执行的任务' )
        # 查询该任务的计划任务id
        sql_sel = \"\"\"select id from gl_jhrwb where ssid='%s'\"\"\"%(rs[0][0])
        cur.execute(sql_sel)
        rs_jh = cur.fetchall()
        # 更新计划任务表中的状态和配置
        sql_upd = \"\"\"update gl_jhrwb set zt = '0' where id = '%s'\"\"\"%(rs_jh[0][0])
        cur.execute(sql_upd)
        # 通过计划任务id删除当日执行计划表的记录
        sql_del = \"\"\"delete from gl_drzxjhb where ssid = '%s' and rq = '%s' and jhfqsj > '%s' and zt = '0'\"\"\" %(rs_jh[0][0],dqsj,jhfqqsj)
        cur.execute(sql_del)
    tlog.log_info( '禁用交易[%s]处理完成' % jym )"""
    # 交易暂停
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)
    values('%s','trans_pause(jym)','交易暂停','将指定交易暂停。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'jym','交易码','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1]
    
def send_message():
    nr = """# 方法一：注意此注释代码是直接写发短信文件，建议使用下面的方法，想jy_dxxx（短信信息表）中插入数据。
#         写文件这种方式，需要此段代码在通讯主机执行，而下面的第二种方法在任何一台主机都可以

#import datetime,os
#from cpos.esb.basic.busimodel.transutils import get_xtcs
#from ops.trans.utils import get_lsh
#from cpos.esb.basic.busimodel.dictlog import tlog
#dqsj = datetime.datetime.now().strftime('%Y%m%d')
## 获取要发送的手机号
#tlog.log_info( '要发送的手机号：%s' % sjhm )
#phone_no =  [ sjh for sjh in sjhm.split(',') if sjh ]
## 获取短信序号生成短信文件名
#xh = get_lsh( 'dxxh' )            # 短信序号
#tlog.log_info( '短信序号：%s' % str(xh) )
#dxjgdm = get_xtcs('DX_JGDM')
#tlog.log_info( '短信机构代码：%s' % dxjgdm )
#fn = 'SMSRZ%s%s.%04d' % ( dxjgdm, dqsj,xh )
#tlog.log_info( '文件名称：%s' % fn )
#dxpath = get_xtcs('DX_DIRECTORY')
#tlog.log_info( '短信文件保存路径：%s' % dxpath )
#smsf = open( os.path.join( dxpath, fn ) , 'wb' )
#tlog.log_info( '短信文件：%s' % smsf )
#tlog.log_info( '写短信文件开始' )
#tlog.log_info( '短信内容：%s' % dxnr )
#for sjh in phone_no:
#    buf = '%-12s%-200s000%s\\n' % ( sjh, dxnr, dxjgdm )
#    tlog.log_info( 'buf：%s' % buf )
#    smsf.write(buf)
#    smsf.flush()
#smsf.close()
#tlog.log_info( '写短信文件结束' )
#os.system('chmod 777 %s' % ( os.path.join( dxpath, fn ) ) )

# 方法二： 调用公共函数，将发送短信息写入到jy_dxxx中
from ops.trans.utils import send_msg
from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict
from cpos.esb.basic.busimodel.dictlog import tlog
jyzd = AttrDict({})
tlog.log_info( '写短信信息到数据库开始' )
send_msg( dxnr,sjhm,jyzd )
tlog.log_info( '写短信信息到数据库结束' )"""
    # 交易暂停
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)
    values('%s','send_message(sjhm,dxnr)','发送短信','将需要发送的短信内容及接收手机号生成到短信文件。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'sjhm','手机号码列表','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    # 传入参数表中插入数据
    ins_crs2 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'dxnr','短信内容','2','%s','False','','2')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1,ins_crs2]
    
def con_pause():
    nr = """import datetime
dqsj = datetime.datetime.now().strftime('%Y%m%d')
jhfqqsj = datetime.datetime.now().strftime('%H%M')
with connection() as con:
    cur = con.cursor()
    # 将指定的监控配置状态改为禁用
    sql = \"\"\"update gl_jkfxpz set zt = 0 where mc = '%s'\"\"\"%(mon_name)
    cur.execute(sql)
    # 获取该配置ID
    sql = \"\"\"select id from gl_jkfxpz where mc = '%s'\"\"\"%(mon_name)
    cur.execute(sql)
    rs = cur.fetchone()
    # 获取对应计划任务id，更新状态，并将当日计划表中信息删除
    # 查询该任务的计划任务id
    sql = \"\"\"select id from gl_jhrwb where ssid='%s'\"\"\"%(rs[0])
    cur.execute(sql)
    rs_jh = cur.fetchone()
    #更新计划任务表中的状态和配置
    sql = \"\"\"update gl_jhrwb set zt = 0 where id = '%s'\"\"\"%(rs_jh[0])
    cur.execute(sql)
    # 通过计划任务id删除当日执行计划表的记录
    sql = \"\"\"delete from gl_drzxjhb where ssid = '%s' and rq = %s and jhfqsj > '%s' and zt = '0'\"\"\"%(rs_jh[0],dqsj,jhfqqsj)
    cur.execute(sql)"""
    # 停止监控
    hsxxid = uuid.uuid4().hex
    nruuid = uuid.uuid4().hex
    # 函数信息表中插入数据
    ins_hsxx = """insert into gl_hsxxb(id,hsmc,zwmc,ms,nr_id,dmlx,zt,lb,ly,czr,czsj)
    values('%s','con_pause(mon_name)','停止监控','将指定监控配置的状态改为禁用。','%s','1','1','dz','2' ,'','%s')"""%(hsxxid,nruuid,dqsj)

    # blob管理表插入数据
    ins_blob = """insert into gl_blob(id,lx,czr,czsj,nr) values(:nruuid,'gl_hsxxb','',:czsj,:nr)"""

    # 传入参数表中插入数据
    ins_crs1 = """insert into gl_crcs(id,csdm,cssm,sslb,ssid,sfkk,mrz,sxh) values( '%s', 'mon_name','监控配置名称','2','%s','False','','1')"""%(uuid.uuid4().hex,hsxxid)
    return [ins_hsxx,[ins_blob,{'nruuid':nruuid,'nr':pickle.dumps(nr),'czsj':dqsj}],ins_crs1]
        
    
if __name__=='__main__':
    lst = []
    # 执行系统命令 tab_change, back_table del_tabdata trans_pause send_message con_pause
    lst += excute_cmd()
    lst += tab_change()
    lst += back_table()
    lst += del_tabdata()
    lst += trans_pause()
    lst += send_message()
    lst += con_pause()
    with Get_cursor() as cursor:
        print ("预置分析规则导入开始...")
        i = 0
        for sql in lst:
            if isinstance(sql,list):
                cursor.execute(sql[0],sql[1])
            else:
                cursor.execute(sql)
            i+=1
        print ("预置分析规则导入结束...")
