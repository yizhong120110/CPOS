# -*- coding: utf-8 -*-
# Action: 打印配置 view
# Author: zhangchl
# AddTime: 2015-01-08
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request,render_to_string, get_sess_hydm
from .kf_ywgl_018_service import data_service, data_add_sel_service, data_add_service, data_edit_sel_service, data_edit_service, data_del_service


@register_url('GET')
def index_view():
    """
    # 打印配置列表首页
    """
    ywid = request.GET.ywid
    data = {'ywid':ywid}
    return render_to_string("kf_ywgl/kf_ywgl_018/kf_ywgl_018.html", data)

@register_url('GET')
def data_view():
    """
    # 打印配置信息获取data
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 业务id
        ywid = request.GET.ywid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'ywid': ywid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def data_add_sel_view():
    """
    # 打印配置新增页面参数查询
    """
    # 反馈信息
    result = {'state': False, 'msg': '', 'ywid':'', 'mblx_lst':[]}
    try:
        # 业务id
        ywid = request.POST.ywid
        # 组织调用函数字典
        data_dic = { 'ywid': ywid }
        # 调用操作数据库函数
        result = data_add_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_add_view():
    """
    # 打印配置新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 当前登录人
        hydm = get_sess_hydm()
        # 所属业务id
        ywid = request.forms.ywid
        # 模板类型
        mblx = request.forms.mblx
        # 模板名称
        mbmc = request.forms.mbmc
        # 模板描述
        mbms = request.forms.mbms
        # 模板内容
        nr = request.forms.hsnr
        # 组织调用函数字典
        data_dic = { 'hydm': hydm, 'ywid': ywid,
            'mblx': mblx, 'mbmc': mbmc, 'mbms': mbms,
            'nr': nr }
        # 调用操作数据库函数
        result = data_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_sel_view():
    """
    # 打印配置编辑前查询
    """
    # 反馈信息
    result = {'state': False, 'msg':'', 'mblx_lst':''}
    try:
        # 打印模板配置id
        id = request.forms.id
        # 组织调用函数字典
        data_dic = { 'dymbdy_id': id }
        # 组织调用函数字典
        result = data_edit_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 打印配置编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 所属业务id
        ywid = request.forms.ywid
        # 当前登录人
        hydm = get_sess_hydm()
        # 模板类型
        mblx = request.forms.mblx
        # 模板描述
        mbms = request.forms.mbms
        # 模板内容
        nr = request.forms.hsnr
        # 打印模板定义表id
        dyid = request.forms.dyid
        # blob表定义id
        blob_id = request.forms.blobid
        # 组织调用函数字典
        data_dic = { 'ywid': ywid, 'hydm': hydm, 'mblx': mblx,
        'mbms': mbms, 'nr': nr, 'dyid': dyid, 'blob_id': blob_id }
        # 调用操作数据库函数
        result = data_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 打印配置删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 所属业务id
        ywid = request.forms.ywid
        # 要删除的打印模板id
        ids = request.forms.ids
        # 要删除的打印模板描述
        dymss = request.forms.dymss
        # 组织调用函数字典
        data_dic = { 'ywid': ywid, 'ids': ids, 'dymss': dymss }
        # 调用操作数据库函数
        result = data_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result