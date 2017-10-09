# -*- coding: utf-8 -*-

from sjzhtspj import ModSql

def data_service(sql_data):
    """
    # 查询终端信息.
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询终端信息的条数
        count = ModSql.tcr_0003.execute_sql(db, 'get_zdjk_cnt', sql_data)[0].cnt
        # 查询终端信息
        zdxx = ModSql.tcr_0003.execute_sql_dict(db, 'get_zdjk', sql_data)
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = zdxx
    return data
