# -*- coding: utf-8 -*-
from cpos.esb.basic.busimodel.transutils import get_xtcs, pickle_loads
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.functools import get_uuid
import json
import datetime


def get_xx(drrwid):
    """
    根据当日执行任务id获取任务执行信息
    这是管理端提供的接口函数
    输入：任务id
    输出：任务类型，结果字典：
            rwlx = jy(交易):
                'jy',{ 'buf': "报文", 'timeout': 超时时间 }
            rwlx = cj（采集）:
                'cj',{ 'classname': 类名称, 'funcname': 函数名称, 'classparam': 类参数字典, 'funcparam': 函数参数字典 }
            rwlx = fx（分析）：
                'fx',{ 'funcuuid': 函数uuid, 'funcparam': 函数参数字典, 'hxdz_dic': {'True':[动作1，动作2，……], 'False': []} ( 后续动作 ) }
            rwlx = dz( 动作 )：
                'dz',{ 'funcuuid': 函数uuid, 'funcparam': 函数参数字典 }
    """
    try:
        # 虚拟柜员，使用系统参数值
        XNGY = get_xtcs('XNGY')
        # 虚拟机构，使用系统参数值
        XNJGDM = get_xtcs('XNJGDM')
        # 通讯节点ID，用于交易处理，默认值
        COMMID = get_call_jy_commid()
        # 当前日期，时间
        now = datetime.datetime.now()
        rq = now.strftime('%Y%m%d')
        sj = now.strftime('%H%M')
        with connection() as con:
            # 获取任务类型信息
            sql = "select rwlx, ssid from gl_jhrwb where id = (select ssid from gl_drzxjhb where id = %(drrwid)s)  " 
            d = dict(drrwid=drrwid)
            rs = con.execute_sql(sql, d)
            row = rs[0] if len(rs) else None
            # 动作类型的任务，没有对应计划任务信息
            # 计划任务批量转单笔也没有对应计划任务信息
            if row == None:
                sql = "select rwlx, ssid from gl_drzxjhb where id = %(drrwid)s"
                d = dict(drrwid=drrwid)
                rs = con.execute_sql(sql, d)
                row = rs[0] if len(rs) else None
            # 任务类型为交易
            if row['rwlx'] == 'jy':
                sql_jy = "select jym,timeout from gl_jydy where id = %(ssid)s"
                d = dict(ssid=row['ssid'])
                rs = con.execute_sql(sql_jy, d)
                row_jy = rs[0] if len(rs) else None
                dic = {'CZGY':XNGY,'JYJGM':XNJGDM}
                buf = row_jy['jym'] + ' '*(16 - len(row_jy['jym'])) + json.dumps( dic )
                buf = '%04d'%(len(buf)+4) + buf
                buf = buf.encode("utf8")
                
                # 尝试获取交易的报文和通讯节点id，如果没有，则使用上面的默认值
                sql_jybuf = "select txglbm ,buf from gl_plzdb where drzxjhbid = %(drrwid)s"
                d = dict(drrwid=drrwid)
                rs_buf = con.execute_sql(sql_jybuf, d)
                if len(rs_buf):
                    # txglbm 不一定有值
                    COMMID = rs_buf[0]["txglbm"] or COMMID
                    buf = pickle_loads(rs_buf[0]["buf"])
                return 'jy',{'buf':buf,'timeout':row_jy['timeout'] ,'commid':COMMID}
            # 数据采集
            elif row['rwlx'] == 'cj':
                # 计划任务表中ssid保存的是：对象采集配置表.id
                # 反馈：类名，方法名，类参数，方法参数
                # 根据计划任务表id.所属id 获取对象采集配置信息( 类名，方法名 )
                sql_hsmc = """  select  c.sslbbm, c.zbbm, a.id as dxcjpzid, a.zdzjip as zjip  from gl_dxcjpz a, gl_cjpzb b, gl_jkzb c
                                where a.id = %(ssid)s
                                and a.sscjpzid = b.id
                                and b.zbid = c.id"""
                d = dict(ssid=row['ssid'])
                rs = con.execute_sql(sql_hsmc, d)
                rs_hsmc = rs[0] if len(rs) else None
                # 类名
                classname = rs_hsmc['sslbbm']
                # 方法名
                funcname = rs_hsmc['zbbm']
                # 类参数
                classparam = { 'zjip': rs_hsmc['zjip'], 'dxcjpzid': rs_hsmc['dxcjpzid'] }
                # 获取方法参数
                funcparam = {}
                sql_fs_cs = """ select d.csdm, a.csz, d.mrz from gl_csdyb a, gl_dxcjpz b, gl_cjpzb c, gl_crcs d
                                where a.ssid = b.id
                                and b.sscjpzid = c.id
                                and c.zbid = d.ssid
                                and d.id = a.crcsid
                                and b.id = %(ssid)s"""
                d = dict( ssid=row['ssid'] )
                rs_fs_cs = con.execute_sql(sql_fs_cs, d)
                for obj in rs_fs_cs:
                    funcparam[obj['csdm']] = obj['csz'] if obj['csz'] else ( obj['mrz'] if obj['mrz'] else '' ) 
                return 'cj', { 'classname': classname, 'funcname': funcname, 'classparam': classparam, 'funcparam': funcparam }
            # 分析
            elif row['rwlx'] == 'fx':
                # 计划任务表中ssid保存的是：监控分析配置表id
                # 反馈：函数uuid，函数参数，后续动作字典
                # 根据计划任务表id.所属id 获取函数id
                sql_hsid = """  select gzid from gl_jkfxpz where id = %(ssid)s"""
                d = dict( ssid=row['ssid'] )
                rs = con.execute_sql(sql_hsid, d)
                rs_hsid = rs[0] if len(rs) else None
                # 函数uuid
                funcuuid = rs_hsid['gzid']
                # 函数参数
                funcparam = {}
                sql_hscs = """  select a.csdm, b.csz, a.mrz from gl_crcs a, gl_csdyb b
                                where a.ssid = %(funcuuid)s
                                and b.crcsid = a.id 
                                and b.ssid = %(ssid)s"""
                d = dict( funcuuid=funcuuid, ssid=row['ssid'] )
                rs_fs_cs = con.execute_sql(sql_hscs, d)
                
                for obj in rs_fs_cs:
                    funcparam[obj['csdm']] = obj['csz'] if obj['csz'] else ( obj['mrz'] if obj['mrz'] else '' ) 
                # 后续动作列表
                # 查询流水号
                sql_drzxjhrwxx = "select lsh from gl_drzxjhb where id = %(drrwid)s"
                d = dict(drrwid=drrwid)
                rs = con.execute_sql(sql_drzxjhrwxx, d)
                row_rwxx = rs[0] if len(rs) else None
                lsh = row_rwxx['lsh']
                sql_hxdz = """  select a.fxjgcf, a.id as ssid, b.zjip as ip, a.fqfs as dzlx, a.jhsj as jhfqsj from gl_xydzpz a, gl_dzzxzj b
                                where b.ssid = a.id
                                and a.ssjkfxid = %(rwls)s"""
                d = dict( rwls=row['ssid'] )
                rs_hxdz = con.execute_sql( sql_hxdz, d )
                hxdz_dic = { 'True': [], 'False': [] }
                for obj in rs_hxdz:
                    # 所属id为：响应动作配置id
                    # 发起方式：计划发起:1：自动发起：当前时间，2：手工发起：无，3：计划时间
                    jhfqsj = sj if obj['dzlx'] == '1' else ( obj['jhfqsj'].replace(":","") if obj['dzlx'] == '3' else '' )
                    hxdz_dic[obj['fxjgcf']].append( { 'rwlx': 'dz', 'ssid': obj['ssid'], 'ip': obj['ip'], 
                                                'dzlx': obj['dzlx'], 'rq': rq, 'jhfqsj': jhfqsj,
                                                'zt': '0', 'bcflsh': lsh, 'sfkbf': '0'  } )
                return 'fx', { 'funcuuid': funcuuid, 'funcparam': funcparam, 'hxdz_dic': hxdz_dic }
            # 动作
            elif row['rwlx'] == 'dz':
                # 计划任务表中ssid保存的是：监控分析-响应动作配置id
                # 反馈：函数uuid，函数参数
                # 根据计划任务表id.所属id 获取响应动作配置id
                sql_hsid = """select a.dzid, b.dmlx from gl_xydzpz a, gl_hsxxb b 
                            where a.id = %(id)s and a.dzid = b.id"""
                d = dict(id=row['ssid'])
                rs = con.execute_sql(sql_hsid, d)
                rs_hsid = rs[0] if len(rs) else None
                # 函数uuid
                funcuuid = rs_hsid['dzid']
                # 代码类型
                dmlx = rs_hsid['dmlx']
                # 函数参数
                funcparam = {}
                sql_hscs = """  select a.csdm, b.csz, a.mrz from gl_crcs a, gl_csdyb b
                                where a.ssid = %(funcuuid)s
                                and b.crcsid = a.id 
                                and b.ssid = %(ssid)s"""
                d = dict( funcuuid=funcuuid, ssid=row['ssid'] )
                rs_fs_cs = con.execute_sql(sql_hscs, d)
                for obj in rs_fs_cs:
                    funcparam[obj['csdm']] = obj['csz'] if obj['csz'] else ( obj['mrz'] if obj['mrz'] else '' ) 
                return 'dz', { 'funcuuid': funcuuid, 'funcparam': funcparam, 'lx': 'HS_SHELL' if dmlx == '2' else 'HS' }
    except:
        logger.oes( 'get_xx处理异常结束',lv = 'error',cat = 'app.jr_db')
    return None ,None


