# -*- coding: utf-8 -*-
# Action: 当日执行计划列表
# Author: fangch
# AddTime: 2015-04-14
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request, render_to_string,get_sess
from sjzhtspj.common import get_strftime,get_hy_byjsdm_sq
from sjzhtspj.const import FHR_JSDM
from .yw_jhrw_003_service import data_service,data_ymxx_service,data_dzzxjhlb_service,data_sgzxjhlb_service,check_service,sgzxcl_service,demo_log_service

@register_url('GET')
def index_view():
    """
    # 当日执行计划列表页面
    """
    # 初始化反馈前台信息
    data = { 'zt_lst': [], 'rwlx_lst': [], 'rq':'' }
    try:
        # 获取下拉列表信息
        data = data_ymxx_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到当日执行计划列表页面
    return render_to_string("yw_jhrw/yw_jhrw_003/yw_jhrw_003.html",data)

@register_url('POST')
def data_view():
    """
    # 监控规则发起列表信息json数据
    """
    data = {'total':0, 'rows':[]}
    # 发起日期
    rq = request.POST.rq.replace('-','')
    # 数据查询条件
    params = { 'rn_start': request.rn_start, 'rn_end': request.rn_end, 'rq':rq, 'mc':request.POST.mc, 'rwlx':request.POST.rwlx, 'zt':request.POST.zt, 'lsh':request.POST.lsh}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('POST')
def xydzlb_view():
    """
    # 响应动作列表展示
    """
    # 获取配置名称前台页面使用
    pzmc = request.POST.pzmc
    data = { 'pzmc':pzmc }
    return data
    
@register_url('GET')
def xydzlb_sel_view():
    """
    # 响应动作列表json数据
    """
    # 获取配置ID查询使用
    pzid = request.GET.pzid
    params = { 'pzid':pzid }
    # 定义反馈信息
    data = {'total':0, 'rows':[] }
    try:
        data = data_xydzlb_service(params)
    except:
        logger.info(traceback.format_exc())
    print (data)
    return data
    
@register_url('POST')
def sgzx():
    """
    # 手工执行处理
    """
    # 初始化反馈前台信息
    drzxjhid = request.forms.drzxjhid
    fhr = request.forms.fhr
    data = { 'drzxjhid': drzxjhid, 'fhr':fhr, 'msg': '', 'state': False }
    try:
        # 手工执行处理
        data = sgzxcl_service(data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        msg_log = traceback.format_exc()
        logger.info( msg_log )
        data['msg'] = '手工执行失败，异常信息：%s' % msg_log
        
    return data
    
@register_url('GET')
def ty_sq():
    """
    通用授权 
    """
    # 获取当前登录行员的机构编码
    jgbm = get_sess('jgbm')
    param = {'jsdm':FHR_JSDM,'bm':jgbm}
    hyxx_lst = get_hy_byjsdm_sq( param )
    data = { 'url': request.GET.url,'hyxx_lst':hyxx_lst, 'dgid': request.GET.dgid if request.GET.dgid else '' }
    return render_to_string("yw_jhrw/yw_jhrw_003/ty_sq.html",data)

@register_url('POST')
def sq_check():
    """
    授权校验 
    """
    # 反馈信息
    result = {'state': False, 'msg':''}
    try:
        # 复核人
        fhr = request.forms.fhr
        # 复核人密码
        fhrmm = request.forms.fhrmm
        # 组织调用函数字典
        data_dic = { 'fhr': fhr, 'fhrmm': fhrmm }
        # 调用操作数据库函数
        result = check_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '授权校验失败！异常错误提示信息[%s]' % error_msg
    return result
    
@register_url('POST')
def dzzxjhlb_sel_view():
    """
    # 响应动作列表json数据
    """
    # 获取配置ID查询使用
    lsh = request.POST.lsh
    params = { 'lsh':lsh, 'rn_start': request.rn_start, 'rn_end': request.rn_end }
    # 定义反馈信息
    data = {'total':0, 'rows':[] }
    try:
        data = data_dzzxjhlb_service(params)
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('POST')
def sgzxjh_sel_view():
    """
    # 手工执行计划列表json数据
    """
    # 查询使用条件
    params = { 'lsh':request.POST.lsh,'rwlx':request.POST.rwlx, 'rn_start': request.rn_start, 'rn_end': request.rn_end }
    # 定义反馈信息
    data = {'total':0, 'rows':[] }
    try:
        data = data_sgzxjhlb_service(params)
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def demo_log_view():
    """
    # 获取日志
    """
    # Log流水号
    log_lsh = request.POST.log_lsh
    rq = request.POST.rq
    result = {'state': False, 'msg': '', 'log': ''}
    try:
        result = demo_log_service([rq,log_lsh])
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '获取Log失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)