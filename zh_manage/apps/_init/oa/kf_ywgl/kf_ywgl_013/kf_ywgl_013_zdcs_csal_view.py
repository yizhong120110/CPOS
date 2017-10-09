# -*- coding: utf-8 -*-
# Action: 自动化测试 测试案例流程列表 view
# Author: 周林基
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import logger, request,render_to_string, render_string
from .kf_ywgl_013_zdcs_csal_service import data_service,csalxx_service,zxjgms_service


@register_url('GET')
def index_view():
    """
    # 自动化测试：自动测试测试案例页面
    """
    data = { 'lx': request.GET.lx, 'csalids':request.GET.csaldyssid, 'jdmc':request.GET.text, 'lxmc':request.GET.lxmc}
    
    return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal.html", data)

@register_url('GET')
def data_view():
    """
    # 自动化测试：datagrid列表的展示
    """
    # 类型
    lx = request.GET.lx
    # 类型名称
    lxmc = request.GET.lxmc
    # 流程名称/测试对象名称
    dxmc = request.GET.dxmc
    # 所属ID
    csaldyssid = request.GET.csaldyssid
    # gl 是否关联测试
    gl = request.GET.gl
    # jddyid 节点定义id
    jddyid = request.GET.jddyid
    # 开始页数
    rn_start = request.rn_start
    # 结束页数
    rn_end = request.rn_end
    try:
        # 组织调用函数字典
        data_dic = { 'lx': lx, 'lxmc': lxmc, 'dxmc': dxmc, 'csaldyssid': csaldyssid, 'rn_start': rn_start, 'rn_end': rn_end, 'gl': gl, 'jddyid': jddyid }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())

    return json.dumps(data)
    
@register_url('GET')
def csalxx_view():
    """
    # 流程测试案例查看-节点信息基本信息的页面
    """
    # 节点测试案例执行步骤ID
    jdcsalid = request.GET.jdcsalid
    # 批次
    pc = request.GET.pc
    # 节点测试案例的执行步骤的demoid
    demoid = request.GET.demoid
    #返回值
    result = {'srys':[], 'scys':[]}
    try:
        result = csalxx_service(jdcsalid,pc)
    except:
        logger.info(traceback.format_exc())
    result['srys'] = json.dumps(result['srys'])
    result['scys'] = json.dumps(result['scys'])
    result['demoid'] = demoid
    result['lx'] = request.GET.lx
    result['jdcsalzxbzid'] = request.GET.jdcsalzxbzid
    result['jdcsalid'] = jdcsalid
    result['pc'] = pc
    result['hideQw'] = ''
    result['lxdm'] = ''
    return render_to_string("kf_ywgl/kf_ywgl_015/kf_ywgl_015_csal_jdxx_jbxx.html",result)
    

@register_url('POST')
def zxjgms_view():
    """
    # 节点测试案例测试结果，结果说明的查询
    """
    # 节点测试案例执行步骤ID
    jdcsalid = request.POST.jdcsalid
    # 批次
    pc = request.POST.pc
    #返回值
    result = {'zxjg':'' ,'jgsm':''}
    try:
        result = zxjgms_service(jdcsalid,pc)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)
    
@register_url('POST')
def getxgcsal_view():
    """
    # 根据节点的测试案例查询出引用该节点的测试案例
    """
    # 节点定义id
    jddyid = request.POST.jddyid
    #返回值
    result = []
    try:
        result = getxgcsal_service(jddyid)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)