# 公共函数
def upd_rwxx( rwid, zt, **kwargs ):
    try:
        #  更新当日计划任务表中的状态
        logger.ods( '更新任务表状态:zt[%s] %s'%(str(zt),str(kwargs)),lv = 'dev',cat = 'app.db_jr')
        subsql = ""
        kwargs['sjfqsj'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for key ,value in kwargs.items():
            # gl_drzxjhb 中的字段都是str类型
            subsql += " ,%s='%s'"%(key ,value)
        
        with connection() as con:
            sql = " update gl_drzxjhb set zt = %(zt)s "+subsql+" where id = %(rwid)s "
            logger.ods( '更新任务执行状态sql: %s'%(sql),lv = 'dev',cat = 'app.db_jr')
            d = dict(zt=zt,rwid=rwid)
            rs = con.execute_sql( sql, d )
        return True
    except:
        logger.oes( 'upd_rwxx处理异常结束',lv = 'error',cat = 'app.db_jr')
        return False


def insert_drzxjhrw(  rw_lst ):
    """
        # 根据后续动作写当日执行计划任务信息
    """
    with connection() as con:
        for rwxx_dic in rw_lst:
            id = rwxx_dic.get('id', '') if rwxx_dic.get('id', '') else get_uuid()
            xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000, con = con )
            lsh = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
            sql_inst = """insert into gl_drzxjhb (id,lsh,rwlx,ssid,ip,
            dzlx,rq,jhfqsj,zt,bcflsh,sfkbf)
            values( %(id)s,%(lsh)s,%(rwlx)s,%(ssid)s,%(ip)s,%(dzlx)s,
            %(rq)s,%(jhfqsj)s,%(zt)s,%(bcflsh)s,%(sfkbf)s )
            """
            d = dict( id=id, lsh=lsh, rwlx=rwxx_dic.get('rwlx',''),
            ssid=rwxx_dic.get('ssid',''),ip=rwxx_dic.get('ip',''),
            dzlx=rwxx_dic.get('dzlx',''),rq=rwxx_dic.get('rq',''),jhfqsj=rwxx_dic.get('jhfqsj',''),
            zt=rwxx_dic.get('zt',''),bcflsh=rwxx_dic.get('bcflsh',''),sfkbf=rwxx_dic.get('sfkbf','') )
            rs = con.execute_sql( sql_inst, d )


