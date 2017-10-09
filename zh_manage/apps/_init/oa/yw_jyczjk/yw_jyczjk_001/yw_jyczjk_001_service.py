# -*- coding: utf-8 -*-
# Action: 冲正监控
# Author: zhangchl
# AddTime: 2015-10-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import pickle
from sjzhtspj import ModSql, logger
from sjzhtspj.common import ( get_strfdate, get_bmwh_bm, change_log_msg, format_log, get_strftime2 )
from sjzhtspj.esb import readlog, send_jr


def index_service( sql_data ):
    """
    # 初始化交易监控页面数据准备 service
    """
    # 初始化反馈值
    data = { 'zt_lst': [] }
    # 查询流水状态列表
    zt_lst = get_bmwh_bm( '10029' )
    # 追加请选择选项
    zt_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    # 将结果放到返回值中
    data['zt_lst'] = zt_lst
    # 当前日期
    data['nowdate'] = get_strfdate()
    # 将结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'jyrq', 'lsh', 'czlsh', 'czlshzt', 'jymc', 'jym' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jyczjk_001.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jyczjk_001.execute_sql_dict(db, "data_rs", sql_data)
        # 查询冲正流水状态列表
        zt_lst = get_bmwh_bm( '10029', db = db )
        # 冲正流水状态字典
        zt_dict = dict( [(xx['value'], xx['text']) for xx in zt_lst ] )
        # 查询交易流水状态列表
        jyzt_lst = get_bmwh_bm( '10010', db = db )
        # 交易流水状态字典
        jyzt_dict = dict( [(xx['value'], xx['text']) for xx in jyzt_lst ] )
        # 对结果集中状态进行翻译
        for obj in jbxx:
            obj['ztmc'] = zt_dict.get( str( obj['zt'] ), obj['zt'] )
            obj['ylsztmc'] = jyzt_dict.get( obj['ylszt'], obj['ylszt'] )
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data

def select_log_service( sql_data ):
    """
    # 查询流程日志
    """
    # 初始化返回值
    result = { 'state':True, 'msg': '', 'rznr':'' }
    # 调用公共函数获取本流程交易日期
    log_lst_dic = readlog( sql_data['jyrq'], sql_data['lsh'] )
    log_all = change_log_msg( log_lst_dic )
    # 整理日志
    result['rznr'] = format_log( log_all )
    # 将日志信息返回给view
    return result
    
def czjyrz_ck_service( sql_data ):
    """
    # 冲正交易执行子流程步骤列表
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jyczjk_001.execute_sql(db, "czhtrz_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jyczjk_001.execute_sql_dict(db, "czhtrz_rs", sql_data)
        for htrz in jbxx:
            if htrz['htxx'] == None:
                htrz['htxx'] = ''
            else:
                htrz['htxx'] = pickle.loads(htrz['htxx'].read())
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data

def sgcz_service( sql_data ):
    """
    # 手工冲正
    """
    # 初始化返回值
    result = {'state': False, 'msg':'发起失败'}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询：YWZJ_IP 业务主机hostname
        rs_zxzjip = ModSql.common.execute_sql_dict(db, "get_xx_csdy")
        if not rs_zxzjip:
            result['msg'] = '参数代码[YWZJ_IP:业务主机IP]未在参数定义表中存在'
            return result
        hostname = rs_zxzjip[0]['value']
        # 原流水号
        logger.info( "冲正操作，原流水号:[%s]"  % str( sql_data['ylsh'] ) )
        # 判断原交易流水状态是否为：10交易失败 98冲正失败 88异常
        rs_count = ModSql.yw_jyczjk_001.execute_sql(db, "check_jy", sql_data)[0].count
        if rs_count > 0:
            # 对应原交易流水状态非正常
            logger.info( "原交易流水[%s]状态为：10交易失败 或 98冲正失败 或 88异常"  % sql_data['ylsh'] )
            # 冲正流水号
            content = { "ylsh": sql_data['ylsh'],"czlsh": sql_data['czlsh'] }
            source = 'cz'
            # 更新流水状态为冲正中
            sql_data['updtime'] = get_strftime2()
            ModSql.yw_jyczjk_001.execute_sql(db, "update_jycz", sql_data)
            # 调用函数发起冲正
            logger.info( "===================>>>>>>>>>调用send_jr传入信息content：%s " % str( content ) )
            result_msg = send_jr( content, hostname, source )
            if result_msg == 'ok':
                result['state'] = True
                result['msg'] = '发起成功'
            else:
                result['msg'] = '发起失败，核心反馈：%s' % result_msg
            logger.info( "===================>>>>>>>>>调用send_jr返回值：%s " % str( result_msg ) )
        else:
            msg = "原交易流水[%s]状态非：10交易失败 或 98冲正失败 或 88异常 或未找到对应的原交易" % sql_data['ylsh']
            logger.info( msg )
            result['msg'] = msg
            
    return result

