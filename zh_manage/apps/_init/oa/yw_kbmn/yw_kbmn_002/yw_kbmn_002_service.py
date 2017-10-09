# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: luoss
# AddTime: 2015-06-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql

def data_wzxx_service( sql_data ):
    """
    # 知识库分类列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询知识库总条数
        total = ModSql.yw_kbmn_002.execute_sql(db, "select_wzts", sql_data)[0].count
        # 查询知识库列表
        jbxx = ModSql.yw_kbmn_002.execute_sql_dict(db, "select_wzxx", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data