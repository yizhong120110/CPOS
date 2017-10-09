# -*- coding: utf-8 -*-
# Action: 交易流程编辑
# Author: gaorj
# AddTime: 2015-01-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import request, render_to_string, logger
from sjzhtspj.common import lc_data_service, jd_del_service
from .kf_ywgl_005_service import (
    index_service, repository_data_service, node_edit_service, node_edit_submit_service, node_ys_service, node_ys_edit_service, 
    node_ys_add_service, node_ys_del_service, node_fhz_update_service, node_yycs_service, lc_save_service, get_wym_service, dbts_ys_data_service, 
    dbts_bz_data_service, get_ywsjb_service, demo_jbxx_data_service, demo_jbxx_data_add_service, demo_sj_data_service, demo_sj_data_add_service, 
    demo_sj_data_edit_service, demo_sj_data_del_service, demo_jbxx_data_del_service, djbjd_data_service, set_djbjd_service, 
    demo_execute_service, demo_log_service, demo_save_step_service, demo_del_step_service, dbtsjl_service, del_dbts_service, save_jdcsal_service, 
    save_csal_service, get_node_fhz_service,demo_sj_data_pladd_service, get_czpz_service, czpz_sub_service
)


@register_url('GET')
def index_view():
    """
    # 交易流程编辑url
    """
    # 类型（lc流程，zlc子流程）
    lx = request.GET.lx
    # 交易ID/子流程ID
    id = request.GET.id
    # 交易名称/子流程名称
    mc = request.GET.mc
    params = {'lx': lx, 'id': id, 'mc': mc}
    
    data = {'lx': lx, 'id': id, 'mc': mc, 'yw_data': [], 'txzlc_data': [], 'ptzlc_data': [], 'jd_data': [], 'wym': '', 'wym_bbk': '', 'ywid': '', 'lcbm': '', 'ywsjb': []}
    try:
        data = index_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_005/kf_ywgl_005.html", data)

@register_url('GET')
def repository_data_view():
    """
    # 获取节点库数据
    """
    # 类型
    type = request.GET.type
    # 业务ID
    ywid = request.GET.ywid
    
    data = []
    try:
        data = repository_data_service(type, ywid)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('GET')
def data_view():
    """
    # 交易流程编辑获取数据
    """
    # 交易ID
    id = request.GET.jyid
    
    data = [{}, []]
    try:
        data = lc_data_service(id, 'lc')
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('GET')
def node_edit_view():
    """
    # 节点编辑url
    """
    # 节点ID
    nodeid = request.GET.nodeid
    # 流程布局ID
    bjid = request.GET.bjid
    # 节点类型
    jdlx = request.GET.jdlx
    params = {'nodeid': nodeid, 'bjid': bjid, 'jdlx': jdlx}
    
    data = {'nodeid': nodeid, 'bjid': bjid, 'jdlx': jdlx, 'jdmc': '', 'bm': '', 'nr': '', 'jdys_lb': {}, 'jdys_ly': {}}
    try:
        data = node_edit_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_005/kf_ywgl_005_node_edit.html", data)

@register_url('POST')
def node_edit_submit_view():
    """
    # 节点编辑url
    """
    # 节点ID
    nodeid = request.POST.nodeid
    # 节点类型
    jdlx = request.POST.jdlx or '1'
    # 节点编码
    jdbm = request.POST.jdbm
    # 节点名称
    jdmc = request.POST.jdmc
    # 节点逻辑代码
    jdnr = request.POST.jdnr
    params = {'nodeid': nodeid, 'jdlx': jdlx, 'jdbm': jdbm, 'jdmc': jdmc, 'jdnr': jdnr}
    
    result = {'state':False, 'msg':'', 'nodeid': ''}
    try:
        result = node_edit_submit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def jd_del_view():
    """
    # 节点删除
    """
    # 节点ID，逗号分隔
    jdids = ','.join(json.loads(request.POST.jdids))
    # 交易ID/子流程ID
    lcid = request.POST.lcid
    result = {'state':False, 'msg':''}
    
    if not jdids:
        return result
    try:
        result = jd_del_service(jdids, lcid)
    except:
        logger.info(traceback.format_exc())
    return result

