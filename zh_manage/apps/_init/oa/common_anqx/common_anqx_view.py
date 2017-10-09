# -*- coding: utf-8 -*-
# Action: 按钮权限加载
# Author: houpp
# AddTime: 2015-08-31
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj.common import anqx_service
from sjzhtspj import request, render_to_string, logger

@register_url('POST')
def index_view():
    """
    # 获取按钮权限列表
    """
    # 菜单代码-前台传入
    cddm = request.POST.menuDm
    # 初始化反馈前台信息
    data = { 'an_lst': []}
    try:
        # 组织请求信息字典
        sql_data = { 'cddm': cddm }
        # 调用数据库操作函数
        data = anqx_service( sql_data )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return data
