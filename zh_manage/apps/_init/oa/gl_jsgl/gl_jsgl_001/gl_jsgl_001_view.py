# -*- coding: utf-8 -*-
# Action: 角色管理
# Author: houpp
# AddTime: 2015-05-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .gl_jsgl_001_service import jsgl_service, data_service, data_add_service,data_edit_service,get_jsxx_service,\
    delete_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    data = {'jsfl_lst': []}
    try:
        # 调用操作数据库函数
        data = jsgl_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string("gl_jsgl/gl_jsgl_001/gl_jsgl_001.html", data)

@register_url('GET')
def jsgl_view():
    """
    # 角色管理页面的跳转 并附有一个下拉列表的值
    """
    data = {'jsfl_lst': []}
    try:
        # 调用操作数据库函数
        data = jsgl_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string("gl_jsgl/gl_jsgl_001/gl_jsgl_001.html", data)

@register_url('POST')
def data_view():
    """
    # 自动发起表格数据查询
    """
    # 初始化反馈信息
    data = {'total': 0, 'rows': []}
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 角色名称
        jsmc = request.POST.jsmc
        # 角色代码
        jsdm = request.POST.jsdm
        # 角色分类
        jsfl = request.POST.jsfl
        # 组织调用函数字典
        data_dic = {'jsmc': jsmc, 'jsfl': jsfl, 'jsdm': jsdm, 'rn_start': rn_start, 'rn_end': rn_end}
        # 调用操作数据库函数
        data = data_service(data_dic)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def add_js_view():
    """
    #新增角色信息
    :return:
    """
    # 获取前台页面数据
    # 获取角色代码
    jsdm = request.POST.jsdm
    # 获取角色名称
    jsmc = request.POST.jsmc
    #获取角色分类
    jsfl = request.POST.jsfl
    #获取角色描述
    jsms = request.POST.jsms
    #组织数据
    sql_data = {'jsdm':jsdm, 'jsmc': jsmc, 'jsfl': jsfl,
                'jsms': jsms, 'sfsc': '0'}

    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_add_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    return  result_data

@register_url('POST')
def edit_js_view():
    """
    #编辑角色信息
    :return:
    """
    #获取页面数据
    # 角色id
    id = request.POST.jsid
    # 角色名称
    jsmc = request.POST.jsmc
    # 角色代码
    jsdm = request.POST.jsdmhid
    #获取角色分类
    jsfl = request.POST.jsfl
    #获取角色描述
    jsms = request.POST.jsms
    #组织数据
    sql_data = {'id':id, 'jsdm': jsdm, 'jsmc': jsmc, 'jsfl': jsfl,
                'jsms': jsms}

    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_edit_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    return  result_data

@register_url('POST')
def del_js_view():
    """
    #角色删除
    :return:
    """
    #获取删除数据
    #角色ID列表
    ids = request.POST.id
    #初始化
    result_data = {'state':False,'msg':''}
    #前台传入角色ID列表
    sql_data = {'ids':ids}
    try:
        #调用后台service
        result_data = delete_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '删除失败！异常错误!'
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def get_jsxx_view():
    """
    # 获取角色信息
    :return:
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','gnxx':{}}
    # 获取前台传入的id
    id= request.POST.id
    try:
        data = get_jsxx_service(id)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取角色信息失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data
