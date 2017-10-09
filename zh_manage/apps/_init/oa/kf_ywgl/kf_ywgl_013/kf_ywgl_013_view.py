# -*- coding: utf-8 -*-
# Action: 自动化测试 view
# Author: 周林基
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import logger, request,render_to_string, render_string
from .kf_ywgl_013_service import data_service


@register_url('GET')
def index_view():
    """
    # 自动化测试：主页面
    """
    data = { 'ywid': request.GET.ywid}
    return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013.html", data)

@register_url('GET')
def data_view():
    """
    # 自动化测试：选择需测试的交易或节点树形结构和datagrid列表的展示
    """
    # 业务ID
    ssywid = request.GET.ywid

    try:
        # 组织调用函数字典
        data_dic = { 'ssywid': ssywid}
        data = []
        # 调用操作数据库函数
        data = data_service( data_dic )

    except:
        logger.info(traceback.format_exc())

    return json.dumps(data)
