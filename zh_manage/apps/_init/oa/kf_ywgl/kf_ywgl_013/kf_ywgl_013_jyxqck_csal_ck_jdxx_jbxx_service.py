# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 输入输出查看 service
# Author: 周林基
# AddTime: 2015-2-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import json
from sjzhtspj import ModSql
from sjzhtspj.common import srscys_hex_to_binary


def index_service( data_dic ):
    """
    # 自动化测试：子流程测试案例 输入输出查看
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
        # 处理报文信息
        srscys_hex_to_binary(srys)
        srscys_hex_to_binary(scys)
        # 转化为json数据
        srys = json.dumps(srys)
        scys = json.dumps(scys)
        return {'srys': srys, 'scys': scys, 'demoid':data_dic['demoid']}