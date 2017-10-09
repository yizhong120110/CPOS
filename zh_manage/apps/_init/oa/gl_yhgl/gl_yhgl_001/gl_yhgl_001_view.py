# -*- coding: utf-8 -*-
# Action: 用户管理
# Author: houpp
# AddTime: 2015-05-14
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, redirect, render_to_string, logger
from .gl_yhgl_001_service import ( yhgl_service, data_service, data_add_service, data_edit_service,
    data_resetMm_service, delete_service, data_js_service ,data_qx_service, data_jslst_service,get_yhxx_service,
    check_qx_service )


@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    data = {'xb_lst': [],'bm_lst':[]}
    try:
        # 调用操作数据库函数
        data = yhgl_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string("gl_yhgl/gl_yhgl_001/gl_yhgl_001.html", data)

@register_url('POST')
def data_view():
    """
    # 自动发起表格数据查询
    """
    # 初始化反馈信息
    data = {'total': 0, 'rows': []}
    try:
        # 登录账户
        dlzh = request.POST.dlzh
        # 姓名
        xm = request.POST.xm
        # 手机
        sj = request.POST.sj
        # 部门
        bm = request.POST.bm
        # 性别
        xb = request.POST.xb
        # 计算rownum的开始和结束
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = {'dlzh': dlzh, 'xm': xm, 'sj': sj, 'xb': xb,'bm':bm ,'rn_start':rn_start, 'rn_end':rn_end}
        # 调用操作数据库函数
        data = data_service(data_dic)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def add_yh_view():
    """
    # 新增用户
    :return:
    """
    # 获取前台页面数据
    # 登录账号
    dlzh = request.POST.dlzh

    # 姓名
    xm = request.POST.xm
    # 性别
    xb = request.POST.xb
    # 手机
    sj = request.POST.sj
    # 出生日期
    csrq = request.POST.csrq
    # 电话
    dh = request.POST.dh
    # 电子邮箱
    dzyx = request.POST.dzyx
    # 所属部门
    ssbm= request.POST.ssbm

    # 备注
    bz = request.POST.bz
    #角色ID列表
    ids = request.POST.jsid
    # 组织数据
    sql_data = {
        'dlzh': dlzh,
        'xm': xm,
        'xb': xb,
        'sj': sj,
        'csrq': csrq,
        'dh': dh,
        'dzyx': dzyx,
        'ssbm': ssbm,
        'bz': bz,
        'sfsc':'0',
        'ids':ids
    }
    #初始化返回值
    result_data = {'state': False, 'msg': ''}

    try:
        result_data = data_add_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '新增失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def edit_yh_view():
    """
    #编辑用户管理
    :return:
    """
    #获取页面信息
    id = request.POST.yhid
    dlzh = request.POST.hydm
    xm = request.POST.xm
    xb = request.POST.xb
    sj = request.POST.sj
    csrq = request.POST.csrq
    dh = request.POST.dh
    dzyx = request.POST.dzyx
    ssbm = request.POST.ssbm
    bz = request.POST.bz
    #角色ID列表
    ids = request.POST.jsid

    #初始化返回值
    result_data = {'state': False, 'msg': ''}

    #组织数据
    sql_data = {
        'id':id,   # 主键
        'dlzh': dlzh, # 登录账号
        'mc': xm, # 姓名
        'xb': xb, # 性别
        'sj': sj, # 手机
        'csrq': csrq, # 出生日期
        'dh': dh, # 电话
        'dzyx': dzyx, # 电子邮箱
        'ssbm': ssbm ,# 所属部门
        #'bmid':bmid,
        'sm': bz, # 备注
        'ids':ids # 角色id
    }

    try:
        result_data = data_edit_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def resetMm_view():
    """
    # 密码重置
    :return:
    """
    #获取用户id
    yhid = request.POST.yhid
    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    sql_data = {
       'yhid': yhid,  # 用户ID
    }
    try:
        result_data = data_resetMm_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '密码重置失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def del_yh_view():
    """
    # 用户删除
    :return:
    """
    #获取删除数据
    #用户ID列表
    ids = request.POST.id
    #初始化
    result_data = {'state':False,'msg':''}
    #前台传入ID列表
    sql_data = {'ids':ids}
    try:
        #调用后台service
        result_data = delete_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '删除失败！异常错误\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def data_js_view():
    """
    # 获取用户角色和用户权限信息
    :return:
    """
    # 初始化返回数据
    result_data = { 'state':False, 'msg':'',  'rows':[], 'total':0 }
    # 获取前台页面用户id
    yhid = request.POST.id
    sql_data = {'yhid':yhid}
    try:
        #调用后台service
        result_data = data_js_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '获取数据失败！异常错误\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def data_qx_view():
    """
    # 获取用户角色和用户权限信息
    :return:
    """
    # 初始化返回数据
    result_data = { 'state':False, 'msg':'', 'rows':[], 'total':0 }
    # 获取前台页面用户id
    yhid = request.POST.yhid
    sql_data = {'yhid':yhid}
    try:
        #调用后台service
        result_data = data_qx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '获取数据失败！异常错误\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def data_jslst_view():
    """
    # 角色列表获取
    :return:
    """
    # 初始化返回值
    result_data = {'state': False, 'msg': '', 'rows': [], 'total': 0, 'js_exitLst': []}
    #获取前台页面用户id
    yhid = request.POST.id

    sql_data = {'yhid': yhid}
    try:
       #调用后台service
        result_data = data_jslst_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '获取数据失败！异常错误\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def get_yhxx_view():
    """
    # 获取部门信息
    :return:
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','yhxx':{},'xb_lst': [],'bm_lst':[]}
    # 获取前台传入的id
    id= request.POST.id
    try:
        data = get_yhxx_service(id)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取用户信息失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data

@register_url('POST')
def check_qx_view():
    """
    # 判断所属部门选择是否正确
    :return:
    """
    #获取选择的所属部门ID
    bmid = request.POST.bmid
    # 初始化返回值
    result_data = {'state': False, 'msg': ''}
    # 组织数据
    sql_data={'bmid':bmid}
    try:
        result_data = check_qx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '判断所属部门失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

