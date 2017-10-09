# -*- coding: utf-8 -*-
# Action: 运维参数管理-系统参数
# Author: zhangchl
# AddTime: 2015-04-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import render_to_string


@register_url('GET')
def index_view():
    """
    # 运维参数管理 主页面
    """
    return render_to_string("yw_csgl/yw_csgl_001/yw_csgl_001.html")
