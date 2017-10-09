# -*- coding: utf-8 -*-
# Action: 菜单管理
# Author: luoss
# AddTime: 2015-06-09
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .gl_mmgl_001_service import update_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    try:
        # 页面跳转执行
        return render_to_string("gl_mmgl/gl_mmgl_001/gl_mmgl_001.html")
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())

@register_url('POST')
def update_view():
    """
    # 密码修改
    """
    # 初始化返回值
    result ={'state':False,'msg':''}
    try:
        # 获取原密码
        newpass = request.POST.password
        # 获取新密码
        oldpass = request.POST.oldPassword
        # 组织请求字典
        sql_data = {'newpass':newpass,'oldpass':oldpass}
        # 调用service
        result = update_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '修改失败！异常错误提示信息[%s]' % error_msg
    # 将结果返回给前台
    return result
