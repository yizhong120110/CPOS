# -*- coding: utf-8 -*-
# Action: 维护系统导出
# Author: zhangzhf
# AddTime: 2015-10-19
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request, render_to_string
from .yw_pzsj_002_service import data_service,dc_service

@register_url('GET')
def index_view():
    """
    # 业务系统导出页面加载view
    """
    return render_to_string("yw_pzsj/yw_pzsj_002/yw_pzsj_002.html")
    
@register_url('POST')
def data_view():
    """
    # 获取要导出信息的view
    """
    # 数据结构    
    data = {'state':False, 'msg':'没有可导出的对象', 'return_data':[], 'have':False}
    try:
        # 调用service
        data = data_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取导出信息失败！异常错误提示信息\n[%s]' % error_msg
    return json.dumps(data)

@register_url('POST')
def dc_view():
    """
    # 导出的view
    """
    # 数据结构    
    data = {'state':False, 'msg':'导出失败'}
    dcms = request.forms.dcms
    bzxx = request.forms.bzxx
    try:
        # 调用service
        data = dc_service({'dcms':dcms, 'bzxx':bzxx})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '导出失败失败！异常错误提示信息\n[%s]' % error_msg
    return data
    