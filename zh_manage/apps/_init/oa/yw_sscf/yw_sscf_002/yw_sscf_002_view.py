# -*- coding: utf-8 -*-
# Action: 主机详细信息监控
# Author: zhangzhf
# AddTime: 2015-05-16
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request, render_to_string
from .yw_sscf_002_service import index_service,zjxx_service,kr_jc_service,set_refresh_service,get_yjxx_service,get_xydzxx_service, update_clgc_service,able_jk_service,jkpzgl_service,update_jkpzgl_service,jkjcpz_service,get_jclxzt_service,add_jcpz_service,get_jcpz_edit_service,edit_jcpz_service,del_jcpz_service,update_yj_yc_service

@register_url('GET')
def index_view():
    """
    # 主机详细信息页面加载view
    """
    # 数据结构    
    data = {'yj':0,'yc':0,'sxpl':0,'zjmc':'','zt':'0', 'zjip':''}
    ip = request.GET.ip
    try:
        # 调用service
        data = index_service({'ip': ip})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    data['zjip'] = ip
    return render_to_string("yw_sscf/yw_sscf_002/yw_sscf_002.html", data)
    
@register_url('POST')
def zjxx_view():
    """
    # 主机各个指标信息的view
    """
    # ip
    ip = request.forms.ip
    # 放大缩小的标识
    mark = request.forms.mark
    # 数据结构    
    data = {'cpu':{'key_c':['用户使用','系统使用','IO等待'], 'keys':['us','sy','wa'], 'values':{'us':[], 'sy':[], 'wa':[]}, 'time':[], 'time_l':[], 'length':1}, 
            'zjjc':{'jcxx':[], 'length':1},
            'wj':{ 'xx':{}, 'time':[], 'keys':[], 'length':1, 'time_l':[] },
            'io':{ 'keys':[], 'values':{}, 'time':[], 'length':1, 'time_l':[] },
            'wlnc':{ 'xx':[], 'time':[], 'length':1, 'time_l':[]} }
    try:
        sql_data = {'ip':ip,'mark':mark}
        # 调用service
        data = zjxx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取主机信息失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def kr_jc_view():
    """
    # 重启进程view
    """
    data = {'state':False, 'msg':''}
    # ip
    ip = request.POST.ip
    # 进程名称
    jcmc = request.POST.jcmc
    try:
        sql_data = {'ip':ip,'jcmc':jcmc}
        # 调用service
        data = kr_jc_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '重启进程失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def set_refresh_view():
    """
    # 刷新频率配置view
    """
    data = {'state':False, 'msg':'', 'sxpl':0}
    # 刷新频率
    sxpl = request.forms.sxpl
    # ip
    ip = request.forms.ip
    try:
        sql_data = {'sxpl':sxpl, 'ip':ip}
        # 调用service
        data = set_refresh_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '刷新频率配置失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def get_yjxx_view():
    """
    # 获取预警信息view
    """
    data = {'rows':[], 'total':0}
    # 预警类别
    yjjb = request.forms.yjjb
    # ip
    ip = request.forms.ip
    rn_start = request.rn_start
    rn_end = request.rn_end
    
    try:
        sql_data = {'yjjb':yjjb, 'ip':ip, 'rn_start':rn_start, 'rn_end':rn_end}
        # 调用service
        data = get_yjxx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取预警信息失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def get_xydzxx_view():
    """
    # 获取响应动作列表view
    """
    data = {'rows':[], 'total':0}
    # 监控分析配置id
    jkfxpzid = request.forms.jkfxpzid
    # lsh
    lsh = request.forms.lsh
    rn_start = request.rn_start
    rn_end = request.rn_end
    
    try:
        sql_data = {'jkfxpzid':jkfxpzid, 'lsh':lsh, 'rn_start':rn_start, 'rn_end':rn_end}
        # 调用service
        data = get_xydzxx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取响应动作列表失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def update_clgc_view():
    """
    # 处理过程view
    """
    data = {'state':False, 'msg':''}
    # 执行计划id
    zxjhid = request.forms.zxjhid
    # 处理过程
    clgc = request.forms.clgc
    # 函数名称
    hsmc = request.forms.hsmc
    # 中文名称
    zwmc = request.forms.zwmc
    # 规则描述
    gzms = request.forms.gzms
    # 流水号
    lsh = request.forms.lsh
    try:
        sql_data = {'zxjhid':zxjhid, 'clgc':clgc, 'hsmc':hsmc,'zwmc':zwmc,'gzms':gzms,'lsh':lsh}
        # 调用service
        data = update_clgc_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '添加处理过程失败！异常错误提示信息\n[%s]' % error_msg
    return data

