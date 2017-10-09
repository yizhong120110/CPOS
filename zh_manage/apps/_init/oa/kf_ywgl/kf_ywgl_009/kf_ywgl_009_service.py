# -*- coding: utf-8 -*-
# Action: 流程-自动化测试编码
# Author: liuhh
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import json
from sjzhtspj import ModSql

def get_csaldylb_service(ssid, sslb, lb, rn_start, rn_end):
    """
    # 获取流程-测试案例定义列表的信息
    """
    with sjapi.connection() as db:
        # 根据测试案例定义表的所属ID查询测试案例的个数
        total = ModSql.kf_ywgl_009.execute_sql(db, "get_count_csaldy", {"ssid":ssid, "sslb":sslb, "lb":lb})[0].count
        # 根据测试案例定义表所属ID查询测试案例的信息列表
        csaldylb = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csaldylb", {"ssid":ssid, "sslb":sslb, "lb":lb, "rn_start":rn_start, "rn_end":rn_end})
        return {'total':total,'rows':csaldylb}

def csal_jbxx_service(map):
    """
    # 获取流程-测试案例定义基本的信息
    """
    with sjapi.connection() as db:
        # 根据测试案例定义表ID查询测试案例
         csal = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_jbxx", map)[0]
         return csal

def csal_jdxx_service(map):
    """
    # 获取流程-测试案例定义节点的信息
    """
    sortlst = []
    with sjapi.connection() as db:
        #根据测试案例的ID获取节点测试案例执行步骤列表
        jdcsalzxbz = ModSql.kf_ywgl_009.execute_sql(db, "get_csal_jdxx_jdcsalzxbzlb_id", map)[0]
        jdcsalzxbzids = jdcsalzxbz['jdcsalzxbzlb'].split(",")
        # 根据测试案例定义表ID查询出的测试案例执行步骤,进行获取节点信息
        jdxxlb = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_jdxx_jdcsalzxbzlb_data", {"jdcsalzxbz":jdcsalzxbzids})
        # 按照执行步骤进行排序
        if jdxxlb:
            for i in jdcsalzxbzids:
                jdxxlb_lst = [row for row in jdxxlb if row["id"] == i]
                if jdxxlb_lst:
                    sortlst.append( jdxxlb_lst[0] )
    
    return {'rows':sortlst}

def csal_jdxx_jbxx_service(map):
    """
    # 获取流程-测试案例定义节点输入输出要素
    """
    with sjapi.connection() as db:
        # 根据节点测试案例执行步骤ID查询出输入输出要素的信息
        yslb = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        # 输入要素
        srys = [row for row in yslb if row['lx'] == '1']
        # 输出要素
        scys = [row for row in yslb if row['lx'] != '1']
        srys = json.dumps(srys)
        scys = json.dumps(scys)
        return {'srys':srys, 'scys':scys, 'demoid':""}

def csal_demo_service(map):
    """
    # 获取流程-测试案例定义demo信息
    """
    with sjapi.connection() as db:
        # 测试案例定义demo的具体信息
        rs = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_demo", map);
        # 不能存在demo数据的时候直接进行返回
        if not rs :
            return  {'demo':{},'demojbxxsjb':[]}
        demo = rs[0]
        # 查询demo基本信息的ID查询demo的数据表
        demojbxxsjb = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_demojbxx_sjb", {"demojbxxid":demo["id"]})
        return {'demo':demo, 'demojbxxsjb':demojbxxsjb}

def csal_demo_datagrid_service(sjkmxdyid, sjbid):
    """
    # 获取流程-测试案例定义demo信息表字段及表名称
    """
    with sjapi.connection() as db:
         # 查询demo基本信息的ID查询demo的字段表名称
        demojbxxzbzdmc = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_demojbxx_bzdmc", {"sjkmxdyid":sjkmxdyid})
        # 查询demo基本信息的ID查询demo的字段表值
        demojbxxzbzd = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_demojbxx_bzd", {"sjbid":sjbid})
        #看是否有表字段值,如果没有直接返回
        if not demojbxxzbzdmc:
            return  {"columns":[], "rows":[]}
        # 组织列名
        columns = [{"field":row["zdmc"], "title":row["zdmc"], "width":100} for row in demojbxxzbzdmc]
        # 遍历动态组织前台渲染表格表头和内容
        data = {"columns":[], "rows":[]}
        list_dic = {}
        for row in demojbxxzbzd:
            list_dic.setdefault(row['xssx'], {})[row['zdm']] = row['zdz']
        data["rows"] = list(list_dic.values())
        data["columns"].append(columns)
        # 返回
        return data;