# -*- coding: utf-8 -*-
# Action: 监控管理-监控配置
# Author: zhangchl
# AddTime: 2015-05-06
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_jkgl_006_service import ( index_service, data_service, jkpz_add2upd_sel_service, jkpz_add_service, jkpz_upd_service
                                ,jkpz_gzcs_sel_service, jkpz_gzcs_add2edit_service, jkpz_del_service, jkpz_qyjy_service
                                ,data_xydz_service, xydz_add2upd_sel_service, xydz_crcs_init_service, xydz_add_service, xydz_upd_service
                                ,xydz_del_service, xydz_csck_sel_service)
@register_url('GET')
def index_view():
    """
    # 监控配置 主页面
    """
    # 平台
    pt = request.GET.pt
    # 初始化反馈前台信息
    data = { 'fxgz_lst': [{'id':'','zwmc':'请选择'}], 'yjjb_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'sfbf_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'zt_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'pt': pt }
    try:
        # 组织请求信息字典
        sql_data = { 'pt': pt }
        # 调用数据库操作函数
        data = index_service( sql_data )
        # 将对应平台反馈给前台
        data['pt'] = pt
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到监控配置列表页面
    return render_to_string( "yw_jkgl/yw_jkgl_006/yw_jkgl_006.html", data )

@register_url('POST')
def data_view():
    """
    # 监控配置列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 平台
        pt = request.POST.pt
        # 名称
        mc = request.POST.mc
        # 分析规则
        gzid = request.POST.gzid
        # 预警级别
        yjjb = request.POST.yjjb
        # 是否可并发
        sfkbf = request.POST.sfkbf
        # 状态
        zt = request.POST.zt
        # 分页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'pt': pt, 'mc': mc, 'gzid': gzid, 'yjjb': yjjb, 'sfkbf': sfkbf, 'zt': zt, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def jkpz_add2upd_sel_view():
    """
    # 监控配置新增、编辑获取页面初始化数据
    """
    # 平台
    pt = request.POST.pt
    # 编辑监控配置id
    jkpzid = request.POST.jkpzid
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'fxgz_lst': [{'id':'','zwmc':'请选择'}],
            'yjjb_lst': [{'value': '', 'ms': '', 'text': '请选择'}],
            'sfbf_lst': [{'value': '', 'ms': '', 'text': '请选择'}],
            'zxzj_lst':[{'id':'sjdev','zwmc':'请选择'}],
            'jkpz_dic': {} }
    try:
        # 组织请求信息字典
        sql_data = { 'pt': pt, 'jkpzid': jkpzid }
        # 调用数据库操作函数
        data = jkpz_add2upd_sel_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def jkpz_add_view():
    """
    # 新增提交 view
    """
    # 平台
    pt = request.forms.pt
    # 名称
    mc = request.forms.jkpzMc
    # 分析规则
    gzid = request.forms.jkpzFxgz
	# 执行主机
    zxzj = request.forms.zxzj
    # 分析规则名称
    gzmc = request.forms.gzmc
    # 预警级别
    yjjb = request.forms.jkpzYjjb
    # 预警级别名称
    yjjbmc = request.forms.yjjbmc
    # crontab配置
    zdfqpz = request.forms.jkpzZdfqpz
    # 是否可并发
    sfkbf = request.forms.jkpzSfkbf
    # 是否可并发名称
    sfkbfmc = request.forms.sfkbfmc
    # crontab说明
    zdfqpzsm = request.forms.jkpzZdfqpzsm
    # 状态 '0'禁用 '1'启用
    zt = request.forms.zt
    # 描述
    ms = request.forms.jkpzMs
    # 请求信息
    sql_data = { 'pt': pt, 'mc': mc,'gzid': gzid,'gzmc': gzmc,'yjjb': yjjb,'yjjbmc': yjjbmc,'zdfqpz': zdfqpz,'sfkbf': sfkbf,'sfkbfmc': sfkbfmc, 'zdfqpzsm': zdfqpzsm, 'zt': zt, 'ms': ms,'zxzj':zxzj }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = jkpz_add_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result
    
@register_url('POST')
def jkpz_upd_view():
    """
    # 编辑提交 view
    """
    # 编辑监控配置id
    jkpzid = request.forms.jkpzid
    # 平台
    pt = request.forms.pt
    # 名称
    mc = request.forms.jkpzMc
    # 分析规则
    gzid = request.forms.jkpzFxgz
	# 执行主机
    zxzj = request.forms.zxzj
    # 分析规则名称
    gzmc = request.forms.gzmc
    # 预警级别
    yjjb = request.forms.jkpzYjjb
    # 预警级别名称
    yjjbmc = request.forms.yjjbmc
    # crontab配置
    zdfqpz = request.forms.jkpzZdfqpz
    # 是否可并发
    sfkbf = request.forms.jkpzSfkbf
    # 是否可并发名称
    sfkbfmc = request.forms.sfkbfmc
    # crontab说明
    zdfqpzsm = request.forms.jkpzZdfqpzsm
    # 状态 '0'禁用 '1'启用
    zt = request.forms.zt
    # 描述
    ms = request.forms.jkpzMs
    # 请求信息
    sql_data = { 'jkpzid': jkpzid, 'pt': pt, 'mc': mc, 'gzid': gzid, 'gzmc': gzmc, 'yjjb': yjjb, 'yjjbmc': yjjbmc,
                'zdfqpz': zdfqpz,'sfkbf': sfkbf,'sfkbfmc': sfkbfmc, 'zdfqpzsm': zdfqpzsm, 'zt': zt, 'ms': ms,'zxzj':zxzj }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = jkpz_upd_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def jkpz_gzcs_sel_view():
    """
    # 编辑规则参数，页面初始化view
    """
    # 监控配置id
    jkpzid = request.POST.jkpzid
    # 规则id
    gzid = request.POST.gzid
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'gzmc': '', 'gzms': '', 'gzcs_lst': [], 'ycsxx_str': '' }
    try:
        # 组织请求信息字典
        sql_data = { 'jkpzid': jkpzid, 'gzid': gzid }
        # 调用数据库操作函数
        data = jkpz_gzcs_sel_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def jkpz_gzcs_add2edit_view():
    """
    # 编辑规则参数，新增或编辑提交 view
    """
    # 编辑监控配置id
    jkpzid = request.forms.gzcsJkpzid
    # 规则id
    gzid = request.forms.gzcsGzid
    # 原参数值集合字符串
    ycsxx_str = request.forms.ycsxxStr
    # 参数集合字符串( 传入参数id~参数对应表~参数代码~参数说明~参数值&传入参数id~参数对应表~参数代码~参数说明~参数值 )
    crcs_str = request.forms.crcs_str
    # 请求信息
    sql_data = { 'ssid':jkpzid, 'jkpzid': jkpzid, 'gzid': gzid, 'ycsxx_str': ycsxx_str, 'crcs_str': crcs_str }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = jkpz_gzcs_add2edit_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑规则参数失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def jkpz_del_view():
    """
    # 监控配置删除
    """
    # 监控配置删除id列表
    jkpzid_str = request.POST.ids
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        sql_data = { 'jkpzidlst': jkpzid_str.split(',') }
        result = jkpz_del_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除监控分析配置失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def jkpz_qyjy_view():
    """
    # 监控配置启用禁用 view
    """
    # 监控配置id列表
    jkpzid_str = request.POST.ids
    # 启用禁用标识
    qyjy_type = request.POST.qyjy_type
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        sql_data = { 'jkpzidlst': jkpzid_str.split(','), 'qyjy_type': qyjy_type }
        result = jkpz_qyjy_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '%s监控分析配置失败！异常错误提示信息[%s]' % ( '启用' if qyjy_type == '1' else '禁用', error_msg )
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def data_xydz_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 监控配置id
        jkpzid = request.POST.jkpzid
        # 分页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'jkpzid': jkpzid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_xydz_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def xydz_add2upd_sel_view():
    """
    # 响应动作新增、编辑获取页面初始化数据
    """
    # 平台
    pt = request.POST.pt
    # 响应动作id
    xydzid = request.POST.xydzid
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'xydz_lst': [], 'fxjgcf_lst': [], 'fqfs_lst': [], 'dzzxzj_lst': [], 'xydzcs_lst': [], 'xydz_dic': {} }
    try:
        # 组织请求信息字典
        sql_data = { 'pt': pt, 'xydzid': xydzid }
        # 调用数据库操作函数
        data = xydz_add2upd_sel_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def xydz_crcs_init_view():
    """
    # 获取响应动作对应的传入参数 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 响应动作id
        dzid = request.POST.dzid
        # 编辑响应动作id
        xydzid = request.POST.xydzid
        
        # 组织调用函数字典
        data_dic = { 'dzid': dzid, 'xydzid': xydzid }
        # 调用操作数据库函数
        data = xydz_crcs_init_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def xydz_add_view():
    """
    # 响应动作新增提交 view
    """
    # 平台
    pt = request.forms.pt
    # 所属监控分析id
    ssjkfxid = request.forms.ssjkfxid
    # 动作id
    dzid = request.forms.xydzXydz
    # 动作名称
    dzmc = request.forms.dzmc
    # 分析触发结果
    fxjgcf = request.forms.xydzFxjgcf
    # 分析触发结果名称
    fxjgcfmc = request.forms.fxjgcfmc
    # 发起方式
    fqfs = request.forms.xydzFqfs
    # 发起方式名称
    fqfsmc = request.forms.fqfsmc
    # 计划时间
    jhsj = request.forms.xydzJhsj
    # 动作执行主机
    dzzxzj = request.forms.dzzxzj
    dzzxzjmc = request.forms.dzzxzjmc.replace('请选择,','')
    # 传入参数
    crcs_str = request.forms.crcs_str
    # 请求信息
    sql_data = { 'pt': pt, 'ssjkfxid': ssjkfxid, 'dzid': dzid, 'dzmc': dzmc, 'fxjgcf': fxjgcf, 'fxjgcfmc': fxjgcfmc,
                'fqfs': fqfs, 'fqfsmc': fqfsmc, 'jhsj': jhsj, 'dzzxzj': dzzxzj, 'dzzxzjmc': dzzxzjmc, 'crcs_str': crcs_str }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = xydz_add_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result
    
@register_url('POST')
def xydz_upd_view():
    """
    # 编辑提交 view
    """
    # 编辑监控配置id
    xydzid = request.forms.xydzid
    # 平台
    pt = request.forms.pt
    # 所属监控分析id
    ssjkfxid = request.forms.ssjkfxid
    # 动作id
    dzid = request.forms.xydzXydz
    # 动作名称
    dzmc = request.forms.dzmc
    # 分析触发结果
    fxjgcf = request.forms.xydzFxjgcf
    # 分析触发结果名称
    fxjgcfmc = request.forms.fxjgcfmc
    # 发起方式
    fqfs = request.forms.xydzFqfs
    # 发起方式名称
    fqfsmc = request.forms.fqfsmc
    # 计划时间
    jhsj = request.forms.xydzJhsj
    # 动作执行主机
    zxzjstr = request.forms.zxzjstr
    zxzjmcstr = request.forms.zxzjmcstr
    dzzxzj = request.forms.dzzxzj
    dzzxzjmc = request.forms.dzzxzjmc.replace('请选择,','')
    # 传入参数
    crcs_str = request.forms.crcs_str
    # 原传入参数
    xydzycsxxstr = request.forms.xydzycsxxstr
    # 请求信息
    sql_data = {'xydzid': xydzid, 'pt': pt, 'ssjkfxid': ssjkfxid, 'dzid': dzid, 'dzmc': dzmc, 'fxjgcf': fxjgcf, 'fxjgcfmc': fxjgcfmc,
    'fqfs': fqfs, 'fqfsmc': fqfsmc, 'jhsj': jhsj, 'zxzjstr': zxzjstr, 'zxzjmcstr': zxzjmcstr, 'dzzxzj': dzzxzj, 'dzzxzjmc': dzzxzjmc, 
    'crcs_str': crcs_str, 'xydzycsxxstr': xydzycsxxstr }
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        result = xydz_upd_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def xydz_del_view():
    """
    # 响应动作删除
    """
    # 响应动作删除id列表
    xydzid_str = request.POST.ids
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 调用数据库操作函数
        sql_data = { 'xydzidlst': xydzid_str.split(',') }
        result = xydz_del_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除响应动作失败！异常错误提示信息[%s]' % error_msg
    # 将得到的结果反馈给前台
    return result

@register_url('POST')
def xydz_csck_sel_view():
    """
    # 响应动作传入参数查看
    """
    # 响应动作id
    xydzid = request.POST.xydzid
    # 动作id
    dzid = request.POST.dzid
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '','xydzcs_lst': [] }
    try:
        # 组织请求信息字典
        sql_data = { 'xydzid': xydzid, 'dzid': dzid }
        # 调用数据库操作函数
        data = xydz_csck_sel_service( sql_data )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data