@register_url('GET')
def node_ys_view():
    """
    # 节点要素获取
    """
    # 节点ID
    nodeid = request.GET.nodeid
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = request.GET.lb
    params = {'nodeid': nodeid, 'lb': lb}
    
    data = {'total': 0, 'rows': []}
    try:
        data = node_ys_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def node_ys_edit_view():
    """
    # 节点要素编辑
    """
    # 节点ID
    nodeid = request.POST.nodeid
    # 节点要素ID
    id = request.POST.ysid
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = request.POST.lb
    # 要素编码
    bm = request.POST.ysbm
    # 要素名称
    ysmc = request.POST.ysmc
    # 默认值
    mrz = request.POST.ysmrz
    # 归属类别（'1': '节点使用', '2': '系统默认', '3': '系统参数表', '4': '业务参数表', '5': '交易参数表'）
    gslb = request.POST.gslb
    params = {'nodeid': nodeid, 'id': id, 'lb': lb, 'bm': bm, 'ysmc': ysmc, 'mrz': mrz, 'gslb': gslb}
    
    result = {'state': False, 'msg': '编辑失败'}
    try:
        result = node_ys_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def node_ys_add_view():
    """
    # 节点要素新增
    """
    # 节点ID
    nodeid = request.POST.nodeid
    # 流程布局ID
    bjid = request.POST.bjid
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = request.POST.lb
    # 要素编码
    bm = request.POST.ysbm
    # 要素名称
    ysmc = request.POST.ysmc
    # 归属类别（'1': '节点使用', '2': '系统默认', '3': '系统参数表', '4': '业务参数表', '5': '交易参数表'）
    gslb = request.POST.gslb
    # 默认值
    mrz = request.POST.ysmrz
    params = {'nodeid': nodeid, 'bjid': bjid, 'lb': lb, 'bm': bm, 'ysmc': ysmc, 'gslb': gslb, 'mrz': mrz}
    
    result = {'state': False, 'msg': '新增失败！', 'nodeid': ''}
    try:
        result = node_ys_add_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def node_ys_del_view():
    """
    # 节点要素删除
    """
    ids = request.POST.ids
    params = {'ids': ids}
    
    result = {'state':False, 'msg':'删除失败！'}
    
    try:
        result = node_ys_del_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def node_fhz_update_view():
    """
    # 编辑节点返回值备注
    """
    # 返回值ID
    fhzid = request.POST.fhzid
    # 返回值备注
    bz = request.POST.bz
    
    result = {'state': False, 'msg': ''}
    try:
        result = node_fhz_update_service(fhzid, bz)
    except:
        logger.info(traceback.format_exc())
    
    return result

@register_url('GET')
def node_yycs_view():
    """
    # 节点引用次数
    """
    # 节点ID
    nodeid = request.GET.nodeid
    params = {'nodeid': nodeid}
    
    data = {'total': 0, 'rows': []}
    try:
        data = node_yycs_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def lc_save_view():
    """
    # 流程保存
    """
    lx = request.POST.lx
    id = request.POST.id
    # 交易码/子流程编码
    lcbm = request.POST.lcbm
    nodes = json.loads(request.POST.nodes)
    conns = json.loads(request.POST.conns)
    params = {'lx': lx, 'id': id, 'lcbm': lcbm, 'nodes': nodes, 'conns': conns}
    
    result = {'state': False, 'msg': '', 'wym': '', 'wym_bbk': ''}
    try:
        result = lc_save_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def get_wym_view():
    """
    # 获取唯一码
    """
    lx = request.GET.lx
    id = request.GET.id
    
    result = {'state': False, 'msg': '', 'wym': '', 'wym_bbk': ''}
    try:
        result = get_wym_service(lx, id)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取唯一码失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def zlc_index_view():
    """
    # 子流程查看url
    """
    # 子流程ID
    zlcid = request.GET.zlcid
    
    return render_to_string("kf_ywgl/kf_ywgl_005/kf_ywgl_005_zlc.html", {'zlcid': zlcid})

@register_url('GET')
def dbts_index_view():
    """
    # 单步调试url
    """
    # 节点ID
    nodeid = request.GET.nodeid
    # 节点类型（'strat':开始节点，'end':结束节点，'jd':节点，'zlc':子流程）
    type = request.GET.type
    # 业务ID
    ywid = request.GET.ywid
    return render_to_string("kf_ywgl/kf_ywgl_005/kf_ywgl_005_dbts.html", {'nodeid': nodeid, 'type': type, 'ywid': ywid})

@register_url('GET')
def dbts_ys_data_view():
    """
    # 单步调试要素
    """
    # 交易ID/子流程ID
    lcid = request.GET.lcid
    # 节点ID
    nodeid = request.GET.nodeid
    # 节点类型（'strat_jy':交易开始节点，'strat_zlc':子流程开始节点，'end_jy':交易结束节点，'end_zlc':子流程结束节点，'jd':节点，'zlc':子流程）
    type = request.GET.type
    # 类别 1输入要素，2输出要素，3返回值
    lb = request.GET.lb
    params = {'lcid': lcid, 'nodeid': nodeid, 'type': type, 'lb': lb}
    
    data = {'total': 0, 'rows': []}
    try:
        data = dbts_ys_data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('GET')
