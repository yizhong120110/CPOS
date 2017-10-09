# -*- coding: utf-8 -*-
# Action: 自动化测试
# Author: liuhh
# AddTime: 2015-2-15
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_014_service import get_zdcslb_service, cs_start_service, cs_stop_service, cs_close_service, get_cs_zxjg_service,del_test_data_service

@register_url('GET')
def index_view():
    """
    # 测试案例列表页面
    """
    # 自动测试案例的IDs,以逗号分割的字符串
    csalids = request.GET.csalids
    # 测试案例信息，包含所属业务id和类型
    csal = request.GET.csal
    return render_to_string("kf_ywgl/kf_ywgl_014/kf_ywgl_014.html",{"csalids":csalids, "csal":csal})

@register_url('POST')
def get_zdcslb_view():
    """
    # 自动测试案例列表
    """
    # 自动测试案例的IDs,以逗号分割的字符串
    csalids = request.POST.csalids
    # 测试案例信息，业务所属id和类型等信息。
    csal = request.POST.csal

    # 返回对象
    result = {}
    try:
       result = get_zdcslb_service(csalids, csal)
    except:
        logger.info(traceback.format_exc())
    return  result
    
@register_url('POST')
def cs_start_view():
    """
    # 点击开始测试按钮的响应的view
    """
    # 前台自动化测试的数据
    data = request.POST.row_data
    pc = request.POST.pc
    # 返回对象
    result = {'state':False, 'msg':''}
    try:
       result = cs_start_service(data,pc)
    except:
        # 删除测试数据
        del_test_data_service(data)
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '测试失败！异常错误提示信息[%s]' % error_msg
    return  result

@register_url('POST')
def cs_stop_view():
    """
    # 点击停止测试按钮的响应的view
    """
    # 停止测试的测试案例的IDs
    pc = request.POST.pc

    # 返回对象
    result = {'rows':[]}
    try:
       result['rows'] = cs_stop_service(pc)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)

@register_url('POST')
def cs_close_view():
    """
    # 点击关闭按钮时的响应的view
    """
    # 关闭窗体的时候,删除的临时表中的信息的批次ids
    pc = request.POST.pc

    # 返回对象
    result = {'rows':[]}
    try:
       result['rows'] = cs_close_service(pc)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)

@register_url('POST')
def get_cs_zxjg_view():
    """
    # 开启测试之后,每五秒进行获取测试执行的结果
    """
    # 开启测试之后,获取执行测试结果的批次ids
    pc = request.POST.pc
    # 测试案例的id
    csalids = request.POST.csalids
    # 返回对象
    result = {'rows':[]}
    try:
       result['rows'] = get_cs_zxjg_service(pc,csalids)
    except:
        logger.info(traceback.format_exc())
    return json.dumps(result)
