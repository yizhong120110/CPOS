# -*- coding: utf-8 -*-
# Action: 计划任务管理-自动发起交易列表
# Author: zhangchl
# AddTime: 2015-04-09
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行


import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_jhrw_001_service import zdfqjylb_service, zdfqjylb_data_service, zdfqjylb_edit_sel_service, zdfqjylb_edit_service


@register_url('GET')
def index_view():
    """
    # 计划任务管理 主页面
    """
    # 平台
    pt = request.GET.pt
    # 组织返回值
    data = { 'pt': pt if pt else '' }
    return render_to_string( "yw_jhrw/yw_jhrw_001/yw_jhrw_001.html",data )

@register_url('GET')
def zdfqjylb_view():
    """
    # # 初始化自动发起交易列表页面数据准备 view 主页面
    """
    # 初始化反馈前台信息
    data = { 'zt_lst': [] }
    try:
        # 平台
        pt = request.GET.pt
        # 组织请求信息字典
        sql_data = { 'pt': pt }
        # 调用数据库操作函数
        data = zdfqjylb_service( sql_data )
        # 将对应平台反馈给前台
        data['pt'] = pt
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到自动发起交易列表页面
    return render_to_string("yw_jhrw/yw_jhrw_001/yw_jhrw_001_zdfqjylb.html",data)

@register_url('POST')
def zdfqjylb_data_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 平台
        pt = request.POST.pt
        # 业务名称
        ywmc = request.POST.ywmc
        # 交易码
        jym = request.POST.jym
        # 交易名称
        jymc = request.POST.jymc
        # 交易状态
        jyzt = request.POST.jyzt
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'pt': pt, 'ywmc': ywmc, 'jym': jym, 'jymc': jymc, 'jyzt': jyzt, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = zdfqjylb_data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def zdfqjylb_edit_sel_view():
    """
    # 编辑页面初始化组织数据 view
    """
    # 交易id
    jyid = request.POST.jyid
    
    # 初始化反馈信息
    # 交易基本信息初始化为空字典
    result = { 'state':False, 'msg':'','jyjbxx_dic': {} }
    try:
        # 调用数据库操作函数
        result = zdfqjylb_edit_sel_service( { 'jyid': jyid } )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def zdfqjylb_edit_view():
    """
    # 编辑提交 view
    """
    # 平台
    pt = request.forms.pt
    # 交易ID
    id = request.forms.jyid
    # 业务名称
    ywmc = request.forms.ywmc
    # 交易码
    jym = request.forms.jym
    # 交易名称
    jymc = request.forms.jymc
    # 交易自动发起配置
    zdfqpz = request.forms.zdfqjyZdfqpz
    # 交易状态 '0'禁用 '1'启用
    zt = request.forms.jyzt
    # 修改前内容
    ynr = request.forms.ynr
    # 原交易状态 '0'禁用 '1'启用
    yzt = request.forms.yzt
    # 原交易自动发起配置
    yzdfqpz = request.forms.yzdfqpz
    # 请求信息
    sql_data = { 'pt': pt, 'id': id,'ywmc': ywmc,'jym': jym,'jymc': jymc,'zdfqpz': zdfqpz, 'zdfqpzsm': '', 'zt': zt, 'ynr': ynr,
            'yzt': yzt, 'yzdfqpz': yzdfqpz }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = zdfqjylb_edit_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result