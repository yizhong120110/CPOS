# -*- coding: utf-8 -*-
# Action: 菜单管理
# Author: houpp
# AddTime: 2015-05-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .gl_bmgl_001_service import lst_service,data_service,\
    data_add_service,get_bmxx_service,data_edit_service,delete_service,check_qx_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    # 页面跳转执行
    return render_to_string("gl_bmgl/gl_bmgl_001/gl_bmgl_001.html")

@register_url('POST')
def lst_view():
    """
    # 目录选择时执行的页面跳转
    """
    data = {'state':False,'msg':'','bmfl_lst': [],'sjbm_lst':[] ,'bmxx':{},'flag':'0','bmid_login':''}
    # 获取前台传入的部门id
    bmid = request.POST.bmid
    sql_data = {'bmid':bmid}
    try:
        # 调用操作数据库函数
        data = lst_service(sql_data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    # 页面跳转执行
    return data

@register_url('POST')
def data_view():
    """
    # 自动发起表格数据查询
    """
    # 初始化反馈信息
    data = {'total': 0, 'rows': []}
    try:
         # 调用操作数据库函数
        data = data_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 将组织的结果反馈给前台
    return data


@register_url('POST')
def add_bm_view():
    """
    #新增部门信息
    :return:
    """
    # 获取前台页面数据
    # 获取部门代码
    bmdm = request.POST.bmdm
    # 获取部门名称
    bmmc = request.POST.bmmc
    #获取部门分类
    bmfl = request.POST.bmfl
    #获取主负责人
    zfzr = request.POST.zfzr
    # 获取电话
    dh = request.POST.dh
    # 获取传真
    cz = request.POST.cz
    # 获取地址
    dz = request.POST.dz
    # 上级部门
    sjbm = request.POST.sjbm
    if sjbm=='':
        sjbm='0'
    # 排序号
    pxh = request.POST.pxh
    if pxh =='':
        pxh =='1'
    # 备注
    bz = request.POST.bz

    #组织数据
    sql_data = { 'bmdm':bmdm, 'bmmc': bmmc, 'bmfl': bmfl,
                'zfzr': zfzr, 'dh': dh, 'cz':cz, 'dz':dz,
                'sjbm':sjbm, 'bz':bz, 'pxh': pxh, 'scbz':'0'}

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
def edit_bm_view():
    """
    #编辑部门信息
    :return:
    """
    # 获取前台页面数据
    # 获取部门代码
    bmdm = request.POST.bmdm
    bmid = request.POST.bmid
    # 获取部门名称
    bmmc = request.POST.bmmc
    #获取部门分类
    bmfl = request.POST.bmfl
    #获取主负责人
    zfzr = request.POST.zfzr
    # 获取电话
    dh = request.POST.dh
    # 获取传真
    cz = request.POST.cz
    # 获取地址
    dz = request.POST.dz
    # 上级部门
    sjbm = request.POST.sjbm
    if sjbm=='':
        sjbm='0'
    # 排序号
    pxh = request.POST.pxh
    if pxh =='':
        pxh =='1'
    # 备注
    bz = request.POST.bz

    #组织数据
    sql_data = {'bmid': bmid,'bmdm':bmdm, 'bmmc': bmmc, 'bmfl': bmfl,
                'zfzr': zfzr, 'dh': dh, 'cz':cz, 'dz':dz,
                'sjbm':sjbm, 'bz':bz, 'pxh': pxh, 'scbz':'0'}

    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_edit_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def del_bm_view():
    """
    # 删除部门
    :return:
    """
    #获取删除数据
    #部门ID列表
    id = request.POST.id
    # 部门名称
    bmmc = request.POST.bmmc

    #初始化
    result_data = {'state':False,'msg':''}
    #前台传入部门ID列表
    sql_data = {'id':id, 'bmmc': bmmc }
    try:
        #调用后台service
        result_data = delete_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '删除失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data

@register_url('POST')
def get_bmxx_view():
    """
    # 获取部门信息
    :return:
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','bmxx':{},'flag':'0'}
    # 获取前台传入的id
    id= request.POST.id
    try:
        data = get_bmxx_service(id)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取部门信息失败！异常错误提示信息\n[%s]' % error_msg
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
        result_data['msg'] = '获取所属部门失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data
