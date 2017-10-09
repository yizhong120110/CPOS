# -*- coding: utf-8 -*-

from sjzhtspj import ModSql

def data_service(sql_data):
    """
    # 查询库存信息.
    """
    # 数据结构
    data = {}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询库存信息
        kcxx = ModSql.tcr_0004.execute_sql_dict(db, 'get_kcxx', sql_data)
        # 将查询结果放到结果集中
        data['rows'] = kcxx
    return data
