# -*- coding: utf-8 -*-
# Action: 行员日常运维流水展示
# Author: kongdq
# AddTime: 2015-04-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql


def index_service():
    """
    # 初始化查询service
    """
    # 初始化返回值
    data = {'czpt_lst':[]}
    
    # 数据库链接
    with sjapi.connection() as db:
        # 查询业务列表
        tmp = ModSql.yw_hycz_001.execute_sql_dict(db, "data_bm")
        # 追加请选择选项
        tmp.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
        # 将查询详情结果放到结果集中
        data['czpt_lst'] = tmp
    
    # 将查询到的结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 条件查询service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询业务总条数
        total = ModSql.yw_hycz_001.execute_sql(db, "data_count",sql_data)[0].total
        # 查询业务列表
        tmp = ModSql.yw_hycz_001.execute_sql_dict(db, "data_cx",sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = tmp
    
    # 将查询到的结果反馈给view
    return data
