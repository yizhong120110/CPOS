# -*- coding: utf-8 -*-
# Action: 业务基本信息
# Author: gaorj
# AddTime: 2014-12-26
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj.esb import memcache_data_del
from sjzhtspj import render_to_string, ModSql, logger, get_sess_hydm
from sjzhtspj.common import get_uuid, get_strftime, update_wym, ins_czrz, zz_nr
from ..kf_ywgl_017.kf_ywgl_017_service import del_memcache_data


def index_service(params):
    """
    # 业务基本信息
    """
    data = {}
    
    with sjapi.connection() as db:
        # 查询业务基本信息
        ywobj = ModSql.kf_ywgl_002.execute_sql_dict(db, "get_ywjbxx", params)
        data['yw_dic'] = ywobj[0] if ywobj else {}
        # 查询地区定义 lx(1:地区)
        zones = ModSql.kf_ywgl_002.execute_sql_dict(db, "get_dqdy")
        data['zones'] = zones
    return data

def jbxx_edit_service(params):
    """
    # 业务基本信息编辑
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 校验业务简称是否存在
        sql_data = {'id': params['id'], 'ywbm': params['ywbm']}
        obj = ModSql.kf_ywgl_002.execute_sql(db, "check_ywbm", sql_data)
        if obj:
            result['msg'] = '业务简称[%s]已经存在，请重新输入' % params['ywbm']
            return result
        
        # 查询修改前的信息
        data = ModSql.kf_ywgl_002.execute_sql(db, "select_jbxx", sql_data)[0]
        # 更新业务基本信息
        sql_data = {'id': params['id'], 'ywbm': params['ywbm'], 'ywmc': params['ywmc'], 'ywms': params['ywms']}
        ModSql.kf_ywgl_002.execute_sql(db, "update_yw", sql_data)
        # 登记操作日志
        nr_bjq = '编辑前：业务编码[%s]，业务名称[%s]，业务描述[%s]' % (data['ywbm'], data['ywmc'], data['ywms'])
        nr_bjh = '编辑后：业务编码[%s]，业务名称[%s]，业务描述[%s]' % (params['ywbm'], params['ywmc'], params['ywms'])
        ins_czrz( db, '业务编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '业务管理_编辑' )

        # 清除memcache
        del_memcache_data( db, ywbm = params['ywbm'] )
        
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result

def data_service(params):
    """
    # 业务参数json数据
    """
    data = {}
    
    with sjapi.connection() as db:
        # 查询总条数
        sql_data = {'ywid': params['ywid']}
        total = ModSql.kf_ywgl_002.execute_sql(db, "count_cs", sql_data)[0].count
        # 查询业务参数
        sql_data = {'ywid': params['ywid'], 'rn_start': params['rn_start'], 'rn_end': params['rn_end']}
        ywcs = ModSql.kf_ywgl_002.execute_sql_dict(db, "get_ywcs", sql_data)
        
        data['total'] = total
        data['rows'] = ywcs
    
    return data

def data_add_service(params):
    """
    # 业务参数新增
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 校验业务参数是否存在
        sql_data = {'ywid':params['ywid'], 'csdm':params['csdm']}
        obj = ModSql.kf_ywgl_002.execute_sql(db, "check_ywcs", sql_data)
        if obj:
            result['msg'] = '参数代码[%s]已经存在，请重新输入' % params['csdm']
            return result
        
        # 插入参数定义表 lx(1:地区)
        id = get_uuid()
        sql_data = {'id':id, 'csdm':params['csdm'], 'csms':params['csms'], 'value':params['csz'], 'lx':'2', 'ssid':params['ywid'], 'zt':params['cszt'], 'czr':get_sess_hydm(), 'czsj':get_strftime()}
        ModSql.kf_ywgl_002.execute_sql(db, "insert_csdy", sql_data)
        
        # 更新唯一码
        update_wym(db, 'cs', id)
        # 清除memcache
        del_memcache_data( db, ywid = params['ywid'] )
        
        # 记录行员日常运维流水
        # 获取登记内容
        nr = zz_nr( db, sql_data, '业务参数管理-新增参数' )
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = params['pt'], gnmc = '业务参数管理_新增' )
        
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def data_del_service(params):
    """
    # 业务参数删除
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        sql_data = {'ids': params['ids'].split(',')}
        # 查询业务参数代码、名称
        rs_csmc = ModSql.kf_ywgl_002.execute_sql_dict(db, "get_ywcs_dm_ms", sql_data)
        # 删除业务参数
        ModSql.kf_ywgl_002.execute_sql(db, "del_ywcs", sql_data)
        # 清除memcache
        del_memcache_data( db, ywid = params['ywid'] )
        # 登记操作日志
        nr = '业务参数[%s]已被删除' % ','.join([k['csdm']+':'+(k['csms'] or '') for k in rs_csmc])
        ins_czrz( db, nr, pt = params['pt'], gnmc = '业务参数管理_删除' )
        
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result

def data_edit_service(params):
    """
    # 业务参数修改
    """
    result = {}
    
    with sjapi.connection() as db:
        # 更新参数定义表
        sql_data = {'csid':params['csid'], 'csms':params['csms'], 'value':params['csz'], 'zt':params['cszt'], 'czr':get_sess_hydm(), 'czsj':get_strftime()}
        # 获取登记内容
        nr = zz_nr( db, sql_data, '业务参数管理-编辑参数', upd_id = params['csid'] )
        # 保存修改内容
        ModSql.kf_ywgl_002.execute_sql_dict(db, "update_csdy_yw", sql_data)
        
        # 更新唯一码
        update_wym(db, 'cs', params['csid'])
        # 清除memcache
        del_memcache_data( db, ywid = params['ywid'] )
        # 记录行员日常运维流水
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = params['pt'], gnmc = '业务参数管理_编辑' )
        
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result
