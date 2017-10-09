# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 查看 service
# Author: 周林基
# AddTime: 2015-2-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
# Explain: 由于本功能特殊，所以允许将sql下载此py中

from sjzhtspj import ModSql

def csal_demo_service(map):
    """
    # 获取流程-测试案例定义demo信息
    """
    with sjapi.connection() as db:
        # 测试案例定义demo的具体信息
        rs = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_demo", map);
        # 不能存在demo数据的时候直接进行返回
        if not rs :
            return  {'demo':{},'demojbxxsjb':[]}
        demo = rs[0]
        # 查询demo基本信息的ID查询demo的数据表
        demojbxxsjb = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_demojbxx_sjb", {"demojbxxid":demo["id"]})
        return {'demo':demo, 'demojbxxsjb':demojbxxsjb}

def csal_demo_datagrid_service(sjkmxdyid, sjbid):
    """
    # 获取流程-测试案例定义demo信息表字段及表名称
    """
    with sjapi.connection() as db:
         # 查询demo基本信息的ID查询demo的字段表名称
        demojbxxzbzdmc = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_demojbxx_bzdmc", {"sjkmxdyid":sjkmxdyid})
        # 查询demo基本信息的ID查询demo的字段表值
        demojbxxzbzd = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_demojbxx_bzd", {"sjbid":sjbid})
        #看是否有表字段值,如果没有直接返回
        if not demojbxxzbzdmc:
            return  {"columns":[], "rows":[]}
        # 组织列名
        columns = [{"field":row["zdmc"], "title":row["zdmc"], "width":50} for row in demojbxxzbzdmc]
        # 遍历动态组织前台渲染表格表头和内容
        data = {"columns":[], "rows":[]}
        list_dic = {}
        for row in demojbxxzbzd:
            list_dic.setdefault(row['xssx'], {})[row['zdm']] = row['zdz']
        data["rows"] = list(list_dic.values())
        data["columns"].append(columns)
        # 返回
        return data;