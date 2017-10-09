# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 Demo数据查看view
# Author: 周林基
# AddTime: 2015-2-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import logger, request,render_to_string, render_string
from .kf_ywgl_013_jyxqck_csal_ck_demo_service import csal_demo_service,csal_demo_datagrid_service

@register_url('GET')
def csal_demo_view():
    """
    # 流程测试案例查看-Demo信息的页面
    """
    #节点测试案例的执行步骤的demoid
    demoid = request.GET.demoid
    #返回值
    result = {'demo':{},'demojbxxsjb':[]}
    try:
       result = csal_demo_service({'demoid':demoid})
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_demo.html",result)

@register_url('POST')
def csal_demo_datagrid_view():
    """
    # 流程-测试案例列表-demo信息
    """
    # 流程-测试案例列表-demo信息对应的数据模型的ID
    sjkmxdyid = request.POST.sjkmxdyid
    # 流程-测试案例列表-demo信息对应的数据模型的ID
    sjbid = request.POST.sjbid
    # 返回对象
    result =  {"columns":[], "rows":[]}
    try:
       result = csal_demo_datagrid_service(sjkmxdyid, sjbid)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '获取信息失败！异常错误提示信息[%s]' % error_msg
    return  result