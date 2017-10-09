# -*- coding: utf-8 -*-
# Action: 交易基本信息
# Author: gaorj
# AddTime: 2014-12-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj.esb import memcache_data_del
from sjzhtspj import ModSql, get_sess_hydm
from sjzhtspj.common import get_uuid, get_strftime, get_strftime2, update_wym, ins_czrz, crontab_fy, update_jhrw, zz_nr


def index_service(params):
    """
    # 交易基本信息
    """
    jy_dic = {'id':params['id'], 'jym':'', 'jymc':'', 'jyms':'', 'zt':'', 'timeout':'', 'zdfqpz':''}
    data = {'jy_dic': jy_dic, 'zones':[]}
    
    with sjapi.connection() as db:
        # 查询交易基本信息
        jyobj = ModSql.common.execute_sql_dict(db, "get_jydy", params)
        jy_dic = jyobj[0] if jyobj else jy_dic
        # 查询地区定义
        zones = ModSql.common.execute_sql_dict(db, "get_zones")
        data['jy_dic'] = jy_dic
        data['zones'] = zones
    return data

def data_service(params):
    """
    # 交易参数json数据
    """
    data = {'total':0, 'rows':[]}
    
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.common.execute_sql_dict(db, "get_csdy_count", {'ssid':params['ssid']})[0]['count']
        # 查询业务参数
        ywcs = ModSql.common.execute_sql_dict(db, "get_csdy", params)
        data['total'] = total
        data['rows'] = ywcs
    
    return data

def data_add_service(params):
    """
    # 交易参数新增
    """
    # ID
    id= get_uuid()
    
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 校验业务参数是否存在
        sql_data = {'ssid':params['ssid'], 'csdm':params['csdm']}
        count = ModSql.common.execute_sql_dict(db, "check_csdm", sql_data)[0]['count']
        if count > 0:
            result['msg'] = '参数代码[%s]已经存在，请重新输入' % params['csdm']
            return result
        
        # 插入参数定义表
        params.update({'id': id, 'lx':'3', 'czr': get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.common.execute_sql_dict(db, "insert_csdy", params)
        
        # 更新唯一码
        update_wym(db, 'cs', id)
        # 记录行员日常运维流水
        # 获取登记内容
        nr = zz_nr( db, params, '交易参数管理-新增参数' )
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = params['pt'], gnmc = '交易参数管理_新增' )
        # 清除memcache
        memcache_data_del([params['jym']])
        
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def data_del_service(params):
    """
    # 交易参数删除
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        sql_data = {'id_lst': params['ids'].split(',')}
        # 查询业务参数代码、名称
        rs_csmc = ModSql.common.execute_sql_dict(db, "get_csdm", sql_data)
        # 删除业务参数
        ModSql.common.execute_sql_dict(db, "delete_csdy", sql_data)
        
        # 登记操作日志
        nr = '交易参数[%s]已被删除' % ','.join([k['csdm']+':'+(k['csms'] or '') for k in rs_csmc])
        ins_czrz( db, nr, pt = params['pt'], gnmc = '交易参数管理_删除' )
        
        # 清除memcache
        memcache_data_del([params['jym']])
        
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result

def data_edit_service(params):
    """
    # 交易参数编辑
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 更新参数定义表
        params.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        # 获取登记内容
        nr = zz_nr( db, params, '交易参数管理-编辑参数', upd_id = params['id'] )
        ModSql.common.execute_sql_dict(db, "update_csdy", params)
        
        # 更新唯一码
        update_wym(db, 'cs', params['id'])
        # 记录行员日常运维流水
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = params['pt'], gnmc = '交易参数管理_编辑' )
        # 清除memcache
        memcache_data_del([params['jym']])
        
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result

def jbxx_edit_service(params):
    """
    # 交易基本信息编辑
    """
    result = {'state':False, 'msg':'', 'zdfqpzsm': ''}
    
    with sjapi.connection() as db:
        # 校验交易码是否存在
        sql_data = {'id': params['id'], 'jym': params['jym']}
        obj = ModSql.kf_ywgl_003.execute_sql_dict(db, "check_jym", sql_data)
        if obj:
            result['msg'] = '交易码[%s]已经存在，请重新输入' % params['jym']
            return result
        # 自动发起配置如果不为空，则进行翻译
        if params['zdfqpz']:
            # 返回信息：(True/False, 中文翻译, message)
            ret = crontab_fy(params['zdfqpz'])
            # 翻译错误，将错误信息反馈前台
            if ret[0] == False:
                result['msg'] = ret[2]
                return result
            else:
                # 翻译成功，将中文翻译放在保存字典中
                params['zdfqpzsm'] = ret[1]
        # 查询修改前的信息
        data = ModSql.kf_ywgl_003.execute_sql(db, "select_jbxx", sql_data)[0]
        # 更新交易基本信息
        params.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.kf_ywgl_003.execute_sql_dict(db, "update_jydy", params)
        # 处理交易的计划任务信息
        # upd_dic = { 'zdfqpz': zdfqpz,'zdfqpzsm': zdfqpzsm,'rwlx': rwlx,'ssid':ssid,'zt':zt }
        upd_dic = { 'zdfqpz': params['zdfqpz'],'zdfqpzsm': params['zdfqpzsm'], 'rwlx': 'jy','ssid': params['id'],'zt': params['zt'] }
        # 调用公共函数
        update_jhrw( db, data['zt'], data['zdfqpz'], upd_dic = upd_dic )
        # 登记操作日志
        nr_bjq = '编辑前：交易名称[%s]，交易码[%s]，交易状态[%s]，交易超时时间[%s]，交易自动发起配置[%s]，自动发起配置说明[%s]，交易描述[%s]' % (data['jymc'], data['jym'], data['zt'], data['timeout'], data['zdfqpz'], data['zdfqpzsm'], data['jyms'])
        nr_bjh = '编辑后：交易名称[%s]，交易码[%s]，交易状态[%s]，交易超时时间[%s]，交易自动发起配置[%s]，自动发起配置说明[%s]，交易描述[%s]' % (params['jymc'], params['jym'], params['zt'], params['timeout'], params['zdfqpz'], params['zdfqpzsm'], params['jyms'])
        ins_czrz( db, '交易编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '交易管理_编辑' )
        # 更新唯一码
        update_wym(db, 'jy', params['id'])
        # 清除memcache
        memcache_data_del([params['jym']])
        # 组织反馈信息
        result['state'] = True
        result['msg'] = '修改成功'
        result['zdfqpzsm'] = params['zdfqpzsm']
    
    return result

def zdfqpzfy_service(params):
    """
    # 翻译
    """
    # 返回信息：(True/False, 中文翻译, message)
    ret = crontab_fy(params['zdfqpz'])
    # 组织反馈信息
    result = { 'state': ret[0], 'msg': ret[2], 'zdfqpzsm': ret[1] }
    # 将结果反馈给view
    return result