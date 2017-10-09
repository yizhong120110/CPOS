# -*- coding: utf-8 -*-
# Action: 运维监控配置列表
# Author: fangch
# AddTime: 2015-04-11
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_bmwh_bm

def data_ymxx_service():
    """
    # 初始化监控配置列表页面数据准备 service
    """
    # 初始化反馈值
    data = { 'zt_lst': [], 'gzlb_lst': [] }
    # 查询状态列表
    zt_lst = get_bmwh_bm( '10001' )
    # 查询规则列表
    gzlb_lst = get_bmwh_bm( '10002' )
    # 只取编码为分析和采集的规则类别
    gzlb_lst = [ obj for obj in gzlb_lst if obj.get('value') in ('fx','cj')]
    # 追加请选择选项
    zt_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    gzlb_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    # 将结果放到返回值中
    data['zt_lst'] = zt_lst
    data['gzlb_lst'] = gzlb_lst
    # 将结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 监控配置列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    search_lst = [ 'gzlb', 'pzmc', 'fxgzzb', 'zt' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询监控配置总条数
        total = ModSql.yw_jhrw_002.execute_sql(db, "data_count", sql_data)[0].count
        # 查询监控配置列表
        jbxx = ModSql.yw_jhrw_002.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data

def data_xydzlb_service( sql_data ):
    """
    # 响应动作列表json数据 service
    """
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询响应动作列表总条数
        total = ModSql.yw_jhrw_002.execute_sql(db, "data_xydzlb_count", sql_data)[0].count
        # 查询响应动作列表
        jbxx = ModSql.yw_jhrw_002.execute_sql_dict(db, "data_xydzlb_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data