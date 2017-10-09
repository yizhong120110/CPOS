# -*- coding: utf-8 -*-
# Action: 数据采集配置管理
# Author: zhangzhf
# AddTime: 2015-04-27
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request, render_to_string
from .yw_jkgl_005_service import index_service,data_service,get_cjlx_service,get_sfbf_service,get_cjzb_service,add_cjpz_service,get_cjpz_update_service,edit_service,get_dxmc_zdzj_service,add_sydx_service,del_sydx_service,sydx_service,del_cjpz_service,able_sydx_service,edit_sydx_service

@register_url('GET')
def index_view():
    """
    # 数据采集配置service
    """
    # 数据结构    
    data = {'cjlb':[], 'sfbf':[], 'zt':[], 'cjzb':[], 'lb_zb':{}}
    try:
        # 调用service
        data = index_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    return render_to_string("yw_jkgl/yw_jkgl_005/yw_jkgl_005.html", data)

@register_url('GET')
def data_view():
    """
    # 数据采集配置列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end }
        # 采集类别
        sql_data['cjlb'] = request.GET.cjlb
        # 采集指标
        sql_data['cjzb'] = request.GET.cjzb
        # 采集名称
        sql_data['cjmc'] = request.GET.cjmc
        # 是否可并发
        sql_data['sfbf'] = request.GET.sfbf
        # 状态
        sql_data['lx'] = request.GET.lx
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data
    
@register_url('POST')
def get_cjlx_view():
    """
    # 获取采集对象类型
    """
    # 初始化返回值
    data = []
    try:
        data = get_cjlx_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def add_view():
    """
    # 新增采集配置
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','other':{}}
    try:
        # 名称
        cjmc = request.forms.cjmc
        # 描述
        cjms = request.forms.cjms
        # 类别
        cjlb = request.forms.cjlb
        # 指标
        cjzb = request.forms.cjzb
        # 类型
        sjcj_cjlx = request.forms.sjcj_cjlx
        # 发起频率
        fqpl = request.forms.fqpl
        # 自动发起配置
        zdfqjyzdfqpz = request.forms.zdfqjyzdfqpz
        # 是否可并发
        sfbf = request.forms.sfbf
        # 自动发起配置说明
        zdfqjyzdfqpzsm = request.forms.zdfqjyzdfqpzsm
        # 状态
        # state = request.forms.state
        sql_data = {'cjmc':cjmc,'cjms':cjms,'cjlb':cjlb,'cjzb':cjzb,'sjcj_cjlx':sjcj_cjlx,'fqpl':fqpl,'zdfqjyzdfqpz':zdfqjyzdfqpz,'sfbf':sfbf,'zdfqjyzdfqpzsm':zdfqjyzdfqpzsm}
        data = add_cjpz_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '新增失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data

