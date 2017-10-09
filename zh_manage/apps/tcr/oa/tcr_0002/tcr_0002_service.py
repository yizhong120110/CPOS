# -*- coding: utf-8 -*-

from sjzhtspj import ModSql
#from sjzhtspj.common import ins_czrz,get_strftime,ip_is_called,del_waitexec_task,ins_waitexec_task,get_uuid,update_wym_yw

def data_service(sql_data):
    """
    # 查询终端信息.
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询终端信息的条数
        count = ModSql.tcr_0002.execute_sql(db, 'get_zdxx_cnt', sql_data)[0].cnt
        # 查询终端信息
        zdxx = ModSql.tcr_0002.execute_sql_dict(db, 'get_zdxx', sql_data)
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = zdxx
    return data

def force_exit_service(sql_data):
    """
    # 强制签退.
    """
    # 数据结构
    data = {'state':True, 'msg':'强制签退成功'}

    with sjapi.connection() as db:
        ModSql.tcr_0002.execute_sql(db, 'force_exit', sql_data)
    return data
