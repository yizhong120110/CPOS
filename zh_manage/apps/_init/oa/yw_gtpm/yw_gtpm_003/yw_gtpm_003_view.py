# -*- coding: utf-8 -*-
# Action: 阈值检验流水
# Author: chengdg
# AddTime: 2015-04-25
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from sjzhtspj.common import check_yzjy_single
from .yw_gtpm_003_service import index_service, data_service,index_check_mxck_service , index_mxck_service, data_mxck_service, edit_service, zwjwdkk_service, xgyz_service, cx_service, tg_service


@register_url('GET')
def index_view():
    """
    # 阈值检验流水 主页面
    """
    # 数据结构    
    data = {'ssyw':[], 'jklx':[]}
    try:
        # 调用数据库操作函数
        data = index_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    # 转到交易监控列表页面
    return render_to_string( "yw_gtpm/yw_gtpm_003/yw_gtpm_003.html", data )

@register_url('POST')
def data_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 所属业务
        ssyw = request.POST.ssyw
        # 开始日期
        startJyrq = request.POST.startJyrq.replace('-','')
        # 结束日期
        endJyrq = request.POST.endJyrq.replace('-','')
        # 监控类型
        jklx = request.POST.jklx
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'ssyw': ssyw, 'startJyrq': startJyrq, 'endJyrq': endJyrq, 'jklx': jklx, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def index_check_mxck_view():
    """
    # 查询明细页面跳转前的校验 view
    """
    # 初始化反馈信息
    data = {'state':False, 'msg':''}
    try:
        # 文件ID
        id = request.POST.id
        # 组织数据字典
        sql_data = {'wjid': id }
        # 调用操作数据库函数
        data = index_check_mxck_service( sql_data )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '批量操作失败！异常错误提示信息[%s]' % error_msg
    # 将组织的结果反馈给前台
    return data

@register_url('GET')
def index_mxck_view():
    """
    # 阈值校验流水明细查看 主页面
    # 请求信息：业务类型、三方账号、客户名称、状态
    """
    # 数据结构--文件id
    data = {'wjid':request.GET.id,'wjm': request.GET.wjm,'ywmc': request.GET.ywmc}
    try:
        # 调用数据库操作函数
        sqldata = index_mxck_service(data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    # 转到阈值校验流水明细查看页面
    return render_to_string("yw_gtpm/yw_gtpm_003/yw_gtpm_003_ckmx.html", sqldata)

@register_url('POST')
def data_mxck_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 文件ID
        wjid = request.POST.wjid
        # 业务类型
        ywlx = request.POST.ywlx
        # 三方账号
        sfzh = request.POST.sfzh
        # 客户名称
        khmc = request.POST.khmc
        # 流水状态
        zt = request.POST.zt
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'wjid':wjid, 'ywlx': ywlx, 'sfzh': sfzh, 'khmc': khmc, 'zt': zt, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_mxck_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def edit_view():
    """
    # 批量置为批扣/批量置为失败 view
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 流水明细  mx结构{'id':row.id, 'ywlx':row.ywlx, 'kkje':row.kkje, 'zt':row.zt}
        mx = request.forms.mx
        wjid = request.forms.wjid
        flag = request.forms.flag
        # 组织调用函数字典
        data_dic = { 'wjid':wjid, 'mx': mx, 'flag': flag, 'rn_start': request.rn_start, 'rn_end': request.rn_start }
        data = edit_service( data_dic )
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '批量操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def zwjwdkk_view():
    """
    # 置文件为待扣款 view
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 文件id
        data['id'] = request.forms.ids
        for id in data['id'].split(','):
            re_value, msg = check_yzjy_single(id)
            if re_value=='0':
                data['msg'] = msg
                return data
        data = zwjwdkk_service( data )
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def xgyz_view():
    """
    # 修改阈值 view
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 文件id
        wjid = request.forms.wjid
        data = xgyz_service( {'wjid':wjid} )
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def cx_view():
    """
    # 撤销 view
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 文件id
        data['wjid'] = request.forms.wjid
        re_value, msg = check_yzjy_single( data['wjid'] )
        if re_value=='0':
            data['msg'] = msg
            return data
        data = cx_service( data )
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def tg_view():
    """
    # 通过 view
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 组织查询信息
        # 文件id
        data['wjid'] = request.forms.wjid
        re_value, msg = check_yzjy_single( data['wjid'] )
        if re_value=='0':
            data['msg'] = msg
            return data
        data = tg_service( data )
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data