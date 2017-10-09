# -*- coding: utf-8 -*-
# Action: 菜单管理
# Author: houpp
# AddTime: 2015-05-26
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .gl_cdgl_001_service import  lst_service, index_service,data_service,gnlb_service , \
    data_add_service, data_edit_service,del_cd_service, data_addGn_service,data_editGn_service,del_gn_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    # 平台
    # cddm = request.GET.menuDm
    # # 初始化反馈前台信息
    # data = { 'an_lst': []}
    # try:
    #     # 组织请求信息字典
    #     sql_data = { 'cddm': cddm }
    #     # 调用数据库操作函数
    #     # data = index_service( sql_data )
    #     data = anqx_service( sql_data )
    # except:
    #     # 查询出现异常时，将异常信息写入到日志文件中
    #     logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string("gl_cdgl/gl_cdgl_001/gl_cdgl_001.html")

@register_url('POST')
def lst_view():
    """
    # 目录选择时执行的页面跳转
    """
    # 获取前台页面数据
    # 菜单ID
    cdid = request.POST.cdid
    #按钮功能ID
    gnid = request.POST.gnid

    data = {'state':False,'msg':'','sjcd_lst':[],'cdfl_lst': [],'dlxt_lst':[],'gnxx':{},'cdxx':{} }
    sql_data = {'cdid':cdid,'gnid':gnid}
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
def gnlb_view():
    """
    # 获取功能菜单列表
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 前台获取菜单id
    cdid = request.POST.cdid
    sql_data = {'cdid':cdid}
    try:
        # 调用操作数据库的函数
        data = gnlb_service(sql_data)

    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return  data


@register_url('POST')
def add_cd_view():
    """
    # 增加菜单
    :return:
    """
    # 获取前台页面数据
    # 菜单名称
    cdmc = request.POST.cdmc
    # 菜单代码
    cddm = request.POST.cddm
    # 访问地址
    url = request.POST.url
    # 菜单分类
    cdfl = request.POST.cdfl
    #     排序号
    pxh = request.POST.pxh
    #上级菜单
    sjcd = request.POST.sjcd
    if sjcd=='':
        sjcd='0'

    # 所属系统
    ssxt = request.POST.ssxt
    # 备注
    bz = request.POST.bz
    # 组织数据结构
    sql_data = {'cdmc':cdmc, 'url':url, 'cdfl':cdfl, 'pxh':pxh, 'sjcd':sjcd, 'ssxt': ssxt, 'bz':bz
                ,'cddm':cddm
    }
    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_add_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '新增菜单失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def edit_cd_view():
    """
    # 编辑菜单
    :return:
    """
    # 获取前台页面数据
    # 菜单ID
    cdid = request.POST.cdid
    # 菜单名称
    cdmc = request.POST.cdmc
    # 访问地址
    url = request.POST.url
    # 菜单分类
    cdfl = request.POST.cdfl
    #     排序号
    pxh = request.POST.pxh
    #上级菜单
    sjcd = request.POST.sjcd
    # 所属系统
    ssxt = request.POST.ssxt
    # 备注
    bz = request.POST.bz
    # 组织数据结构
    sql_data = {'cdid': cdid, 'cdmc':cdmc, 'url':url, 'cdfl':cdfl, 'pxh':pxh, 'sjcd':sjcd,'ssxt':ssxt, 'bz':bz
    }
    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_edit_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '编辑菜单失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def del_cd_view():
    """
    # 删除菜单
    :return:
    """
    # 获取前台选择的数据
    # 菜单ID
    cdid = request.POST.id
    # 菜单名称
    cdmc = request.POST.cdmc
    # 来源
    ly = request.POST.ly
    # 组织数据结构
    sql_data = {'id': cdid, 'cdmc':cdmc, 'ly':ly }

    # 初始化返回值
    result_data = {'state':False, 'msg':''}
    try:
        result_data = del_cd_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '删除失败！异常错误提示信息[%s]\n' % error_msg
    return  result_data

@register_url('POST')
def add_gn_view():
    """
    # 给菜单增加功能
    :return:
    """
    # 获取前台页面数据
    # 菜单id
    cdid = request.POST.cdid_gn
    # 菜单名称
    cdmc = request.POST.cdmc_gn
    # 功能代码
    gndm = request.POST.gndm
    # 功能名称
    gnmc = request.POST.gnmc
    # 备注
    bz = request.POST.sm
    # 组织数据结构
    sql_data = {'cdid':cdid, 'cdmc':cdmc, 'gndm':gndm, 'gnmc':gnmc, 'bz':bz
    }
    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_addGn_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '新增功能失败！异常错误提示信息\n[%s]' % error_msg
    return  result_data

@register_url('POST')
def edit_gn_view():
    """
    # 编辑功能
    :return:
    """
    # 获取前台页面数据
    # 菜单ID
    cdid = request.POST.cdid_gn
    # 功能id
    gnid = request.POST.gnid
    # 功能代码
    gndm = request.POST.gndmhid
    # 功能名称
    gnmc = request.POST.gnmc
    # 备注
    bz = request.POST.sm
    # 组织数据结构
    sql_data = {'gnid':gnid, 'cdid':cdid, 'gndm':gndm, 'gnmc':gnmc, 'bz':bz
    }
    #初始化返回值
    result_data = {'state': False, 'msg': ''}
    try:
        result_data = data_editGn_service(sql_data)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '编辑功能失败！异常错误提示信息[%s]' % error_msg
    return  result_data

@register_url('POST')
def del_gn_view():
    """
    # 批量删除功能
    :return:
    """
    # 获取前台数据
    # 功能id列表
    ids = request.POST.id
    # 菜单名称
    cdmc = request.POST.cdmc
    #初始化
    result_data = {'state':False,'msg':''}
    #前台传入角色ID列表
    sql_data = {'ids':ids, 'cdmc':cdmc}
    try:
        #调用后台service
        result_data = del_gn_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result_data['msg'] = '删除功能失败！异常错误\n[%s]' % error_msg
    # 将结果反馈给前台
    return result_data














