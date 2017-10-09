# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 查看 service
# Author: 周林基
# AddTime: 2015-2-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import json
from sjzhtspj import ModSql 

def index_service( data_dic ):
    """
    # 自动化测试：子流程测试案例 查看
    # @param data_dic:字典参数
    """
    with sjapi.connection() as db:
        #根据测试案例的ID获取节点测试案例执行步骤列表
        param_dic = {'csaldyid': data_dic['csaldyid']}
        jdcsalzxbz_obj = ModSql.kf_ywgl_013.execute_sql(db, "index_zdcs_csal_jy_jdcsalzxbzlb", param_dic)
        if jdcsalzxbz_obj and data_dic['lx'] != "jd":
            jdcsalzxbzids = jdcsalzxbz_obj[0]['jdcsalzxbzlb'].split(",")
            # 根据测试案例定义表ID查询出的测试案例执行步骤,进行获取节点信息
            csaldy_lst = ModSql.kf_ywgl_013.execute_sql_dict(db, "index_zdcs_csal_jy_jdcsalzxbzlb_detail", {"id": jdcsalzxbzids})
            # 根据测试案例执行步骤排序
            row_lst = []
            if csaldy_lst:
                for i in jdcsalzxbzids:
                    jdxxlb_lst = [row for row in csaldy_lst if row["id"] == i]
                    if jdxxlb_lst:
                        row_lst.append( jdxxlb_lst[0] )
            # 若果是类型是交易，修改开始和结束为交易开始[解包名字]，交易结束[打包名字]
            if data_dic['lx'] == 'jy' and row_lst:
                row_lst[0]['jdmc'] = '交易开始[%s]' % row_lst[0]['jdmc']
                row_lst[len(row_lst)-1]['jdmc'] = '交易结束[%s]' % row_lst[len(row_lst)-1]['jdmc']
            return {'rows': row_lst, 'lx': data_dic['lx'], 'jdcsalzxbzid': ""}
        elif jdcsalzxbz_obj and data_dic['lx'] == "jd":
            jdcsalzxbzids = jdcsalzxbz_obj[0]['jdcsalzxbzlb'].split(",")
            return {'rows': [], 'lx': data_dic['lx'], 'jdcsalzxbzid': jdcsalzxbzids[0]}
        else:
            return {'rows': [], 'lx': data_dic['lx'], 'jdcsalzxbzid': ""}

def jd_index_service( data_dic ):
    """
    # 自动化测试：子流程测试案例 输入输出查看 节点
    # @param data_dic:字典参数
    """
    with sjapi.connection() as db:
        # 根据节点测试案例执行步骤ID查询出输入输出要素的信息
        ys_dic = ModSql.kf_ywgl_013.execute_sql_dict(db, "index_zdcs_csal_csalys", data_dic)
        # 输入要素
        srys = []
        # 输出要素
        scys = []
        #遍历进行分组
        for row in ys_dic:
            if row['lx'] == '1':
                srys.append(row)
            else:
                scys.append(row)
        srys = json.dumps(srys)
        scys = json.dumps(scys)
        return {'srys': srys, 'scys': scys}