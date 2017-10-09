# -*- coding: utf-8 -*-
# Action: 监控管理-监控对象管理
# Author: zhangzhf
# AddTime: 2015-04-08
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string,get_sess_hydm
from .yw_jkgl_002_service import index_service,data_service,add_service,del_service,edit_service,able_service,get_dxlx_service,get_edit_service
from sjzhtspj.common import get_strftime

@register_url('GET')
def index_view():
    """
    # 管理对象列表页面
    """
    # 数据结构    
    data = {'dxlx':[], 'dxzt':[]}
    try:
        # 调用service
        data = index_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    return render_to_string("yw_jkgl/yw_jkgl_002/yw_jkgl_002.html", data)

@register_url('GET')
def data_view():
    """
    # 获取管理对象列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end }
        # 对象类型
        sql_data['dxlx'] = request.GET.dxlx
        # 对象编码
        sql_data['dxbm'] = request.GET.dxbm
        # 对象名称
        sql_data['dxmc'] = request.GET.dxmc
        # 对象状态
        sql_data['dxzt'] = request.GET.dxzt
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def add_view():
    """
    # 添加监控管理-监控对象
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 对象编码
        dxbm = request.forms.jkdx_dxbm   
        # 主机类型
        zjlx = request.forms.jkdx_zjlx   
        # 对象类型
        dxlx = request.forms.jkdx_dxlx   
        # 对象名称
        dxmc = request.forms.jkdx_dxmc   
        # 对象描述
        dxms = request.forms.jkdx_dxms   
        # 状态
        zt = request.forms.dxzt   
        # 操作人
        czr = get_sess_hydm()
        # 操作时间
        czsj = get_strftime()
        sql_data = {'dxbm':dxbm,'dxlx':dxlx,'zjlx':zjlx,'dxmc':dxmc,'dxms':dxms,'zt':zt,'czr':czr,'czsj':czsj}
        data = add_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def del_view():
    """
    # 删除监控管理-监控对象
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    # 要删除的管理对象的id
    ids = request.forms.ids   
    try:
        data = del_service(ids)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def edit_view():
    """
    # 编辑监控管理-监控对象
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 对象编码
        dxbm = request.forms.jkdx_dxbm_hid
        # 对象类型
        dxlx = request.forms.hid_jkdx_dxlx   
        # 对象名称
        dxmc = request.forms.jkdx_dxmc   
        # 原对象名称
        dxmc_old = request.forms.jkdx_dxmc_old   
        # 对象描述
        dxms = request.forms.jkdx_dxms  
        # 操作人
        czr = get_sess_hydm()
        # 操作时间
        czsj = get_strftime()
        # id
        id = request.forms.jkdx_id   
        sql_data = {'dxbm':dxbm,'dxlx':dxlx,'dxmc':dxmc,'dxms':dxms,'czr':czr,'czsj':czsj,'id':id,'dxmc_old':dxmc_old}
        data = edit_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def able_view():
    """
    # 监控对象启用
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    # 要启用的管理对象的id
    ids = request.forms.ids   
    # 禁用启用标志
    zt = request.forms.zt
    try:
        data = able_service(ids,zt)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        xx = '启用' if zt == '1' else '禁用'
        data['msg'] = xx+'失败！异常错误提示信息[%s]' % error_msg
        
    # 将结果反馈给前台
    return data

@register_url('POST')
def get_dxlx_view():
    """
    # 获取对类型
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','list':[]}
    try:
        data = get_dxlx_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '获取对象类型失败！异常错误提示信息[%s]' % error_msg
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def get_edit_view():
    """
    # 获取对类型
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','jkdx':{}}
    # 监控对象id
    id = request.forms.id
    try:
        data = get_edit_service(id)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '获取监控对象内容失败！异常错误提示信息[%s]' % error_msg
    # 将结果反馈给前台
    return data