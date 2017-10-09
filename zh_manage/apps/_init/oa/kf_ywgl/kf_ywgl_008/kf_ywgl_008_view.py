# -*- coding: utf-8 -*-
# Action: 子流程基本信息url
# Author: zhangzf
# AddTime: 2015-1-6
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_008_service import index_service, update_service

@register_url('GET')
def index_view():
    """
    # 子流程-基本信息
    """
    # 子流程id
    zlcid = request.GET.zlcid
    # 返回对象
    result = {}
    try:
       result = index_service({'zlcid':zlcid})
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_008/kf_ywgl_008.html", {'zlc': result})

@register_url('POST')
def update_view():
    """
    # 子流程-基本信息
    """
    # 子流程ID
    id = request.forms.id
    # 子流程描述
    ms = request.forms.ms
    # 子流程名称
    mc = request.forms.mc
    # 返回对象
    result = {'state': False, 'msg':''}
    try:
       result = update_service({'id':id, 'ms':ms, 'mc':mc, 'zlcid':id})
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
