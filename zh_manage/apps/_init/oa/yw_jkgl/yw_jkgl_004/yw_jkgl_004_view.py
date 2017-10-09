# -*- coding: utf-8 -*-
# Action: 响应动作管理
# Author: zhangzhf
# AddTime: 2015-04-15
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string,get_sess_hydm
from .yw_jkgl_004_service import index_service,data_service,add_service,edit_service,crcs_data_service,crcs_edit_service,del_service,able_service,get_dmlx_service,get_xydz_service
from sjzhtspj.common import get_strftime,get_uuid

@register_url('GET')
def index_view():
    """
    # 响应动作管理列表页面
    """
    # 数据结构    
    data = {'dmlx':[], 'dxzt':[]}
    try:
        # 调用service
        data = index_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    return render_to_string("yw_jkgl/yw_jkgl_004/yw_jkgl_004.html", data)

@register_url('POST')
def data_view():
    """
    # 获取响应动作管理列表数据
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
        # 代码类型
        dmlx = request.forms.dmlx
        # 函数名称
        hsmc = request.forms.hsmc
        # 中文名称
        zwmc = request.forms.zwmc
        # 对象状态
        dxzt = request.forms.dxzt
        # 来源
        dxly = request.forms.dxly
        sql_data['dmlx'] = dmlx
        sql_data['hsmc'] = hsmc
        sql_data['zwmc'] = zwmc
        sql_data['dxzt'] = dxzt
        sql_data['dxly'] = dxly
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
    # 添加相应动作
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织保存数据
        # id
        id = get_uuid()
        # 函数名称
        hsmc = request.forms.hsmc
        # 中文名称
        zwmc = request.forms.zwmc
        # 代码类型
        dmlx = request.forms.dmlx
        # 描述
        ms = request.forms.ms
        # 操作人
        czr = get_sess_hydm()
        # 操作时间
        czsj = get_strftime()
        # 状态
        zt = request.forms.state   
        # 动作代码
        nodeBox = request.forms.nodeBox
        sql_data = {'hsmc':hsmc,'zwmc':zwmc,'dmlx':dmlx,'ms':ms,'zt':zt,'czr':czr,'czsj':czsj,'id':id,'nodeBox':nodeBox}
        data = add_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '新增失败！异常错误提示信息\n[%s]' % error_msg
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def edit_view():
    """
    # 更新相应动作
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织保存数据
        # id
        id = request.forms.hidXydz_id
        # 函数名称
        hsmc = request.forms.hsmc if request.forms.hsmc else request.forms.hidHsmc
        # 中文名称
        zwmc = request.forms.zwmc
        # 代码类型
        dmlx = request.forms.dmlx
        # 描述
        ms = request.forms.ms
        # 操作人
        czr = get_sess_hydm()
        # 操作时间
        czsj = get_strftime()
        # 状态
        zt = request.forms.state   
        # 内容id
        nr_id = request.forms.nr_id   
        # 动作代码
        nodeBox = request.forms.nodeBox
        sql_data = {'hsmc':hsmc,'zwmc':zwmc,'dmlx':dmlx,'ms':ms,'zt':zt,'czr':czr,'czsj':czsj,'id':id,'nodeBox':nodeBox, 'nr_id':nr_id}
        data = edit_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def crcs_data_view():
    """
    # 获取传入参数列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    try:
        # 组织查询信息
        sql_data = {'xydz_id':request.forms.xydz_id}
        # 调用service
        data = crcs_data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def crcs_edit_view():
    """
    # 添加传入参数
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织保存数据
        # id
        id = request.forms.crcs_id
        # 参数说明
        cssm = request.forms.cssm
        # 参数代码
        csdm = request.forms.csdm_d
        sql_data = {'cssm':cssm,'id':id,'csdm':csdm}
        data = crcs_edit_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def del_view():
    """
    # 删除响应对象
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    # 要删除的响应对象的id
    ids = request.forms.ids   
    try:
        data = del_service(ids)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除失败！异常错误提示信息\n[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def able_view():
    """
    # 响应动作启用
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    # 要启用的响应动作的id
    ids = request.forms.ids   
    # 禁用启用标志
    zt = request.forms.zt
    try:
        data = able_service(ids,zt)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        xx = '启用' if zt == '1' else '禁用'
        data['msg'] = xx+'失败！异常错误提示信息\n[%s]' % error_msg
        
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def get_dmlx():
    """
    # 获取代码类型
    """
    data = {'state':False, 'msg':'','list':[]}
    try:
        data = get_dmlx_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取代码类型失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def get_xydz():
    """
    # 获取响应动作内容
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','xydz':{}}
    # 监控对象id
    id = request.forms.id
    try:
        data = get_xydz_service(id)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取响应动作内容失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data