# -*- coding: utf-8 -*-
# Action: 角色权限管理
# Author: houpp
# AddTime: 2015-06-02
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .gl_jsqx_001_service import data_service, jslst_service,gnlb_service,\
    cdlst_service, add_cdqx_service, add_gnqx_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    # 页面跳转执行
    return render_to_string("gl_jsqx/gl_jsqx_001/gl_jsqx_001.html")

@register_url('POST')
def jslst_view():
    """
    # 角色列表数据
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    # 获取前台页面部门id
    try:
        # 调用操作数据库函数
        data = jslst_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return  data

@register_url('POST')
def data_view():
    """
    # 菜单列表
    """
    # 初始化反馈信息
    data = {'total': 0, 'rows': []}
    #获取前台页面角色id
    jsid = request.POST.jsid
    sql_data = {'jsid': jsid}
    try:
        # 调用操作数据库函数
        data = data_service(sql_data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def gnlb_view():
    """
    # 获取功能菜单列表
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 前台获取菜单id
    cdid = request.POST.cdid
     # 获取用户id
    jsid = request.POST.jsid
    sql_data = {'cdid':cdid,'jsid':jsid}

    try:
        # 调用操作数据库的函数
        data = gnlb_service(sql_data)

    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return  data

@register_url('POST')
def cdlst_view():
    """
    # 菜单树列表数据
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    # 获取前台选择的菜单权限
    cdids = request.POST.cdid
    jsid = request.POST.jsid
    sql_data = {'cdids':cdids,'jsid':jsid}
    try:
        # 调用操作数据库函数
        data = cdlst_service(sql_data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return  data

@register_url('POST')
def add_cdqx_view():
    """
    # 增加菜单权限
    :return:
    """
    data = {'state':False, 'msg':""}
    # 获取前台传递的数据
    # 获取菜单ID
    ids = request.POST.ids
    # 角色ID
    jsid = request.POST.jsid
    sql_data = {'ids':ids, 'jsid':jsid}
    try:
        # 调用操作数据库函数
        data = add_cdqx_service(sql_data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '增加角色菜单权限！异常错误提示信息\n[%s]' % error_msg
    
    return  data

@register_url('POST')
def add_cdgn_view():
    """
    # 增加按钮权限
    :return:
    """
    # 获取前台传递的数据
    # 获取菜单ID
    cdid = request.POST.cdid
    # 获取按钮列表
    ids =  request.POST.ids
    # 角色ID
    jsid = request.POST.jsid

    sql_data = {'ids':ids, 'jsid':jsid, 'cdid':cdid}

    try:
        # 调用操作数据库函数
        data = add_gnqx_service(sql_data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return  data










