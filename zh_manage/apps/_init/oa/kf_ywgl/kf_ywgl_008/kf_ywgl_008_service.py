# -*- coding: utf-8 -*-
# Action: 子流程基本信息service
# Author: zhangzf
# AddTime: 2015-1-6
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import update_wym,get_strftime,ins_czrz

def index_service(map):
    """
    # 获取子流程信息
    """
    # 子流程信息
    with sjapi.connection() as db:
        return ModSql.kf_ywgl_008.execute_sql_dict(db, "get_zlc", map)[0]
    
def update_service(map):
    """
    # 修改子流程信息
    """  
    
    # 更新子流程
    with sjapi.connection() as db:
        # 查询修改前的信息
        data = ModSql.kf_ywgl_008.execute_sql_dict(db, "get_zlc", map)[0]
        map['czr'] = get_sess_hydm()
        map['czsj'] = get_strftime()
        ModSql.kf_ywgl_008.execute_sql(db, "update_zlc", map)
        # 更新唯一码
        update_wym(db, 'zlc', map['id'])
        # 登记操作日志
        nr_bjq = '编辑前：子流程编码[%s]，子流程名称[%s]，子流程类别[%s]，子流程描述[%s]' % (data['bm'], data['mc'], data['lb'], data['ms'])
        nr_bjh = '编辑后：子流程编码[%s]，子流程名称[%s]，子流程类别[%s]，子流程描述[%s]' % (data['bm'], map['mc'], data['lb'], map['ms'])
        ins_czrz( db, '子流程编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '子流程管理_编辑' )
    
    return {'state':True, 'msg':'编辑成功'}
    
