# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: luoss
# AddTime: 2015-06-11
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql

def index_service():
    """
    # 知识库主页列表json数据 service
    """
    # 初始化返回值
    data = {'zskfl_lst':[], 'qsxx_lst':[], 'tjxx_lst':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询系统名称及知识条数
        jbxx = ModSql.yw_kbmn_001.execute_sql_dict(db, "select_zskfl")
        # 查询排行前三的数据
        qsxx = ModSql.yw_kbmn_001.execute_sql_dict(db, "select_tjph")
        # 统计文章信息
        tjwz = ModSql.yw_kbmn_001.execute_sql(db, "select_tjwz")[0].wz
        # 统计评论信息
        tjpl = ModSql.yw_kbmn_001.execute_sql(db, "select_tjpl")[0].pl
        # 统计浏览信息
        tjll = ModSql.yw_kbmn_001.execute_sql(db, "select_tjll")[0].ll
        # 前三位的信息列表
        i = 0
        for k in qsxx[:3]:
            i += 1
            data['qsxx_lst'].append({'sx':i, 'xm':k['xm'], 'dm':k['cjhydm']})
        # 当信息不足三位时，进行添加默认信息
        if i <= 3:
            for k in range(3-i):
                data['qsxx_lst'].append({'sx':i+k+1, 'xm':'暂无', 'dm':'暂无'})
        # 将查询结果放到反馈值中
        data['zskfl_lst'] = jbxx
        data['tjxx_lst'].append(tjwz)
        data['tjxx_lst'].append(tjpl)
        data['tjxx_lst'].append(tjll)
    # 将查询到的结果反馈给view
    return data
    
def data_wzxx_service( sql_data ):
    """
    # 知识库分类列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_kbmn_001.execute_sql(db, "select_wzts", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_kbmn_001.execute_sql_dict(db, "select_wzxx", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data