def get_lsh2con( cs , min = 1 , max = 100000, con = None ):
    if con:
        sql = "select dm , lsh from zd_lsh where dm = %(cs)s for update"
        d = dict(cs=cs)
        rs = con.execute_sql( sql , d )
        row = rs[0] if len(rs) else None
        if row is None:
            sql = "insert into zd_lsh( dm , lsh ) values ( %(cs)s , %(min)s ) "
            d = dict( cs=cs , min=min )
            rs = con.execute_sql( sql , d )
            return min
        else:
            lsh = row['lsh'] + 1
            if lsh < min:
                lsh = min
            if lsh > max:
                lsh = min
            sql =  'update zd_lsh set lsh = %(lsh)s where dm = %(cs)s'
            d = dict( lsh=lsh , cs=cs )
            rs = con.execute_sql( sql , d )
            return lsh
    else:
        with connection() as con:
            sql = "select dm , lsh from zd_lsh where dm = %(cs)s for update"
            d = dict(cs=cs)
            rs = con.execute_sql( sql , d )
            row = rs[0] if len(rs) else None
            if row is None:
                sql = "insert into zd_lsh( dm , lsh ) values ( %(cs)s , %(min)s ) "
                d =  dict( cs=cs , min=min )
                rs = con.execute_sql( sql , d )
                return min
            else:
                lsh = row['lsh'] + 1
                if lsh < min:
                    lsh = min
                if lsh > max:
                    lsh = min
                sql =  'update zd_lsh set lsh = %(lsh)s where dm = %(cs)s'
                d = dict( lsh=lsh , cs=cs )
                rs = con.execute_sql( sql , d )
                return lsh


# 自动发起交易的通讯节点代码
def get_call_jy_commid():
    return get_xtcs("CALL_JY_COMMID")


def test_get_xx():
#    cj: ba74fae6915a41118d4e5b2255e47071
#    fx: 1a997f9b27af406ba56537a24abcfa06
#    dz: 4ca83764bd8440b081ed4444ff8a7c2e
#    dz shell带参数：c86f8519c4d548b5a3a452f6b4227585
#    dz shell不带参数：7409228d2a2f4968ba000908b5b9b56a
    rwlx,csxx = get_xx('c86f8519c4d548b5a3a452f6b4227585')
    print ('获取到的任务类型为：',rwlx)
    print ('获取到的参数有：',csxx)
    rwlx,csxx = get_xx('7409228d2a2f4968ba000908b5b9b56a')
    print ('获取到的任务类型为：',rwlx)
    print ('获取到的参数有：',csxx)


if __name__ == '__main__':
    test_get_xx()
