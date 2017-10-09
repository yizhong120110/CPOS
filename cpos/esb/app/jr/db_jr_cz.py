# -*- coding: utf-8 -*-
"""  
    交易自动冲正
    处理和数据库相关的操作
"""
import cpos.esb.basic.resource.rdb
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.transutils import get_xtcs, pickle_loads
import time


def get_czxx( jyrq ,ylsh ):
    """
        通过原流水号获得要处理的冲正节点信息列表
        并更新冲正状态
        查询不到时需要返回空值
        0 ,[{'xh': 1, 'htxx': '', 'cllx': 'ZLC', 'htcluuid': '5d0b104fdd534839aba23d7be367184b'},{'xh': 2, 'htxx': '', 'cllx': 'ZLC', 'htcluuid '5d0b104fdd534839aba23d7be367184b'}]
        print(get_czxx( '20151020', '999906' ))
    """
    # 已冲正次数
    yclcs = 0
    # 回退信息列表，要按照列表的内容来进行回退处理，有顺序要求
    htxxlist = []
    try:
        with connection() as db:
            # 限定仅处理"冲正中"的数据
            sql = """
                select b.cs ,a.xh ,a.htzlcid ,a.htxx ,c.bm ,a.jym
                from jy_htrz a,jy_cz b ,gl_zlcdy c
                where a.jyrq = b.rq 
                    and a.lsh = b.ylsh
                    and b.zt = '1'
                    and a.jyrq = %(jyrq)s
                    and a.lsh = %(ylsh)s
                    and ( b.czwz > a.xh or b.czwz = '0' )
                    and a.htzlcid = c.id
                    and a.xh > 0
                order by a.xh desc
            """
            logger.ods( '待执行sql: %s'%(sql),lv = 'dev',cat = 'app.db_jr_cz')
            # 使用sql和dict分离的方式，是为了防止SQL注入
            d = {'jyrq':jyrq ,'ylsh':ylsh}
            rs = db.execute_sql( sql ,d )
            for obj in rs:
                htrz_t_dic = { 'cllx': 'ZLC' }
                # 已冲正次数，回退日志的序号，回退处理流程的id，回退需要使用的数据
                yclcs = obj['cs']
                htrz_t_dic.update({ 'xh':obj['xh'] ,'jym':obj['jym'] ,'htcluuid':obj['htzlcid'] ,'htclbm':obj['bm'] ,'htxx':pickle_loads(obj['htxx']) })
                htxxlist.append( htrz_t_dic )
    except:
        logger.oes( 'get_czxx处理异常结束',lv = 'error',cat = 'app.db_jr_cz')
    return yclcs ,htxxlist


def upd_jycz( jyrq, ylsh , zt, **kwargs ):
    """
        更新jy_cz的字段值
        print(upd_jycz( '20151020', '999905' , '2' ))
        print(upd_jycz( '20151020', '999905' , '0' ,cs='1' ,czwz='1' ,czlsh='34' ))
    """
    try:
        logger.ods( '更新jycz状态:zt[%s] %s %s'%(str(zt),str(jyrq),str(ylsh)),lv = 'dev',cat = 'app.db_jr_cz')
        subsql = ""
        kwargs['updtime'] = time.strftime('%Y%m%d%H%M%S')
        for key ,value in kwargs.items():
            subsql += " ,%s='%s'"%(key ,value)
        
        with connection() as con:
            sql = " update jy_cz set zt = %(zt)s "+subsql+" where rq = %(jyrq)s and ylsh = %(ylsh)s "
            logger.ods( '更新jycz字段值sql: %s'%(sql),lv = 'dev',cat = 'app.db_jr_cz')
            d = dict( zt=zt, jyrq=jyrq ,ylsh=ylsh)
            con.execute_sql( sql, d )
        return True
    except:
        logger.oes( 'upd_jycz处理异常结束',lv = 'error',cat = 'app.db_jr_cz')
        return False


def upd_jycz_flag(jyrq, ylsh ,flag ,yclcs):
    """
        jyrq 交易日期
        ylsh 原流水号
        flag 成功/失败
        yclcs 已处理次数
    """
    if flag:
        # 前2次失败，更新为待冲正0，3次失败以后为9，成功为2
        upd_jycz( jyrq, ylsh , '2',cs='%s'%(int(yclcs)+1) )
    else:
        upd_jycz( jyrq, ylsh , '0' if 2 > int(yclcs) else '9' ,cs='%s'%(int(yclcs)+1) )


def upd_jyls( jyrq, lsh , zt):
    """
        更新jy_ls的字段值，将更新前的状态返回
        仅处理以下状态的数据
            10:交易失败
            88:交易执行异常
            98:冲正失败
        return 成功/失败（True/False），原状态（用于失败时更新回来）
        print(upd_jyls( '20151012', '82' , '01' ))
    """
    # 更新前的交易状态
    ylshzt = None
    flag = False
    try:
        logger.ods( '更新jyls状态:zt[%s] %s %s'%(str(zt),str(jyrq),str(lsh)),lv = 'dev',cat = 'app.db_jr_cz')
        with connection() as con:
            sql = "select zt from jy_ls where jyrq = %(jyrq)s and lsh = %(lsh)s"
            d = dict(jyrq=jyrq ,lsh=lsh)
            rs = con.execute_sql( sql , d)
            ylshzt = rs[0] if len(rs) else None
            # 不能处理找不到记录的数据，且不能处理交易成功、被冲正的数据
            # 冲正中的不能再次冲正
            if ylshzt and (ylshzt['zt'] in ("10","88","98") or (ylshzt['zt']=='90' and zt!='90')):
                ylshzt = ylshzt['zt']
                sql = " update jy_ls set zt = %(zt)s where jyrq = %(jyrq)s and lsh = %(lsh)s "
                logger.ods( '更新jyls字段值sql: %s'%(sql),lv = 'dev',cat = 'app.db_jr_cz')
                d = dict( zt=zt, jyrq=jyrq ,lsh=lsh)
                con.execute_sql( sql, d )
                flag = True
    except:
        logger.oes( 'upd_jyls处理异常结束',lv = 'error',cat = 'app.db_jr_cz')
    return flag ,ylshzt


def upd_jyls_flag(jyrq, ylsh ,flag ,yclcs ,ylshzt):
    """
        jyrq 交易日期
        ylsh 原流水号
        flag 成功/失败
        yclcs 已处理次数
        ylshzt 原流水状态
    """
    if flag:
        # 前2次失败，更新为原状态，3次失败以后为冲正失败，成功为99
        upd_jyls( jyrq, ylsh , '99' )
    else:
        upd_jyls( jyrq, ylsh , ylshzt if 2 > int(yclcs) else '98' )



if __name__ == '__main__':
#    print(upd_jycz( '20151020', '999905' , '2' ))
    print(get_czxx( '20151020', '999906' ))
