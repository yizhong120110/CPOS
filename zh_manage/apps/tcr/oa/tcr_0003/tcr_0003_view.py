# -*- coding: utf-8 -*-

import json
import traceback
from sjzhtspj import logger, request, render_to_string, get_sess
from .tcr_0003_service import data_service
from libs_local.sjzhtspj.common import get_sess_hydm
from ops.core.rpc import call_jy_reply

@register_url('GET')
def index_view():
    """
    # 终端列表页面
    """
    data = {}

    return render_to_string('tcr_0003/tcr_0003.html', data)

@register_url('POST')
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
        sql_data = {'rn_start': rn_start, 'rn_end': rn_end}
        # 终端名称
        sql_data['tcrmc'] = request.forms.tcrmc

        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data
