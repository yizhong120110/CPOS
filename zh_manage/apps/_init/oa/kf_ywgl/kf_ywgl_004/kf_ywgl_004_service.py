# -*- coding: utf-8 -*-
# Action: 交易/子流程查看
# Author: gaorj
# AddTime: 2015-01-04
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql


@register_url('GET')
def index_service(params):
    """
    # 交易流程查看
    """
    data = {'lx':params['lx'], 'id': params['id'], 'mc': ''}
    
    with sjapi.connection() as db:
        sql_data = {'id': params['id']}
        if params['lx'] == 'lc':
            # 查询交易名称
            rs = ModSql.common.execute_sql_dict(db, "get_jydy", sql_data)
            data['mc'] = rs[0]['jymc'] if rs else ''
        elif params['lx'] == 'zlc':
            # 查询子流程名称
            rs = ModSql.common.execute_sql_dict(db, "get_zlcdy", sql_data)
            data['mc'] = rs[0]['mc'] if rs else ''
    
    return data
