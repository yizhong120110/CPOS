# -*- coding: utf-8 -*-
# Action: 运维参数管理-业务参数
# Author: zhangchl
# AddTime: 2015-04-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql


def data_service( sql_data ):
    """
    # 业务参数管理列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    
    # 数据库链接
    with sjapi.connection() as db:
        # 查询业务总条数
        total = ModSql.yw_csgl_002.execute_sql(db, "data_count", sql_data)[0].count
        # 查询业务列表
        jbxx = ModSql.yw_csgl_002.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的几个反馈给view
    return data
