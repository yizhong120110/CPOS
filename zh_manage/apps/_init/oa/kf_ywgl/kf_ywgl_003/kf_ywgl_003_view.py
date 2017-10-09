# -*- coding: utf-8 -*-
# Action: 交易基本信息
# Author: gaorj
# AddTime: 2014-12-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from .kf_ywgl_003_service import index_service, data_service, data_add_service, data_del_service, data_edit_service, jbxx_edit_service, zdfqpzfy_service


@register_url('GET')
def index_view():
    """
    # 交易基本信息url
    """
    # 平台
    pt = request.GET.pt
    # 交易ID
    jyid = request.GET.jyid
    params = {'id': jyid}
    
    jy_dic = {'id':jyid, 'jym':'', 'jymc':'', 'jyms':'', 'zt':'', 'timeout':'', 'zdfqpz':''}
    data = {'jy_dic':jy_dic, 'zones':[]}
    
    try:
        data = index_service(params)
    except:
        logger.info(traceback.format_exc())
    
    # 默认是到交易的基本信息页面
    url_html = "kf_ywgl/kf_ywgl_003/kf_ywgl_003_index.html"
    # 当pt存在且是wh时，到参数基本信息页面
    if pt == 'wh':
        url_html = "yw_csgl/yw_csgl_003/yw_csgl_003_jbxx.html"
    
    return render_to_string( url_html, data )

@register_url('GET')
def data_view():
    """
    # 交易参数json数据
    """
    # 交易ID
    jyid = request.GET.jyid
    params = {'rn_start': request.rn_start, 'rn_end': request.rn_end, 'ssid': jyid}
    
    data = {'total':0, 'rows':[]}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def data_add_view():
    """
    # 交易参数新增
    """
    # 平台
    pt = request.forms.pt
    # 交易ID
    jyid = request.forms.jyid
    # 交易码
    jym = request.forms.jym
    # 参数代码
    csdm = request.forms.csdm
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    params = {'ssid': jyid, 'jym': jym, 'csdm': csdm, 'value': csz, 'csms': csms, 'zt': cszt, 'pt': pt}
    
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
    # 交易参数删除
    """
    # 平台
    pt = request.forms.pt
    # 多个ID，逗号分隔
    ids = request.forms.ids
    # 交易码
    jym = request.forms.jym
    params = {'ids': ids, 'jym': jym, 'pt': pt}
    
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
    # 交易参数编辑
    """
    # 平台
    pt = request.forms.pt
    # 参数ID
    csid = request.forms.csid
    # 交易码
    jym = request.forms.jym
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    params = {'id': csid, 'jym': jym, 'value': csz, 'csms': csms, 'zt': cszt, 'pt': pt}
    
    result = {'state':False, 'msg':''}
    try:
        result = data_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def jbxx_edit_view():
    """
    # 交易基本信息编辑
    """
    # 交易ID
    id = request.forms.id
    # 交易名称
    jymc = request.forms.jymc
    # 交易描述
    jyms = request.forms.jyms
    # 交易码
    jym = request.forms.jym
    # 交易状态 '0'禁用 '1'启用
    zt = request.forms.zt
    # 交易超时时间
    timeout = request.forms.timeout
    # 交易自动发起配置
    zdfqpz = request.forms.zdfqpz
    # 原交易状态 '0'禁用 '1'启用
    yzt = request.forms.yzt
    # 原交易自动发起配置
    yzdfqpz = request.forms.yzdfqpz
    params = {'id': id, 'jymc': jymc, 'jyms': jyms, 'jym': jym, 'zt': zt, 'timeout': timeout, 'zdfqpz': zdfqpz, 'zdfqpzsm': '',
            'yzt': yzt, 'yzdfqpz': yzdfqpz }
    # 初始化返回默认值
    result = {'state':False, 'msg':''}
    try:
        result = jbxx_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def zdfqpzfy_view():
    """
    # 自动发起配置翻译
    """
    # 自动发起配置
    zdfqpz = request.POST.zdfqpz
    result = {'state':False, 'msg':'', 'zdfqpzsm': ''}
    try:
        result = zdfqpzfy_service({"zdfqpz": zdfqpz})
    except:
        # 翻译出现异常
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '翻译失败！异常错误提示信息[%s]' % error_msg
    return result