@register_url('POST')
def edit_view():
    """
    # 更新采集配置
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','other':{}}
    try:
        # id
        id = request.forms.cjid
        # 名称
        cjmc = request.forms.cjmc
        # 描述
        cjms = request.forms.cjms
        # 类别
        cjlb = request.forms.cjlb_hid
        # 指标
        cjzb = request.forms.cjzb_hid
        # 类型
        sjcj_cjlx = request.forms.sjcj_cjlx
        # 发起频率
        fqpl = request.forms.fqpl
        # 自动发起配置
        zdfqjyzdfqpz = request.forms.zdfqjyzdfqpz
        # 是否可并发
        sfbf = request.forms.sfbf
        # 自动发起配置说明
        zdfqjyzdfqpzsm = request.forms.zdfqjyzdfqpzsm
        # 状态
        state = request.forms.sjcj_state
        sql_data = {'id':id,'cjmc':cjmc,'cjms':cjms,'cjlb':cjlb,'cjzb':cjzb,'sjcj_cjlx':sjcj_cjlx,'fqpl':fqpl,'zdfqjyzdfqpz':zdfqjyzdfqpz,'sfbf':sfbf,'zdfqjyzdfqpzsm':zdfqjyzdfqpzsm,'state':state}
        data = edit_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return data

@register_url('POST')
def get_cjpz_update_view():
    """
    # 查询采集配置对象，编辑使用
    """
    # 初始化返回值
    data = {'state':False, 'msg':'','cjpz':{}}
    # 采集配置id
    id = request.forms.id
    try:
        data = get_cjpz_update_service({'id':id})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取采集配置信息失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def get_sfbf_view():
    """
    # 获取是否并发
    """
    # 初始化返回值
    data = []
    try:
        data = get_sfbf_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    # 将结果反馈给前台
    return json.dumps(data)

@register_url('GET')
def get_cjzb_view():
    """
    # 获取采集指标
    """
    # 初始化返回值
    data = []
    # 采集类别
    cjlb = request.GET.cjlb
    try:
        data = get_cjzb_service({'cjlb':cjlb})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def get_dxmc_zdzj_view():
    """
    # 对象名称下拉框,指定主机下拉列表内容
    """
    # 初始化返回值
    data = {'state':False,'msg':'','dxmc':[], 'zdzj':[], 'crcs':[]}
    # 指标ID
    zbid = request.forms.zbid
    # 所属类别ID
    sslbbm = request.forms.sslbbm
    # 采集配置ID
    cjpzid = request.forms.cjpzid
    # 适用对象id
    sydxid = request.forms.sydxid
    # type，标识新增还是编辑
    type = request.forms.type
    try:
        data = get_dxmc_zdzj_service({'zbid':zbid,'sslbbm':sslbbm,'cjpzid':cjpzid,'sydxid':sydxid,'type':type})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取信息失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def add_sydx_view():
    """
    # 适用对象添加
    """
    # 初始化返回值
    data = {'state':False,'msg':''}
    # 采集配置ID
    cjpzid = request.forms.cjid_hid
    # 对象ID
    cjdxid = request.forms.dxmc
    # 指定主机IP
    zdzjip = request.forms.zdzj
    # 传入参数
    crcs = request.forms.crcs
    # 状态
    state = request.forms.state
    try:
        data = add_sydx_service({'cjpzid':cjpzid,'cjdxid':cjdxid,'zdzjip':zdzjip,'crcs':crcs,'state':state})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '新增失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)

@register_url('POST')
def edit_sydx_view():
    """
    # 适用对象编辑
    """
    # 初始化返回值
    data = {'state':False,'msg':''}
    # 采集配置ID
    cjpzid = request.forms.cjid_hid
    # 对象ID
    cjdxid = request.forms.hid_dxmc
    # 指定主机IP
    zdzjip = request.forms.hid_zdzjip
    # 指标id
    zbid = request.forms.hidCjzb_hid
    # 传入参数
    crcs = request.forms.crcs
    # 适用对象id
    sydxid = request.forms.sydxid
    try:
        data = edit_sydx_service({'cjpzid':cjpzid,'zbid':zbid,'crcs':crcs,'sydxid':sydxid,'cjdxid':cjdxid,'zdzjip':zdzjip})
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '编辑失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def del_sydx_view():
    """
    # 删除适用对象
    """
    # 初始化返回值
    data = {'state':False,'msg':''}
    # 适用对象ID
    ids = request.forms.ids
    # 采集配置id
    cjpzid = request.forms.cjpzid
    # 采集配置名称
    cjpzmc = request.forms.cjpzmc
    try:
        data = del_sydx_service(ids,cjpzid,cjpzmc)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def sydx_view():
    """
    # 获取适用对象
    """
    # 翻页开始下标
    rn_start = request.rn_start
    # 翻页结束下标
    rn_end = request.rn_end
    # 请求字典
    sql_data = { 'rn_start': rn_start, 'rn_end': rn_end }
    # 初始化返回值
    data = {'total':0,'rows':[]}
    # 采集配置id
    cjpzid = request.forms.cjpzid
    sql_data['cjpzid'] = cjpzid
    sql_data['zbid'] = request.forms.zbid 
    try:
        data = sydx_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def del_cjpz_view():
    """
    # 删除采集配置对象
    """
    # 初始化返回值
    data = {'state':False,'msg':''}
    # 采集配置对象ID
    ids = request.forms.ids
    try:
        data = del_cjpz_service(ids)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除失败！异常错误提示信息\n[%s]' % error_msg
    # 将结果反馈给前台
    return json.dumps(data)
    
@register_url('POST')
def able_sydx_view():
    """
    # 启用，禁用采集配置
    """
    # 初始化返回值
    data = {'state':False,'msg':''}
    # 适用对象ID
    ids = request.forms.ids
    # 状态
    zt = request.forms.zt
    xx = '启用' if zt == '1' else '禁用'
    try:
        data = able_sydx_service(ids,zt)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        error_d = {'xx':xx, 'error_msg': error_msg}
        data['msg'] = '%(xx)s失败！异常错误提示信息\n[%(error_msg)s]' % error_d
    # 将结果反馈给前台
    return json.dumps(data)