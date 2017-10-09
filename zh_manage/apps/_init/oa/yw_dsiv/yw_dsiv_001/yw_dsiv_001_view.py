# -*- coding: utf-8 -*-
# Action: 运维数据库表信息查看
# Author: fangch
# AddTime: 2015-04-08
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_dsiv_001_service import data_service

@register_url('GET')
def index_view():
    """
    # 运维数据库表信息查看 业务信息页面
    """
    # 访问此功能的平台
    pt = request.GET.pt
    # 默认为yx平台，yx平台只可查看，不可操作
    data = {'pt': pt if pt else 'yx'}
    return render_to_string("yw_dsiv/yw_dsiv_001/yw_dsiv_001.html",data)

@register_url('GET')
def data_view():
    """
    # 业务信息json数据
    """
    params = { 'rn_start': request.rn_start, 'rn_end': request.rn_end}
    
    data = {'total':0, 'rows':[]}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    return data