def dbts_bz_data_view():
    """
    # 获取其他步骤
    """
    # 节点ID
    nodeid = request.GET.nodeid
    # 要素类型（'1':输入要素，'2':输出要素）
    lx = request.GET.lx
    params = {'nodeid': nodeid, 'lx': lx}
    
    data = {'bz': [], 'ys': {}}
    try:
        data = dbts_bz_data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('GET')
def djbjd_data_view():
    """
    # 获取打解包节点
    """
    # 类型 'jb'：解包，'db'：打包
    lx = request.GET.lx
    # 交易ID
    jyid = request.GET.jyid
    params = {'lx': lx, 'jyid': jyid}
    
    data = []
    try:
        data = djbjd_data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('POST')
def set_djbjd_view():
    """
    # 设置打解包节点
    """
    # 类型 'jb'：解包，'db'：打包
    lx = request.POST.lx
    # 流程ID
    lcid = request.POST.lcid
    # 流程编码
    lcbm = request.POST.lcbm
    # 打解包节点ID
    jdid = request.POST.jdid
    params = {'lx': lx, 'lcid': lcid, 'lcbm': lcbm, 'jdid': jdid}
    
    result = {'state': False, 'msg': ''}
    try:
        result = set_djbjd_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)

@register_url('GET')
def get_ywsjb_view():
    """
    # 获取业务数据表
    """
    # 业务ID
    ywid = request.GET.ywid
    
    data = []
    try:
        data = get_ywsjb_service(ywid)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('GET')
def demo_jbxx_data_view():
    """
    # 获取Demo基本数据
    """
    # 业务ID
    ywid = request.GET.ywid
    # demo名称
    mc = request.GET.mc
    # demo 描述
    ms = request.GET.ms
    # 计算rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    params = {'ywid': ywid, 'rn_start':rn_start, 'rn_end':rn_end, 'mc':mc, 'ms':ms}
    
    data = {'rows': [], 'total': 0}
    try:
        data = demo_jbxx_data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('POST')
def demo_jbxx_data_add_view():
    """
    # 新增Demo基本信息
    """
    # Demo基本信息ID
    id = request.POST.id
    # Demo基本信息名称
    mc = request.POST.mc
    # Demo基本信息描述
    ms = request.POST.ms
    # 业务ID
    ywid = request.POST.ywid
    params = {'id': id, 'mc': mc, 'ms': ms, 'ssywid': ywid}
    
    data = {'state': False, 'msg': ''}
    try:
        data = demo_jbxx_data_add_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增Demo数据失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(data)

@register_url('POST')
def demo_jbxx_data_del_view():
    """
    # 删除Demo基本信息和数据
    """
    # Demo基本信息ID
    id = request.POST.id
    
    data = {'state': False, 'msg': ''}
    try:
        data = demo_jbxx_data_del_service(id)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除Demo数据失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(data)

@register_url('GET')
def demo_sj_data_view():
    """
    # 获取Demo数据
    """
    # Demo基本信息ID
    demojbxxid = request.GET.demojbxxid
    # 数据表简称
    sjbmc = request.GET.sjbmc
    params = {'demojbxxid': demojbxxid, 'sjbmc': sjbmc}
    
    data = {'columns': [], 'rows': [], 'total': 0, 'sjid_xssx': []}
    try:
        data = demo_sj_data_service(params)
    except:
        logger.info(traceback.format_exc())
    return json.dumps({'total': data['total'], 'rows': data['rows'], 'sjid_xssx': data['sjid_xssx']})

