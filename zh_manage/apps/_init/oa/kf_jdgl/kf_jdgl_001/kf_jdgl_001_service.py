# -*- coding: utf-8 -*-
# Action: 节点管理
# Author: qish
# AddTime: 2015-01-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.const import JDLX_MC_DIC


def data_service(params):
    """
    # 节点管理json数据
    """
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # rn_start和rn_end
        rn_data = {
            'rn_start': params['rn_start'], 
            'rn_end': params['rn_end']
        }
        # 搜索字段名和搜索值
        search_data = {}
        search_name = params['search_name']
        search_value = params['search_value']
        if search_name and search_value:
            search_data['search_name'] = [search_name]
            MC_JDLX_DIC = {v:k for k,v in JDLX_MC_DIC.items()}
            if search_name == 'jdlx':
                search_data['search_value'] = MC_JDLX_DIC.get(search_value, search_value)
            else:
                search_data['search_value'] = search_value
        # 查询节点信息
        jdxx_lst = ModSql.kf_jdgl_001.execute_sql_dict(db, "get_jddy", dict(rn_data, **search_data))
        # 查询打解包节点被引用次数
        djb_yycs = ModSql.kf_jdgl_001.execute_sql_dict(db, "get_djb_yycs")
        djb_yycs_dic = {row['jdid']:row['yycs'] for row in djb_yycs}
        # 获取是否是最新版本数据
        for jdxx in jdxx_lst:
            jdxx['bbsftj'] = ('1' if jdxx['jdwym'] == jdxx['bbkzwym'] else '0')
            jdxx['jdlxdm'] = jdxx['jdlx']
            jdxx['jdlx'] = JDLX_MC_DIC.get(jdxx['jdlx'], jdxx['jdlx'])
            jdxx['yycs'] += djb_yycs_dic.get(jdxx['jdid'], 0)
        # 查询总条数
        total = ModSql.kf_jdgl_001.execute_sql_dict(db, "count_jddy", search_data)[0]['count']
        
        data['total'] = total
        data['rows'] = jdxx_lst
    
    return data

def yycs_data_service(params):
    """
    # 引用次数信息查询
    """
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询交易引用节点次数及子流程引用节点次数
        rows = ModSql.kf_jdgl_001.execute_sql_dict(db, "get_jdyycs", params)
        
        data['total'] = len(rows)
        data['rows'] = rows
    
    return data
