# -*- coding: utf-8 -*-
# Action: 运维当日执行计划
# Author: fangch
# AddTime: 2015-04-14
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, datetime
from sjzhtspj import ModSql, logger
from sjzhtspj.common import get_bmwh_bm, get_strftime, get_strftime2, check_fhr, get_uuid, ins_czrz, format_log, get_hyxx, change_log_msg
from sjzhtspj.esb import readlog
from sjzhtspj.esb import get_lsh2con
from sjzhtspj.const import FHR_JSDM


def data_ymxx_service():
    """
    # 初始化当日执行计划页面数据准备 service
    """
    # 初始化反馈值
    data = { 'zt_lst': [], 'rwlx_lst': [], 'rq': '' }
    # 查询状态列表
    zt_lst = get_bmwh_bm( '10003' )
    # 查询规则列表
    rwlx_lst = get_bmwh_bm( '10002' )
    # 排除任务类型为响应动作的
    rwlx_lst = [ obj for obj in rwlx_lst if obj.get('value') != 'dz']
    # 追加请选择选项
    zt_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    rwlx_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    # 获取当前日期 YYYY-MM-DD
    rq = get_strftime()[:10]
    # 将结果放到返回值中
    data['zt_lst'] = zt_lst
    data['rwlx_lst'] = rwlx_lst
    data['rq'] = rq
    # 将结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 当日执行计划列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    search_lst = [ 'rq', 'mc', 'rwlx', 'zt', 'lsh' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询当日执行计划总条数
        total = ModSql.yw_jhrw_003.execute_sql(db, "data_count", sql_data)[0].count
        # 查询当日执行计划列表
        jbxx = ModSql.yw_jhrw_003.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data

def data_dzzxjhlb_service( sql_data ):
    """
    # 响应动作列表json数据 service
    """
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询响应动作列表总条数
        total = ModSql.yw_jhrw_003.execute_sql(db, "data_dzzxjhlb_count", sql_data)[0].count
        # 查询响应动作列表
        jbxx = ModSql.yw_jhrw_003.execute_sql_dict(db, "data_dzzxjhlb_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data

def data_sgzxjhlb_service(sql_data):
    """
    # 手工执行计划列表json数据 service
    """
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询手工执行计划列表总条数
        total = ModSql.yw_jhrw_003.execute_sql(db, "data_sgzxlb_count", sql_data)[0].count
        # 查询手工执行计划列表
        jbxx = ModSql.yw_jhrw_003.execute_sql_dict(db, "data_sgzxlb_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data

def check_service(data_dic):
    """
    # 授权校验 提交 service
    """
    # 返回值
    result = {'state': False, 'msg':''}
    with sjapi.connection() as db:
        # 首先校验复核人是否正确
        hyxx_dic = { 'hydm': data_dic['fhr'], 'mm': data_dic['fhrmm'], 'jsdm': FHR_JSDM,
                     'sq_gnmc': data_dic.get('sq_gnmc','test'), 'czpt': data_dic.get('czpt'), 'sqgndm': data_dic.get('sqgndm'), 
                     'szcz': data_dic.get('sq_gnmc','test') + '复核人授权' }
        ret,msg = check_fhr( db, hyxx_dic )
        if ret == False:
            result['msg'] = msg
            return result
    # 反馈信息
    result['state'] = True
    result['msg'] = '授权成功'
    return result
    
def sgzxcl_service(data_dic):
    """
    # 手工执行处理
    """
    result = {'msg':'','state': False}
    with sjapi.connection() as db:
        # 查询指定计划的状态
        jbxx = ModSql.yw_jhrw_003.execute_sql_dict(db, "get_jhxx", data_dic)
        jbxx[0]['id'] = get_uuid()
        # 流水号为 日期yyyymmddhhmmss+六位递增数 需与核心登记一致
        xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000, con = db )
        jbxx[0]['lsh'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
        jbxx[0]['rq'] = get_strftime2()[:8]
        jbxx[0]['jhfqsj'] = get_strftime2()[8:]
        # 若状态为0-未发起，则更新状态为3-手工发起
        #if jbxx[0].get('yzt') == '0':
        ModSql.yw_jhrw_003.execute_sql_dict(db, "upd_jhzt", data_dic)
        # 向当日执行计划表中插入一条新的记录，作为新的执行流水
        # 当插入的记录任务类型为分析时
        if jbxx[0]['yrwlx'] == 'fx':
            ip_lst = ModSql.yw_jhrw_003.execute_sql_dict(db, "select_jhip", data_dic)
            if ip_lst:
                jbxx[0]['yip'] = ip_lst[0]['ip']
        if jbxx[0]['yrwlx'] == 'jy':
            plzdb_dic = { 'id': get_uuid(), 'drzxjhbid': jbxx[0]['id'], 'ydrzxjhbid': data_dic['drzxjhid'] }
            ModSql.yw_jhrw_003.execute_sql_dict(db, "ins_plzdb", plzdb_dic)
        # 插入计划任务
        ModSql.yw_jhrw_003.execute_sql_dict(db, "ins_jhrw", jbxx[0])
        # 记录行员日常运维流水
        # 获取登记内容 
        # 获取复核人信息
        hyxx_dic = get_hyxx( db, hydm = data_dic.get('fhr') )
        fhrxm = hyxx_dic.get( data_dic.get('fhr'), '' )
        nr = '当日执行计划列表-执行：流水号[%s],任务类型[%s],crontab配置[%s],原流水号[%s],由授权人[%s:%s]授权手工执行' % (jbxx[0]['lsh'],jbxx[0]['yrwlx'],jbxx[0]['yzdfqpz'],jbxx[0]['ylsh'],data_dic.get('fhr'),fhrxm)
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = 'wh', gnmc = '当日执行计划列表-执行' )
        result['msg'] = "任务登记成功"
        result['state'] = True
        #else:
        #    result['msg'] = "任务状态发生变化，请重新执行"
        return result

def demo_log_service(data):
    """
    # 获取日志信息
    """
    rq = data[0]     # 日期
    lsh = data[1]    # 日志流水号
    ret_log_lst = readlog( rq, lsh )
    logger.info('查询反馈的日志列表：%s' % str(ret_log_lst))
    log_all = change_log_msg( ret_log_lst )
    log = format_log(log_all)
    
    return {'state': True, 'msg': '', 'log': log}