@register_url('POST')
def demo_sj_data_add_view():
    """
    # 新增Demo数据
    """
    # Demo基本信息ID
    demojbxxid = request.GET.demojbxxid
    # 数据表简称
    sjbjc = request.GET.sjbjc
    # 数据表中文名称
    sjbms = request.GET.sjbms
    # 数据
    data = {}
    for zdm, zdz in request.POST.items():
        # 去掉前边的'name_'，并转为大写
        zdm_upper = zdm[5:].upper()
        data[zdm_upper] = request.POST.getunicode(zdm)
    params = {'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'sjbms': sjbms, 'data': data}
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_sj_data_add_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '新增失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_sj_data_pladd_view():
    """
    # 新增Demo数据
    """
    # Demo基本信息ID
    demojbxxid = request.forms.demojbxxid
    # 数据表简称
    sjbjc = request.forms.sjbjc
    # 数据表中文名称
    sjbms = request.forms.sjbms
    # sql语句
    sql = request.forms.sql
    params = {'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'sjbms': sjbms, 'sql': sql}
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_sj_data_pladd_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '插入失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_sj_data_edit_view():
    """
    # 编辑Demo数据
    """
    # Demo数据上级ID
    sjid = request.GET.sjid
    # 显示顺序
    xssx = request.GET.xssx
    # 数据
    data = {}
    for zdm, zdz in request.POST.items():
        # 去掉前边的'name_'，并转为大写
        zdm_upper = zdm[5:].upper()
        data[zdm_upper] = request.POST.getunicode(zdm)
    params = {'sjid': sjid, 'xssx': xssx, 'data': data}
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_sj_data_edit_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '编辑失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_sj_data_del_view():
    """
    # 删除Demo数据
    """
    # Demo基本信息ID
    demojbxxid = request.GET.demojbxxid
    # 数据表简称
    sjbjc = request.GET.sjbjc
    # 数据 [[sjid, xssx], [sjid, xssx], ...]
    data = json.loads(request.POST.data)
    params = {'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'data': data}
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_sj_data_del_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '删除失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_execute_view():
    """
    # 执行单步测试
    """
    # 业务ID
    ywid = request.POST.ywid
    # Demo基本信息ID
    demojbxxid = request.POST.demojbxxid
    # 节点ID
    nodeid = request.POST.nodeid
    # 交易ID/子流程ID
    lcid = request.POST.lcid
    # 节点类型（'strat':开始节点，'end':结束节点，'jd':节点，'zlc':子流程）
    type = request.POST.type
    # 流程类型 lc/zlc
    lx = request.POST.lx
    # 输入要素字典
    srys = json.loads(request.POST.srys)
    params = {'ywid': ywid, 'demojbxxid': demojbxxid, 'nodeid': nodeid, 'lcid': lcid, 'type': type, 'lx': lx, 'srys': srys}
    result = {'state': False, 'msg': '', 'trans_dict': {}}
    try:
        result = demo_execute_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '执行失败！异常错误提示信息：<br>%s' % error_msg.replace('\n', '<br>')
    
    return json.dumps(result)

@register_url('GET')
def demo_log_view():
    """
    # 获取单步调试日志
    """
    # Log流水号
    log_lsh = request.GET.log_lsh
    
    result = {'state': False, 'msg': '', 'log': ''}
    try:
        result = demo_log_service([log_lsh])
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取Log失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_log_all_view():
    """
    # 获取全部日志
    """
    # Log流水号列表
    rzkeys = json.loads(request.POST.rzkeys)
    
    result = {'state': False, 'msg': '', 'log': ''}
    try:
        result = demo_log_service(rzkeys)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取Log失败！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_save_step_view():
    """
    # 保存当前步骤
    """
    # 当前步骤ID
    bzid = request.POST.bzid
    # 已保存过的步骤ID
    bzid_old = request.POST.bzid_old
    # 输入要素
    srys = json.loads(request.POST.srys)
    # 输出要素
    scys = json.loads(request.POST.scys)
    # 类型 jd节点，zlc子流程
    lx = request.POST.lx
    # 所属定义ID 节点ID/子流程ID
    nodeid = request.POST.nodeid
    # 返回值
    fhz = request.POST.fhz
    # 步骤名称
    mc = request.POST.mc
    # 步骤描述
    ms = request.POST.ms
    # 是否跳过
    sftg = request.POST.sftg
    # Demo基本信息ID
    demoid = request.POST.demoid
    # Log流水号
    log_lsh = request.POST.log_lsh
    params = {'bzid': bzid, 'bzid_old': bzid_old, 'srys': srys, 'scys': scys, 'lx': lx, 'nodeid': nodeid, 'fhz': fhz, 'mc': mc, 'ms': ms, 'sftg': sftg, 'demoid': demoid, 'log_lsh': log_lsh}
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_save_step_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存当前步骤失败，无法进行步骤跳转！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)

@register_url('POST')
def demo_del_step_view():
    """
    # 删除保存的步骤
    """
    # 要删除的步骤ID列表
    bzids_old = json.loads(request.POST.bzids_old)
    
    result = {'state': False, 'msg': ''}
    try:
        result = demo_del_step_service(bzids_old)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '步骤删除失败，无法进行步骤跳转！异常错误提示信息[%s]' % error_msg
    
    return json.dumps(result)

@register_url('GET')
def dbtsjl_view():
    """
    # 查看单步调试记录
    """
    # 流程ID
    lcid = request.GET.lcid
    # 类型 lc流程，zlc子流程
    lx = request.GET.lx
    # 布局ID列表（按执行的顺序排列）
    bz_bjids = request.GET.bz_bjids.split(',')
    # 步骤ID列表（顺序和布局ID列表一一对应）
    bzids = request.GET.bzids.split(',')
    
    data = {'zxbz': []}
    try:
        data = dbtsjl_service(lcid, lx, bz_bjids, bzids)
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_005/kf_ywgl_005_dbtsjl.html", data)

@register_url('POST')
def del_dbts_view():
    """
    # 删除单步调试产生的数据
    """
    # 步骤ID列表
    bzids = json.loads(request.POST.bzids)
    # DemoID列表
    demoids = json.loads(request.POST.demoids)
    
    result = {'state': False, 'msg': ''}
    try:
        result = del_dbts_service(bzids, demoids)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def save_jdcsal_view():
    """
    # 保存为节点测试案例
    """
    # 测试案例名称
    mc = request.POST.mc
    # 测试案例描述
    ms = request.POST.ms
    # 节点ID/子流程ID
    nodeid = request.POST.nodeid
    # 业务ID
    ywid = request.POST.ywid
    # 流程ID
    lcid = request.POST.lcid
    # Demo ID
    demoid = request.POST.demoid
    # 步骤ID
    bzid = request.POST.bzid
    # 日志流水号
    rzlsh = request.POST.rzlsh
    # 类别 1:交易测试案例 2:子流程测试案例 3:节点测试案例 4:通讯子流程测试案例
    lb = request.POST.lb
    # 节点类别 'jd'节点 'zlc'子流程
    type = request.POST.type
    params = {'mc': mc, 'ms': ms, 'nodeid': nodeid, 'ywid': ywid, 'lcid': lcid, 'demoid': demoid, 'bzid': bzid, 'rzlsh': rzlsh, 'lb': lb, 'type': type}
    
    result = {'state': False, 'msg': ''}
    try:
        result = save_jdcsal_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def save_csal_view():
    """
    # 保存为测试案例
    """
    # 业务ID
    ywid = request.POST.ywid
    # 测试案例名称
    mc = request.POST.mc
    # 测试案例描述
    ms = request.POST.ms
    # 交易ID/子流程ID
    lcid = request.POST.lcid
    # 类型 lc 流程，zlc 子流程
    lx = request.POST.lx
    # Demo ID列表
    demoids = json.loads(request.POST.demoids)
    # 步骤ID列表
    bzids = json.loads(request.POST.bzids)
    params = {'ywid': ywid, 'mc': mc, 'ms': ms, 'lx': lx, 'lcid': lcid, 'demoids': demoids, 'bzids': bzids}
    
    result = {'state': False, 'msg': ''}
    try:
        result = save_csal_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def get_node_fhz_view():
    """
    # 获取节点返回值
    """
    # 节点/子流程ID
    nodeid = request.POST.nodeid
    # 类型（'jd'节点 'zlc'子流程）
    type = request.POST.type
    
    result = {'state': False, 'msg': '', 'fhz': []}
    try:
        result = get_node_fhz_service(nodeid, type)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '返回值获取失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def get_czpz_view():
    """
    # 查询冲正配置
    """
    # 冲正配置类型
    czpzlx = request.POST.czpzlx
    
    result = {'state': False, 'msg': '', 'czpz_lst': []}
    try:
        result = get_czpz_service( czpzlx )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '返回值获取失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def czpz_sub_view():
    """
    # 冲正配置提交
    """
    # 冲正配置id
    czpzid = request.POST.czpzid
    # 节点id
    nodeid = request.POST.nodeid
    # 步骤id
    bzid = request.POST.bzid
    # 类型
    type = request.POST.type
    # 业务id
    ywid = request.POST.ywid
    # 交易2子流程类型
    lx = request.POST.lx
    # 交易2子流程id
    jy2zlcid = request.POST.jy2zlcid
    
    result = {'state': False, 'msg': ''}
    try:
        data_dic = { 'czpzid': czpzid, 'nodeid': nodeid, 'bzid': bzid, 
                    'type': type, 'ywid': ywid, 'lx': lx, 'jy2zlcid': jy2zlcid }
        result = czpz_sub_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '返回值获取失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
    
    
    
    
    
    