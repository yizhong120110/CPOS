# -*- coding: utf-8 -*-
# Action: 自动化测试日志查看
# Author: liuhh
# AddTime: 2015-2-15
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_015_service import workflow_service,csal_jbxx_service,csal_jdxx_service,csal_jdxx_jbxx_service,get_rz_service,get_jdrz_service
@register_url('GET')
def index_view():
    """
    # 交易日志查看页面
    """
    csalid = request.GET.csalid 
    id = request.GET.id 
    lx = request.GET.lx
    pc = request.GET.pc
    zxjg = request.GET.zxjg
    jgsm = request.GET.jgsm
    lxdm = request.GET.lxdm if request.GET.lxdm else ''
    return render_to_string("kf_ywgl/kf_ywgl_015/kf_ywgl_015.html",{'id':id,'lx':lx,'pc':pc,'zxjg':zxjg,'jgsm':jgsm,'csalid':csalid,'lxdm':lxdm})

@register_url('POST')
def workflow_view():
    """
    # 查询工流程图
    """
    csalid = request.POST.csalid
    id = request.POST.id
    pc = request.POST.pc
    lx = request.POST.lx
    # 返回对象
    result = []
    try:
       result = workflow_service(id,pc,lx,csalid)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)

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
       result['lx'] = request.GET.lx
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_015/kf_ywgl_015_csal_jbxx.html",result)

@register_url('GET')
def csal_jdxx_view():
    """
    # 流程测试案例查看-节点执行步骤的页面
    """
    # 流程测试案例定义表id
    csalid = request.GET.csalid
    zxjg = request.GET.zxjg
    jgsm = request.GET.jgsm
    lx = request.GET.lx
    pc = request.GET.pc
    lxdm = request.GET.lxdm if request.GET.lxdm else ''
    # 返回值
    result = {'rows':[], 'zxjg':zxjg, 'jgsm':jgsm}
    try:
       result = csal_jdxx_service({'csalid':csalid,'zxjg':zxjg,'jgsm':jgsm,'lx':lx})
    except:
        logger.info(traceback.format_exc())
    result['csalid']=csalid
    result['lx'] = lx
    result['pc'] = pc
    result['lxdm'] = lxdm
    return render_to_string("kf_ywgl/kf_ywgl_015/kf_ywgl_015_csal_jdxx.html",result)

@register_url('GET')
def csal_jdxx_jbxx_view():
    """
    # 流程测试案例查看-节点执行步骤的页面右侧的输出要素，输入要素等信息。
    """
    # 节点测试案例执行步骤ID
    jdcsalzxbzid = request.GET.jdcsalzxbzid
    # 节点测试案例的执行步骤的demoid
    demoid = request.GET.demoid
    # 类型
    lx = request.GET.lx
    # 类型代码
    lxdm = request.GET.lxdm
    # 批次
    pc = request.GET.pc
    # 节点测试案例id 
    jdcsalid = request.GET.jdcsalid
    # 
    hideQw = request.GET.hideQw
    #返回值
    result = {'srys':[], 'scys':[], 'demoid':demoid }
    try:
        result = csal_jdxx_jbxx_service({'zxbzid':jdcsalzxbzid.split(','), 'pc':pc, 'jdcsalid':jdcsalid, 'lx':lx, 'lxdm':lxdm})
        result['srys'] = json.dumps(result['srys'])
        result['scys'] = json.dumps(result['scys'])
    except:
        logger.info(traceback.format_exc())
    result["demoid"] = demoid
    result['lx'] = lx
    result['jdcsalzxbzid'] = jdcsalzxbzid
    result['jdcsalid'] = request.GET.jdcsalid
    result['pc'] = pc
    result['lxdm'] = lxdm
    result['hideQw'] = hideQw
    result['sftg'] = request.GET.sftg
    return render_to_string("kf_ywgl/kf_ywgl_015/kf_ywgl_015_csal_jdxx_jbxx.html",result)

@register_url('POST')
def get_rz_view():
    """
    # 查看日志列表
    """
    csalid = request.POST.csalid
    pc = request.POST.pc
    jdcsalzxbzid = request.POST.jdcsalzxbzid
    mark = request.POST.mark
    #返回值
    result = {'state': False, 'msg': '获取日志失败', 'log': ''}
    try:
       result = get_rz_service(pc,csalid,jdcsalzxbzid,mark)
    except:
        logger.info(traceback.format_exc())
    return result

@register_url('POST')
def get_jdrz_view():
    """
    # 获取单个节点的日志列表
    """
    rzlsh = request.POST.rzlsh
    #返回值
    result = {'state': False, 'msg': '获取日志失败', 'log': ''}
    try:
       result = get_jdrz_service(rzlsh)
    except:
        logger.info(traceback.format_exc())
    return result