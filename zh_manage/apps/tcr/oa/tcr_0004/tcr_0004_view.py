# -*- coding: utf-8 -*-

import traceback
from sjzhtspj import logger, request, render_to_string
from .tcr_0004_service import data_service

@register_url('GET')
def index_view():
    """
    # 库存监控
    """

    # 前一个页面传过来的值 
    tcrid = request.GET.tcrid
    data = {'tcrid': tcrid}

    return render_to_string('tcr_0004/tcr_0004.html', data)

@register_url('POST')
def get_data():
    """
    # 获取库存信息
    """
    # 数据结构
    data = {}
    try:
        sql_data = {}
        sql_data['tcrid'] = request.forms.tcrid

        print('zhangxd>>>>>>>>>>>>%s' % request.forms.tcrid)
        # 调用service
        data = data_service(sql_data)
        print('zhangxd>>>>>>>>>>>>%s' % data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data
