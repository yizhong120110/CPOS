# -*- coding: utf-8 -*-
# Action: 运维参数管理-交易参数
# Author: zhangchl
# AddTime: 2015-04-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_csgl_003_service import data_service, jbxx_edit_service


@register_url('GET')
def jycsgl_indx_view():
    """
    # 交易参数管理主页面
    """
    # 无需操作，直接到页面
    return render_to_string("yw_csgl/yw_csgl_003/yw_csgl_003.html")

@register_url('GET')
def data_view():
    """
    # 交易参数交易列表json数据
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 查询字段名称
        search_name = request.GET.search_name
        # 查询内容
        search_value = request.GET.search_value
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end }
        if search_value:
            sql_data.update( { 'search_name': [search_name], 'search_value': search_value } )
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def jbxx_edit_view():
    """
    # 交易基本信息编辑
    """
    # 交易ID
    id = request.forms.id
    # 交易码
    jym = request.forms.jym
    # 修改前信息
    updQ = request.forms.updQ
    # 交易状态 '0'禁用 '1'启用
    zt = request.forms.zt
    # 交易超时时间
    timeout = request.forms.timeout
    # 交易自动发起配置
    zdfqpz = request.forms.zdfqpz
    # 原交易状态 '0'禁用 '1'启用
    yzt = request.forms.yzt
    # 原交易自动发起配置
    yzdfqpz = request.forms.yzdfqpz
    # 组织请求信息
    sql_data = { 'id': id, 'jym': jym, 'updQ': updQ, 'zt': zt, 'timeout': timeout, 'zdfqpz': zdfqpz, 'zdfqpzsm': '',
            'yzt': yzt, 'yzdfqpz': yzdfqpz }
    # 初始化反馈值
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库处理函数
        result = jbxx_edit_service(sql_data)
    except:
        # 操作数据库出现异常，将异常写入日志，并将异常抛给前台进行显示
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    # 将最终结果反馈给前台
    return result