@register_url('POST')
def able_jk_view():
    """
    # 禁用启用监控view
    """
    # 主机Ip
    ip = request.forms.ip
    # 启用禁用的状态
    zt = request.forms.zt
    # 主机名称
    zjmc = request.forms.zjmc
    z_zt = '启用' if zt == '1' else '禁用'
    f_zt = '0' if zt == '1' else '1'
    data = {'state':False, 'msg':'', 'zt':zt}
    try:
        sql_data = {'ip':ip,'zt':zt, 'z_zt':z_zt,'zjmc':zjmc,'f_zt':f_zt}
        # 调用service
        data = able_jk_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '监控'+z_zt+'失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def jkpzgl_view():
    """
    # 监控配置管理view
    """
    data = []
    # ip
    ip = request.forms.ip
    try:
        # 调用service
        data = jkpzgl_service(ip)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取监控配置失败！异常错误提示信息\n[%s]' % error_msg
    return json.dumps(data)
    
@register_url('POST')
def update_jkpzgl_view():
    """
    # 更新配置管理view
    """
    data = {'state':False, 'msg':''}
    # ip
    ip = request.forms.ip
    # 配置信息
    xx = request.forms.xx
    # oldxx, 修改之前的配置信息
    oldxx = request.forms.oldxx
    try:
        # 调用service
        data = update_jkpzgl_service(ip,xx, oldxx)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '更新监控配置失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def jkjcpz_view():
    """
    # 监控进程配置管理view
    """
    data = {'rows':[], 'total':0}
    # ip
    ip = request.forms.ip
    # 进程名称
    jcmc = request.forms.jcmc
    # 状态
    jczt = request.forms.jczt
    rn_start = request.rn_start
    rn_end = request.rn_end
    try:
        # 调用service
        data = jkjcpz_service({'ip':ip, 'jcmc':jcmc, 'jczt':jczt, 'rn_start':rn_start, 'rn_end':rn_end})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    return data
    
@register_url('POST')
def get_jclxzt_view():
    """
    # 获取进程类型和进程状态
    """
    data = {'jclx':[], 'jczt':[], 'jclx_w':[], 'txwjmc':[], 'zjmc':''}
    # ip
    ip = request.forms.ip
    try:
        # 调用service
        data = get_jclxzt_service({'ip':ip})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    return data
    
@register_url('POST')
def add_jcpz_view():
    """
    # 进程配置添加view
    """
    data = {'state':False, 'msg':''}
    # ip
    ip = request.forms.hostname
    # zjmc
    zjmc = request.forms.zjmc
    # 进程名称
    jcmc = request.forms.jcmc
    # 进程数量
    jcsl = request.forms.jcsl
    # 启动命令
    qdml = request.forms.qdml
    # 启动类型
    qdlx = request.forms.qdlx
    # 查看命令
    ckml = request.forms.ckml
    # 状态
    state = request.forms.state
    sql_data = {'ip':ip,'zjmc':zjmc,'jcmc':jcmc,'jcsl':jcsl,'ckml':ckml,'txwjmc':qdlx,'qdml':qdml,'state':state}
    try:
        # 调用service
        data = add_jcpz_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '添加进程配置失败！异常错误提示信息\n[%s]' % error_msg
    return data

@register_url('POST')
def get_jcpz_edit_view():
    """
    # 获取要编辑的进程信息
    """
    data = {'state':False, 'msg':''}
    # id
    id = request.forms.id
    # ip
    ip = request.forms.ip
    try:
        # 调用service
        data = get_jcpz_edit_service({'id':id, 'ip':ip})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑进程配置失败！异常错误提示信息\n[%s]' % error_msg
    return json.dumps(data)

@register_url('POST')
def edit_jcpz_view():
    """
    # 进程配置编辑view
    """
    data = {'state':False, 'msg':''}
    # ip 
    ip = request.forms.hostname
    # id
    id = request.forms.hidId
    # zjmc
    zjmc = request.forms.zjmc
    # 进程名称
    jcmc = request.forms.jcmc
    # 进程数量
    jcsl = request.forms.jcsl
    # 查看命令
    ckml = request.forms.ckml
    # 启动命令
    qdml = request.forms.qdml
    # 启动类型
    qdlx = request.forms.qdlx
    # 状态
    state = request.forms.state
    # 旧数据
    oldData = request.forms.oldData
    sql_data = {'id':id,'ip':ip,'zjmc':zjmc,'jcmc':jcmc,'jcsl':jcsl,'qdml':qdml,'txwjmc':qdlx,'ckml':ckml,'state':state,'oldData':oldData}
    try:
        # 调用service
        data = edit_jcpz_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑进程配置失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def del_jcpz_view():
    """
    # 删除进程信息
    """
    data = {'state':False, 'msg':''}
    # rows, 要删除的进程的信息
    rows = request.forms.rows
    # ip
    ip = request.forms.ip
    # 主机名称
    zjmc = request.forms.zjmc
    try:
        # 调用service
        data = del_jcpz_service(rows,ip,zjmc)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除进程配置失败！异常错误提示信息\n[%s]' % error_msg
    return json.dumps(data)
    
@register_url('POST')
def update_yj_yc_view():
    """
    # 更新页面的预警和异常数量
    """
    data = {'yj':0,'yc':0}
    try:
        # 调用service
        data = update_yj_yc_service({'ip':request.forms.ip})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
    return json.dumps(data)
    