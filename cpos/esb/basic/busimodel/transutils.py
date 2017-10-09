# -*- coding: utf-8 -*-
from cpos.esb.basic.busimodel.fmtdatetime import e_now
from cpos.esb.basic.config import settings
import cpos.esb.basic.resource.rdb
import time, pickle


def get_xtlsh():
    """ 获取系统流水号 """
    with connection() as con:
        if settings.DB_TYPE == "oracle":
            sql_lsh = " select jy_ls_lsh_seq.nextval as nextval from dual"
            rs = con.execute_sql(sql_lsh)
        else:
            sql_lsh = "select nextval('jy_ls_lsh_seq') as nextval"
            rs = con.execute_sql(sql_lsh)
    return rs[0].get("nextval") if len(rs) else None


def _set_xtcs(csdm , csz ,con):
    """
        # 为了get_xtcs和set_xtcs共用同一个赋值语句
    """
    sql_sel = "select value from gl_csdy where csdm = %(csdm)s and lx = '1'"
    d = dict(csdm=csdm)
    rs = con.execute_sql(sql_sel, d)
    if len(rs) == 0:
        d = dict(id=csdm, csdm=csdm, csz=csz)
        # 状态（1：启用），类型（1：系统参数） 来源：2（铺底）
        sql = "insert into gl_csdy ( id ,csdm ,value ,csms ,lx ,zt ,ly ,ssid ,czr ,czsj ,wym)\
         values( %(id)s, %(csdm)s, %(csz)s ,'当前交易时间','1','1','2','','','','' )"
        con.execute_sql( sql, d )
    else:
        sql = "update gl_csdy set value = %(csz)s where csdm = %(csdm)s and lx = '1'"
        d = dict(csz=csz , csdm=csdm)
        con.execute_sql( sql, d )

def get_xtcs( csdm , default = '' ):
    """
    获取系统参数。
    参数：
        csdm    参数代码
        default 默认值
    以字符串形式返回
    """
    with connection() as con:
        sql = "select value from gl_csdy where csdm = %(csdm)s and lx='1'"
        d = dict(csdm=csdm)
        rs = con.execute_sql( sql, d )
        row = rs[0] if len(rs) else None
        if not row:
            csz = default
            _set_xtcs(csdm , csz ,con)
        else:
            csz = row['value']
        return csz


def set_xtcs( csdm , csz ):
    """
    设置系统参数
    参数：
        csdm    参数代码
        csz     参数值（字符串形式）
    """
    with connection() as con:
        _set_xtcs(csdm , csz ,con)


def ins_lsz( lsh, jyrq, jysj, jym, jgdm=None, gyh=None ):
    """
    登记交易流水jy_ls
    参数|建议取值：
        lsh   交易流水号           jyzd.SYS_XTLSH
        jyrq  交易日期             jyzd.SYS_JYRQ
        jysj  交易时间
        jym   交易码
        jgdm  发起机构代码
        gyh   操作柜员
    """
    with connection() as con:
        sql = """insert into jy_ls ( lsh , jyrq , jysj , jyfqsj , jym , jgdm , gyh , zt )
                               values ( %(lsh)s , %(jyrq)s , %(jysj)s , %(jyfqsj)s , %(jym)s , %(jgdm)s , %(gyh)s , %(zt)s )"""
        d = dict( lsh=lsh , jyrq=jyrq , jysj=jysj , jyfqsj=e_now() , jym=jym , jgdm=jgdm , gyh=gyh , zt='00' )
        con.execute_sql( sql, d )
        sql = """insert into JY_LS_KZ ( jylsh , jyrq , jysj )
                               values ( %(lsh)s , %(jyrq)s , %(jysj)s )"""
        con.execute_sql( sql, d )


def upd_lsz( rq, lsh, **d ):
    """
    更新交易流水的字段
    参数：
        rq  交易日期取值jyzd.SYS_JYRQ
        lsh 交易流水号jyzd.SYS_XTLSH
        d  要更新的字段字典，型如：{ field:value, }
    """
    try:
        with connection() as con:
            lsh = d.pop( 'lsh', lsh ) # 流水号不可被更新，故从d中弹出
            di = dict(jyrq=rq, lsh=int(lsh) )
            set_clause = []
            for k,v in d.items():
                set_clause.append( "%s =%%(%s)s" % ( k , k ) )
                di[k] = v
            sql = "update jy_ls set "+ ','.join( set_clause )+" where jyrq = %(jyrq)s and lsh = %(lsh)s"
            con.execute_sql( sql, di )
    except:
        print( '更新流水[%s]失败'%lsh )
        #log_exception( '更新流水[%s]失败' , lsh )
        raise


def ins_jycz( lsh, jyrq, cs=0, czwz=0, zt='0' ):
    """
    登记交易流水jy_ls
    参数|建议取值：
        rq       原流水交易日期     jyzd.SYS_JYRQ
        ylsh     原流水号           jyzd.SYS_XTLSH
        cs       冲正次数：初始为0
        czwz     冲正位置：记录已经成功冲正了几个节点，初始为0
        zt       当前冲正状态:
                    0 待冲正
                    1 冲正中
                    2 冲正成功
                    9 错误不再冲正
        updtime  更新时间（当前时间）
    """
    with connection() as con:
        sql = """ insert into JY_CZ( rq, ylsh, cs, czwz, zt, updtime )
                               values ( %(jyrq)s , %(lsh)s , %(cs)s , %(czwz)s , %(zt)s , %(updtime)s )"""
        d = dict( jyrq=jyrq , lsh=lsh , cs=cs , czwz=czwz , zt=zt , updtime=e_now() )
        con.execute_sql( sql , d )


def is_trans_timeout(sys_cssj ,sys_ctime):
    """
    判断交易是否超时
    防止sys_cssj的值为None，设置默认值为60
    """
    timeout_interval = int(sys_cssj if sys_cssj is not None else 60)
    latency_time = timeout_interval - (time.time() - float(sys_ctime or time.time()))
    if 0 > latency_time:
        return True
    return False


def get_txser_timeout(txjdid):
    """
    获得通讯节点对应的超时时间，用于交易码解出之前的超时
    """
    with connection() as con:
        sql = "select cssj from gl_txgl where bm = %(txjdid)s"
        d = dict(txjdid=txjdid)
        rs = con.execute_sql( sql, d )
        row = rs[0] if len(rs) else None
        if row:
            csz = row['cssj']
        else:
            csz = None
        return csz


def pickle_loads(context):
    if settings.DB_TYPE == "postgresql":
        return pickle.loads(context)
    else:
        return pickle.loads(context.read())


def cnt_hyrz(jyrq, lsh):
    """
        统计jy_htrz表中的记录条数
    """
    with connection() as con:
        sql = "select count(1) as cnt from JY_HTRZ where jyrq = %(jyrq)s and lsh = %(lsh)s"
        d = dict(jyrq=jyrq ,lsh=lsh)
        rs = con.execute_sql( sql , d)
        return int(rs[0]['cnt'])



if __name__=="__main__":
    print('----------',get_xtcs('xtrq'))
    set_xtcs('xtrq','20150320')
    print('----------',get_xtcs('xtrq'))
    #get_xtcs('xtrq')
    #ins_lsz( 38, '', '2015-03-20 15:10:25.467869', 'lt001' )
    #upd_lsz('jyrq',3,**{'xym':'0'})
