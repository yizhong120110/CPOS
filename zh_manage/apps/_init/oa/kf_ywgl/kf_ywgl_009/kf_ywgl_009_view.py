# -*- coding: utf-8 -*-
# Action: 流程-自动化测试
# Author: liuhh
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_009_service import get_csaldylb_service, csal_jbxx_service,csal_jdxx_service,csal_jdxx_jbxx_service,csal_demo_service,csal_demo_datagrid_service

@register_url('GET')
def index_view():
    """
    # 流程-测试案例列表页面
    """
    # 流程测试案例定义表id
    ssid = request.GET.ssid
    # 流程测试案例定义表所属类别
    sslb = request.GET.sslb
    # 流程测试案例定义表类别
    lb = request.GET.lb
    return render_to_string("kf_ywgl/kf_ywgl_009/kf_ywgl_009.html",{"ssid":ssid, "sslb":sslb, "lb":lb})

@register_url('GET')
def get_csaldylb_view():
    """
    # 流程-测试案例列表
    """
    # 流程测试案例定义所属ID
    ssid = request.GET.ssid
    # 流程测试案例定义表所属类别
    sslb = request.GET.sslb
    # 流程测试案例定义表类别
    lb = request.GET.lb

    # 返回对象
    result = {'total':0,'rows':[]}
    try:
       result = get_csaldylb_service(ssid, sslb, lb, request.rn_start, request.rn_end)
    except:
        logger.info(traceback.format_exc())
    return  result

@register_url('GET')
def csal_jbxx_view():
    """
    # 流程测试案例查看-基本信息的页面
    """
    # 流程测试案例定义表id
    csalid = request.GET.csalid
    # 返回对象
    result = {}
    try:
       result = csal_jbxx_service({'csalid':csalid})
       result['csalid']=csalid
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_009/kf_ywgl_009_csal_jbxx.html",result)

@register_url('GET')
def csal_jdxx_view():
    """
    # 流程测试案例查看-节点信息的页面
    """
    # 流程测试案例定义表id
    csalid = request.GET.csalid
    # 返回值
    result = {'rows':[]}
    try:
       result = csal_jdxx_service({'csalid':csalid,'lx':request.GET.lx})
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_009/kf_ywgl_009_csal_jdxx.html",result)

@register_url('GET')
def csal_jdxx_jbxx_view():
    """
    # 流程测试案例查看-节点信息基本信息的页面
    """
    # 节点测试案例执行步骤ID
    jdcsalzxbzid = request.GET.jdcsalzxbzid
    # 节点测试案例的执行步骤的demoid
    demoid = request.GET.demoid
    # 类型
    lx = request.GET.demoid
    #返回值
    result = {'srys':[], 'scys':[], 'demoid':demoid }
    try:
       result = csal_jdxx_jbxx_service({'jdcsalzxbzid':jdcsalzxbzid})
       result['srys'] = json.dumps(result['srys'])
       result['scys'] = json.dumps(result['scys'])
       result["demoid"] = demoid
       request["lx"] = lx
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_009/kf_ywgl_009_csal_jdxx_jbxx.html",result)

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
    return render_to_string("kf_ywgl/kf_ywgl_009/kf_ywgl_009_csal_demo.html",result)

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
    return  result