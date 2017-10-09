# -*- coding: utf-8 -*-
# Action: 业务基本信息
# Author: gaorj
# AddTime: 2014-12-26
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .kf_ywgl_002_service import index_service, jbxx_edit_service, data_service, data_add_service, data_del_service, data_edit_service


@register_url('GET')
def index_view():
    """
    # 业务基本信息url
    """
    pt = request.GET.pt
    ywid = request.GET.ywid
    params = {'ywid': ywid}
    
    yw_dic = {'id':ywid, 'ywbm':'', 'ywmc':'', 'ywms':''}
    data = {'yw_dic':yw_dic, 'zones':[]}
    try:
        data = index_service(params)
    except:
        logger.info(traceback.format_exc())
    # 默认是到业务的基本信息页面
    url_html = "kf_ywgl/kf_ywgl_002/kf_ywgl_002.html"
    # 当pt存在且是wh时，到参数基本信息页面
    if pt == 'wh':
        url_html = "yw_csgl/yw_csgl_002/yw_csgl_002_jbxx.html"
    # 平台
    data['pt'] = pt
    
    return render_to_string( url_html, data )

@register_url('POST')
def jbxx_edit_view():
    """
    # 业务基本信息编辑
    """
    # 业务ID
    id = request.forms.id
    # 业务名称
    ywmc = request.forms.ywmc
    # 业务描述
    ywms = request.forms.ywms
    # 业务简称
    ywbm = request.forms.ywbm
    params = {'id': id, 'ywmc': ywmc, 'ywms': ywms, 'ywbm': ywbm}
    
    result = {'state':False, 'msg':''}
    try:
        result = jbxx_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def data_view():
    """
    # 业务参数json数据
    """
    # 业务ID
    ywid = request.GET.ywid
    params = {'rn_start': request.rn_start, 'rn_end': request.rn_end, 'ywid': ywid}
    
    data = {'total':0, 'rows':[]}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def data_add_view():
    """
    # 业务参数新增
    """
    # 平台
    pt = request.forms.pt
    # 业务ID
    ywid = request.forms.ywid
    # 参数代码
    csdm = request.forms.csdm
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    params = {'ywid': ywid, 'csdm': csdm, 'csz': csz, 'csms': csms, 'cszt': cszt, 'pt': pt}
    
    result = {'state':False, 'msg':''}
    try:
        result = data_add_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 业务参数删除
    """
    # 平台
    pt = request.POST.pt
    ids = request.POST.ids
    ywid = request.POST.ywid
    params = {'ids': ids, 'pt': pt, 'ywid': ywid}
    result = {'state':False, 'msg':''}
    try:
        result = data_del_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 业务参数修改
    """
    # 平台
    pt = request.forms.pt
    # 参数ID
    csid = request.forms.csid
    # 参数代码
    csdm = request.forms.csdm
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    # 业务id
    ywid = request.forms.ywid
    params = {'csid': csid, 'csdm': csdm, 'csz': csz, 'csms': csms, 'cszt': cszt, 'pt': pt, 'ywid': ywid}
    
    result = {'state':False, 'msg':''}
    try:
        result = data_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
