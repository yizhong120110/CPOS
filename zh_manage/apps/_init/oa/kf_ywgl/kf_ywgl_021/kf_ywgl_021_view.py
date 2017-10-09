# -*- coding: utf-8 -*-
# Action: 导出
# Author: jind
# AddTime: 2015-01-31
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import request,render_to_string,logger
from .kf_ywgl_021_service import index_service,data_service,data_export_jy_service,data_export_submit_service,data_wtjsj_service

@register_url('GET')
def index_view():
    """
    # 访问导出主页面
    """
    # 业务ID
    ywid = request.GET.ywid
    # 导出类型
    dclx = request.GET.dclx
    # 通讯ID
    txid = request.GET.txid
    data = {'ywid':ywid,'dclx':dclx,'txid':txid}
    try:
        data['xtlx'] = index_service()
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_021/kf_ywgl_021.html", data )
    
@register_url('POST')
def data_export_jy_view():
    """
    # 导出时校验是否有未提交的数据
    """
    # 业务ID
    ywid = request.forms.ywid
    # 导出类型
    dclx = request.forms.dclx
    # 通讯ID
    txid = request.forms.txid
    data = {'state':False,'msg':'','sfywtj':False}
    try:
        data['sfywtj'] = data_export_jy_service( ywid,dclx,txid )
        data['state'] = True
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data
        
@register_url('GET')
def data_view():
    """
    # 获取导出页面数据
    """
    ywid = request.GET.ywid
    dclx = request.GET.dclx
    txid = request.GET.txid
    data = {'state':False,'msg':'','rows':[] }
    try:
        data = data_service( ywid,dclx,txid )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data
    
@register_url('POST')
def data_wtjsj_view():
    """
    # 获取未提交数据
    """
    ywid = request.POST.ywid
    dclx = request.POST.dclx
    txid = request.POST.txid
    data = {'state':False,'msg':'','leftRows':'','rightRows':''}
    try:
        data = data_wtjsj_service( ywid,dclx,txid )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data
    
@register_url('POST')
def data_export_submit_view():
    """
    # 导出提交
    """
    # 导出描述
    dcms = request.forms.dcms
    # 备注信息
    bzxx = request.forms.bzxx
    # 业务ID
    ywid = request.forms.ywid
    # 导出类型
    dclx = request.forms.dclx
    # 系统类型
    xtlx = request.forms.xtlx
    # 交易列表
    jy_lst = json.loads( request.forms.jy_lst )
    # 子流程列表
    zlc_lst = json.loads( request.forms.zlc_lst )
    # 数据库模型列表
    sjkmx_lst = json.loads( request.forms.sjkmx_lst )
    # 公共函数列表
    gghs_lst = json.loads( request.forms.gghs_lst )
    # 节点列表
    jd_lst = json.loads( request.forms.jd_lst )
    # 通讯ID列表
    tx_id_lst = json.loads( request.forms.tx_id_lst )
    data = {'state':False,'msg':''}
    try:
        data = data_export_submit_service( ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx,dcms,bzxx,tx_id_lst )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '导出失败！异常错误提示信息[%s]' % error_msg
    return data

