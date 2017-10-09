# -*- coding: utf-8 -*-
# Action: 导入历史 view
# Author: zhangchl
# AddTime: 2015-01-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request,render_to_string
from .kf_ywgl_022_service import data_service, data_edit_sel_service, data_edit_service, drht_sel_service, drht_service

@register_url('GET')
def index_view():
    """
    # 导入历史url
    """
    # 导入流水.内容类型
    #   yw:业务( 存在所属id )
    #   jy:交易( 不存在 )
    #   #jd:节点
    #   #sjb:数据表
    #   tx:通讯( 不存在 )
    #   #gghs:公共函数（业务）
    nrlx = request.GET.nrlx
    # 导入流水.所属ID列表
    ss_idlb = request.GET.ss_idlb
    
    # 组织反馈信息
    data = {'nrlx':nrlx, 'ss_idlb': ss_idlb}
    return render_to_string( "kf_ywgl/kf_ywgl_022/kf_ywgl_022.html", data )

@register_url('GET')
def data_view():
    """
    # 导入历史：获取显示数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 导入流水.内容类型
        nrlx = request.GET.nrlx
        # 导入流水.所属ID列表
        ss_idlb = request.GET.ss_idlb
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'nrlx': nrlx, 'ss_idlb': ss_idlb, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def data_edit_sel_view():
    """
    # 导入历史：信息编辑 页面初始化 view
    """
    # 反馈信息
    result = {'state': False, 'msg':'', 'drlsid':'', 'czms': '', 'bz': ''}
    try:
        # 导入id
        drlsid = request.forms.drlsid
        # 组织调用函数字典
        data_dic = { 'drlsid': drlsid }
        # 组织调用函数字典
        result = data_edit_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '获取页面初始化数据出现错误！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 导入历史：信息编辑 提交 view 
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 导入流水id
        drlsid = request.forms.drlsid
        # 操作描述
        czms = request.forms.czms
        # 操作描述
        bz = request.forms.bz
        # 组织调用函数字典
        data_dic = { 'drlsid': drlsid, 'czms': czms, 'bz': bz }
        # 调用操作数据库函数
        result = data_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def drht_sel_view():
    """
    # 导入回退 页面初始化 view
    """
    # 反馈信息
    result = {'state': False, 'msg':'', 'fhr_lst':[]}
    try:
        # 调用操作数据库函数
        result['fhr_lst'] = drht_sel_service()
        result['state'] = True
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '获取页面初始化数据出现错误！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def drht_view():
    """
    # 导入回退 提交 view
    """
    # 反馈信息
    result = {'state': False, 'msg':''}
    try:
        # 内容类型
        nrlx = request.forms.nrlx
        # 导入流水id
        drlsid = request.forms.drlsid
        # 回退描述
        htms = request.forms.htms
        # 备注
        bz = request.forms.bz
        # 复核人
        fhr = request.forms.fhr
        # 复核人密码
        fhrmm = request.forms.fhrmm
        # 组织调用函数字典
        data_dic = { 'nrlx': nrlx, 'drlsid': drlsid, 'htms': htms, 'bz': bz, 'fhr': fhr, 'fhrmm': fhrmm }
        # 调用操作数据库函数
        result = drht_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '导入回退失败！异常错误提示信息[%s]' % error_msg
    
    return result


