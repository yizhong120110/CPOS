# -*- coding: utf-8 -*-
# Action: 通讯管理-通讯管理 主页面 view
# Author: zhangchl
# AddTime: 2015-01-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request,render_to_string
from .kf_txgl_001_service import ( 
    data_service, data_add_sel_service, data_add_bytxlx_txwj_service, data_add_service, data_del_service,
    txxq_jbxx_service, txxq_jbxx_edit_service, txxq_csgl_data_service, txxq_csgl_add2edit_sel_service,
    txxq_csgl_add_service, txxq_csgl_edit_service, txxq_csgl_del_service,
    txxq_cdtx_data_service, txxq_cdtx_add2edit_sel_service, txxq_cdtx_add2edit_dbjb_service, txxq_cdtx_add_service,
    txxq_cdtx_edit_service, txxq_cdtx_del_service, txxq_jymjchs_service,
    txxq_jymjchs_sub_service, txxq_jymjchs_testzx_service,
    txxq_cdtx_yydb_service, txxq_cdtx_yydb_data_service, txxq_cdtx_yydb_add2edit_sel_service,
    txxq_cdtx_yydb_add_service, txxq_cdtx_yydb_edit_service, txxq_cdtx_yydb_del_service,
    txxq_cdtx_yydb_sel_service, txxq_cdtx_yydb_del_sel_service,
    txxq_cdtx_testdb_data_service, txxq_cdtx_testdb_query_service,
    txxq_cdtx_csal_service, txxq_cdtx_csal_data_service, txxq_cdtx_csal_add2edit_sel_service,
    txxq_cdtx_csal_add_service, txxq_cdtx_csal_edit_service, txxq_cdtx_csal_del_service,
    txxq_cdtx_jkjy_qyjy_sel_service, txxq_cdtx_jkjy_qyjy_sel_data_service, txxq_cdtx_jkjy_qyjy_service,
    txxq_cdtx_jkjy_qyjy_jdys_sel_service, txxq_cdtx_jkjy_qyjy_jdys_service,dr_data_service, txxq_cdtx_czpz_service )


@register_url('GET')
def index_view():
    """
    # 通讯管理-通讯管理展示
    """
    return render_to_string("kf_txgl/kf_txgl_001/kf_txgl_001.html")

@register_url('GET')
def data_view():
    """
    # 通讯管理-通讯管理展示 列表初始化
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        txbm = request.GET.txbm
        txmc = request.GET.txmc
        fwfx = request.GET.fwfx
        txlx = request.GET.txlx
        txwdmc = request.GET.txwdmc
        # 组织调用函数字典
        data_dic = { 'rn_start': rn_start, 'rn_end': rn_end,'txbm':txbm,'txmc':txmc,'fwfx':fwfx if fwfx !='0' else '' ,'txlx':txlx,'txwdmc':txwdmc}
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('GET')
def data_add_sel_view():
    """
    # 通讯管理-通讯管理 新增 页面初始化参数查询
    """
    # 服务方向( 1（客户端） 2（服务端） )
    fwfx = request.POST.fwfx
    
    # 初始化反馈信息
    # cssj: 超时时间
    # txlx_lst: 通讯类型下拉列表数据
    # txwjmc_lst: 通讯文件名称下拉列表数据
    result = {'state':False,'cssj':'', 'txlx_lst': [{'value': '', 'ms': '', 'text': '请选择'}]}
    try:
        result = data_add_sel_service( { 'fwfx': fwfx } )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_add_bytxlx_txwj_view():
    """
    # 新增或编辑通讯时，根据通讯类型获取通讯文件列表
    """
    # 通讯类型
    txlxbm = request.POST.txlx
    # 服务方向
    fwfx = request.POST.fwfx
    
    # 初始化反馈信息
    # txwjmc_lst: 通讯文件名称下拉列表数据
    result = {'state':False,'txwjmc_lst':[]}
    try:
        result = data_add_bytxlx_txwj_service( { 'txlxbm': txlxbm, 'fwfx': fwfx } )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取通讯文件名称列表出错！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_add_view():
    """
    # 通讯管理-通讯管理 新增 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 通讯编码
        txbm = request.forms.txbm
        # 通讯名称
        txmc = request.forms.txmc
        # 通讯类型
        txlx = request.forms.txlx
        # 服务方向
        fwfx = request.forms.fwfx
        # 通讯文件名称
        txwjmc = request.forms.txwjmc
        # 超时时间
        cssj = request.forms.cssj
        # 进程并发数
        jcbfs = request.forms.jcbfs
        # 组织调用函数字典
        data_dic = { 'txbm': txbm,
            'txmc': txmc, 'txlx': txlx,
            'fwfx': fwfx, 'txwjmc': txwjmc,
            'cssj': cssj, 'jcbfs': jcbfs }
        # 调用操作数据库函数
        result = data_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 通讯管理-通讯管理 删除 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 通讯id
        txid = request.forms.txid
        # 通讯名称
        txmc = request.forms.txmc
        # 服务方向 （ 1（客户端） 2（服务端） ）
        fwfx = request.forms.fwfx
        # 通讯编码
        txbm = request.forms.txbm
        # 组织调用函数字典
        data_dic = { 'txid': txid, 'txmc': txmc, 'fwfx': fwfx, 'txbm': txbm }
        # 调用操作数据库函数
        result = data_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def txxq_view():
    """
    # 通讯管理-通讯详细信息
    """
    txid = request.GET.txid
    # 服务方向 1（客户端） 2（服务端）
    fwfx = request.GET.fwfx
    data = { 'txid': txid, 'fwfx': fwfx, 'title_mc': 'C端通讯管理' }
    if fwfx == '2':
        data['title_mc'] = '交易码解出函数'
    
    return render_to_string( "kf_txgl/kf_txgl_001/kf_txgl_001_txxq.html", data )

@register_url('GET')
def txxq_jbxx_view():
    """
    # 通讯管理-通讯详细信息-基本信息 view
    """
    # 初始化反馈信息
    tx_dic = {'txid': '', 'bm': '', 'mc': '', 'txlx': '', 'fwfx': '', 
    'txwjmc': '', 'cssj': '', 'jcjymjyid': '', 'jcjymjymc': ''}
    data = { 'tx_dic':tx_dic, 'txlx_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'txwjmc_lst':[],
        'state': False, 'msg': '' }
    
    try:
        # 通讯id
        txid = request.GET.txid
        # 组织调用函数字典
        data_dic = { 'txid': txid }
        # 调用操作数据库函数
        data = txxq_jbxx_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    return render_to_string( 'kf_txgl/kf_txgl_001/kf_txgl_001_txxq_jbxx.html', data )

@register_url('POST')
def txxq_jbxx_edit_view():
    """
    # 通讯管理-通讯基本信息 编辑 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 通讯id
        txid = request.forms.txid
        # 通讯名称
        txmc = request.forms.txmc
        # 通讯类型
        txlx = request.forms.txlx
        # 服务方向
        fwfx = request.forms.fwfx
        # 通讯文件名称
        txwjmc = request.forms.txwjmc
        # 超时时间
        cssj = request.forms.cssj
#        # 交易码解出交易
#        jymjcjy = request.forms.jymjcjy
        # 进程并发数
        jcbfs = request.forms.jcbfs
        # 组织调用函数字典
        data_dic = { 'txid': txid, 'mc': txmc, 'txlx': txlx, 'fwfx': fwfx, 'txwjmc': txwjmc,
                    'cssj': cssj, 'jcbfs': jcbfs }
        # 调用操作数据库函数
        result = txxq_jbxx_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('GET')
def txxq_csgl_data_view():
    """
    # 通讯参数数据表格列表数据获取 view
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 通讯ID
        txid = request.GET.txid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        # 参数定义表 lx(类型 1:系统参数 2:业务参数 3:交易参数 4:通讯参数)
        data_dic = { 'lx': '4', 'ssid': txid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = txxq_csgl_data_service( data_dic )
        
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def txxq_csgl_add2edit_sel_view():
    """
    # 参数新增2编辑页面初始化 view
    """
    # 参数ID
    csid = request.POST.csid
    
    # 初始化反馈信息
    result = {'state':False, 'msg':'','csxx_dic': {}}
    try:
        result = txxq_csgl_add2edit_sel_service( { 'id': csid } )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_csgl_add_view():
    """
    # 通讯参数 新增 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 所属ID
        ssid = request.forms.ssid
        # 参数代码
        csdm = request.forms.csdm
        # 参数值
        csz = request.forms.csz
        # 参数描述
        csms = request.forms.csms
        # 参数状态
        cszt = request.forms.cszt
        # 组织调用函数字典
        data_dic = { 'lx': '4', 'ssid': ssid,
            'csdm': csdm, 'value': csz,
            'csms': csms, 'zt': cszt }
        # 调用操作数据库函数
        result = txxq_csgl_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_csgl_edit_view():
    """
    # 通讯参数 编辑 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 参数id
        csid = request.forms.csid
        # 参数值
        csz = request.forms.csz
        # 参数描述
        csms = request.forms.csms
        # 参数状态
        cszt = request.forms.cszt
        # 组织调用函数字典
        data_dic = { 'id': csid, 'value': csz,
            'csms': csms, 'zt': cszt }
        # 调用操作数据库函数
        result = txxq_csgl_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_csgl_del_view():
    """
    # 通讯参数 删除 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 删除列表
        ids = request.forms.ids
        # 所属id
        ssid = request.forms.ssid
        txbm = request.forms.txbm
        txmc = request.forms.txmc
        # 组织调用函数字典
        data_dic = { 'id_lst': ids.split(','), 'ssid': ssid, 'txbm': txbm, 'txmc': txmc }
        # 调用操作数据库函数
        result = txxq_csgl_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def txxq_cdtx_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 主页面 view
    """
    # 通讯ID
    txid = request.GET.txid
    data = {'txid':txid}
    data['ywdb_lst'] = [{'bm':'','mc':'请选择'},{'bm':'0','mc':'有'},{'bm':'1','mc':'无'}]
    data['jkjy_lst'] = [{'bm':'','mc':'请选择'},{'bm':'0','mc':'禁用'},{'bm':'1','mc':'启用'}]
    return render_to_string("kf_txgl/kf_txgl_001/kf_txgl_001_txxq_cdtx.html", data)
    
@register_url('GET')
def txxq_cdtx_data_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 数据表格初始化 view
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 通讯ID
        txid = request.GET.txid
        # 编码
        bm = request.GET.bm
        # 对方交易名称
        dfjymc = request.GET.dfjymc
        # 对方交易码
        dfjym = request.GET.dfjym
        # 打包
        db = request.GET.db
        # 解包
        jb = request.GET.jb
        # 有无挡板
        ywdb = request.GET.ywdb
        # 接口校验
        jkjy = request.GET.jkjy
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'txid': txid, 'bm': bm, 'dfjymc': dfjymc, 'dfjym': dfjym, 'db': db, 'jb': jb, 'ywdb': ywdb, 'jkjy': jkjy, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = txxq_cdtx_data_service( data_dic )
        
    except:
        logger.info(traceback.format_exc())
    
    return data
    
@register_url('POST')
def txxq_cdtx_add2edit_sel_view():
    """
    # C端管理新增2编辑页面初始化 view
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'','cdtxjbxx_dic': {},
                'yw_lst': [] }
    try:
        # C端通讯id
        cdtxid = request.POST.cdtxid
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid }
        result = txxq_cdtx_add2edit_sel_service( data_dic )
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_add2edit_dbjb_view():
    """
    # C端管理新增2编辑页面初始化 打包解包配置 view
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'','jbjd_lst': [],'yw_lst': [] }
    try:
        result = txxq_cdtx_add2edit_dbjb_service( {} )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_add_view():
    """
    # 通讯管理-C端通讯管理 新增
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 通讯id
        txglid = request.forms.txid
        # C端通讯编码
        bm = request.forms.bm
        # 对方交易码
        dfjym = request.forms.dfjym
        # 对方交易名称
        dfjymc = request.forms.dfjymc
        # 超时时间
        cssj = request.forms.cssj
        # 打包配置
        dbjdid = request.forms.dbjdid
        # 解包配置
        jbjdid = request.forms.jbjdid
        # 所属业务
        ssywid = request.forms.ssywid
        # 冲正配置id
        czzlcdyid = request.forms.czpzid
        # 组织调用函数字典
        data_dic = { 'txglid': txglid, 'bm': bm,
            'dfjym': dfjym, 'dfjymc': dfjymc,
            'cssj': cssj, 'dbjdid': dbjdid, 'jbjdid': jbjdid,
            'ssywid': ssywid, 'czzlcdyid': czzlcdyid }
        # 调用操作数据库函数
        result = txxq_cdtx_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_edit_view():
    """
    # 通讯管理-C端通讯管理 编辑 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 子流程定义id
        zlcdyid = request.forms.zlcdyid
        # 对方交易码
        dfjym = request.forms.dfjym
        # 对方交易名称
        dfjymc = request.forms.dfjymc
        # 超时时间
        cssj = request.forms.cssj
        # 打包配置
        ydbjdid = request.forms.ydbjdid
        dbjdid = request.forms.dbjdid
        # 解包配置
        yjbjdid = request.forms.yjbjdid
        jbjdid = request.forms.jbjdid
        # 所属业务ID
        ssywid = request.forms.ssywid
        # 冲正配置id
        czzlcdyid = request.forms.czpzid
        # 组织调用函数字典
        data_dic = { 
            'cdtxid': cdtxid, 'zlcdyid': zlcdyid, 'dfjym': dfjym, 'dfjymc': dfjymc, 
            'cssj': cssj, 'ydbjdid': ydbjdid, 'dbjdid': dbjdid,
            'yjbjdid': yjbjdid, 'jbjdid': jbjdid, 'ssywid': ssywid,
            'czzlcdyid': czzlcdyid
        }
        # 调用操作数据库函数
        result = txxq_cdtx_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_del_view():
    """
    # C端通讯 删除 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 子流程定义id
        zlcdyid = request.forms.zlcdyid
        # 编码
        bm = request.forms.bm
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'zlcdyid': zlcdyid, 'bm': bm }
        # 调用操作数据库函数
        result = txxq_cdtx_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def txxq_jymjchs_view():
    """
    # 服务方 交易码检查函数 显示信息
    """
    # 通讯ID
    txid = request.GET.txid
    # 反馈信息
    data = { 'txid': txid, 'jcjymhsid': '', 'nr': '' }
    try:
        # 组织调用函数字典
        data_dic = { 'txid': txid }
        # 调用操作数据库函数
        data = txxq_jymjchs_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string( "kf_txgl/kf_txgl_001/kf_txgl_001_txxq_jymjchs.html", data )
    
@register_url('POST')
def txxq_jymjchs_sub_view():
    """
    # 服务方 交易码检查函数 保存 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':'', 'jcjymhsid': ''}
    try:
        # 通讯id
        txid = request.forms.txid
        # 内容
        nr = request.forms.hsnr
        # 组织调用函数字典
        data_dic = { 'txid': txid, 'nr': nr }
        # 调用操作数据库函数
        result = txxq_jymjchs_sub_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '保存失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_jymjchs_testzx_view():
    """
    # 服务方 交易码检查函数 test 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 通讯id
        txid = request.forms.txid
        # 解出交易码函数id
        jcjymhsid = request.forms.jcjymhsid
        # 报文
        bw = request.forms.bw
        # 组织调用函数字典
        data_dic = { 'txid': txid, 'jcjymhsid': jcjymhsid, 'bw': bw }
        # 调用操作数据库函数
        result = txxq_jymjchs_testzx_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '核心执行异常！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def txxq_cdtx_yydb_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 应用挡板 主页面 view
    """
    # 反馈信息
    # 通讯ID
    cdtxid = request.GET.cdtxid
    data = {'cdtxid':cdtxid, 'dbssid':'', 'dblx':'', 'zlcdyid': ''}
    try:
        # 组织调用函数字典
        data_dic = { 'id': cdtxid }
        # 调用操作数据库函数
        data = txxq_cdtx_yydb_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_txgl/kf_txgl_001/kf_txgl_001_txxq_cdtx_yydb.html", data)

@register_url('GET')
def txxq_cdtx_yydb_data_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 应用挡板 data 数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 通讯ID
        cdtxid = request.GET.cdtxid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = txxq_cdtx_yydb_data_service( data_dic )
        
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def txxq_cdtx_yydb_add2edit_sel_view():
    """
    # 应用挡板 新增或编辑获取初始化页面数据
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'','yydb_dic': {},
                'scys_lst': [] }
    try:
        # C端通讯id
        cdtxid = request.POST.cdtxid
        # 挡板d
        dbid = request.POST.dbid
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'dbid': dbid }
        result = txxq_cdtx_yydb_add2edit_sel_service( data_dic )
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_yydb_add_view():
    """
    # 应用挡板 新增 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 简称
        jc = request.forms.jc
        # 挡板名称
        mc = request.forms.mc
        # 挡板描述
        ms = request.forms.ms
        # 返回值
        fhz = request.forms.fhz
        # 要素信息( { id|ysmc:ysz,id|ysmc:ysz,…… } )
        ysxx_str = json.loads(request.forms.ysxx_str)
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'jc': jc,
            'mc': mc, 'ms': ms,
            'fhz': fhz, 'ysxx_str': ysxx_str }
        # 调用操作数据库函数
        result = txxq_cdtx_yydb_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_yydb_edit_view():
    """
    # 应用挡板 编辑 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 挡板id
        dbid = request.forms.dbid
        # 挡板名称
        mc = request.forms.mc
        # 挡板描述
        ms = request.forms.ms
        # 返回值
        fhz = request.forms.fhz
        # 要素信息( { id|ysmc:ysz,id|ysmc:ysz,…… } )
        ysxx_str = json.loads(request.forms.ysxx_str)
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'dbid': dbid,
            'mc': mc, 'ms': ms,
            'fhz': fhz, 'ysxx_str': ysxx_str }
        # 调用操作数据库函数
        result = txxq_cdtx_yydb_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_yydb_del_view():
    """
    # 应用挡板 删除 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 删除挡板id
        dbid = request.forms.dbid
        # 删除挡板简称
        jc = request.forms.jc
        # 删除挡板名称
        mc = request.forms.mc
        # 组织调用函数字典
        data_dic = { 'dbid': dbid, 'jc': jc, 'mc': mc}
        # 调用操作数据库函数
        result = txxq_cdtx_yydb_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_yydb_sel_view():
    """
    # 应用挡板 选择挡板 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 选择挡板id( dbssid|dblx )
        dbid = request.forms.dbid
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 组织调用函数字典
        data_dic = { 'dbssid': dbid.split('|')[0], 'dblx': dbid.split('|')[1], 'cdtxid': cdtxid}
        # 调用操作数据库函数
        result = txxq_cdtx_yydb_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '选择失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_yydb_del_sel_view():
    """
    # 应用挡板 删除选择的挡板 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid}
        # 调用操作数据库函数
        result = txxq_cdtx_yydb_del_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除选择挡板失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('GET')
def txxq_cdtx_testdb_data_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例挡板 data 数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 子流程定义id
        zlcdyid = request.GET.zlcdyid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'zlcdyid': zlcdyid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = txxq_cdtx_testdb_data_service( data_dic )
        
    except:
        logger.info(traceback.format_exc())
    
    return data
    
@register_url('POST')
def txxq_cdtx_testdb_query_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例挡板 跳过输出信息 数据
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'', 'fhz': '',
                'scys_lst': [] }
    try:
        # 返回值
        fhz = request.POST.fhz
        # 节点测试案例执行步骤id
        jdcsalzxbzid = request.POST.jdcsalzxbzid
        # 组织调用函数字典
        data_dic = { 'jdcsalzxbz': jdcsalzxbzid, 'lx': '2' }
        result = txxq_cdtx_testdb_query_service( data_dic )
        result['fhz'] = fhz
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
        
    return result
    
@register_url('GET')
def txxq_cdtx_csal_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例 主页面 view
    """
    # 反馈信息 ( 对方交易名称、子流程ID、所属业务ID、C端通讯ID )
    # 通讯ID
    cdtxid = request.GET.cdtxid
    data = {'cdtxid':cdtxid, 'dfjymc':'', 'zlcdyid': '', 'ssywid': ''}
    try:
        # 组织调用函数字典
        data_dic = { 'id': cdtxid }
        # 调用操作数据库函数
        data = txxq_cdtx_csal_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_txgl/kf_txgl_001/kf_txgl_001_txxq_cdtx_csal.html", data)
    
@register_url('GET')
def txxq_cdtx_csal_data_view():
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例 data 数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 通讯ID
        zlcdyid = request.GET.zlcdyid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'zlcdyid': zlcdyid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = txxq_cdtx_csal_data_service( data_dic )
        
    except:
        logger.info(traceback.format_exc())
    
    return data
    
@register_url('POST')
def txxq_cdtx_csal_add2edit_sel_view():
    """
    # 测试案例 新增或编辑获取初始化页面数据
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'','cdal_dic': {},
                'srys_lst': [], 'scys_lst': [], 'ywmc': '' }
    try:
        # C端通讯id
        cdtxid = request.POST.cdtxid
        # 所属业务id
        ssywid = request.POST.ssywid
        # 测试案例id
        csalid = request.POST.csalid
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'ywid': ssywid, 'csaldyid': csalid }
        result = txxq_cdtx_csal_add2edit_sel_service( data_dic )
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_csal_add_view():
    """
    # 测试案例 新增 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 所属业务id
        ssywid = request.forms.ssywid
        # 子流程定义id
        zlcdyid = request.forms.zlcdyid
        # 测试案例名称
        mc = request.forms.mc
        # 测试案例描述
        ms = request.forms.ms
        # 输入要素信息( id|ysdm|ysz,id|ysdm|ysz,…… )
        ysxx_sr_str = request.forms.ysxx_sr_str
        # 输出要素信息( id|ysdm|ysz,id|ysdm|ysz,…… )
        ysxx_sc_str = request.forms.ysxx_sc_str
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'ssywid': ssywid, 'zlcdyid': zlcdyid,
            'mc': mc, 'ms': ms,
            'ysxx_sr_str': ysxx_sr_str, 'ysxx_sc_str': ysxx_sc_str }
        # 调用操作数据库函数
        result = txxq_cdtx_csal_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def txxq_cdtx_csal_edit_view():
    """
    # 测试案例 编辑 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 测试案例id
        csalid = request.POST.csalid
        # 测试案例描述
        ms = request.forms.ms
        # 输入要素信息( id|ysdm|ysz,id|ysdm|ysz,…… )
        ysxx_sr_str = request.forms.ysxx_sr_str
        # 组织调用函数字典
        data_dic = { 'csaldyid': csalid, 'ms': ms, 'ysxx_sr_str': ysxx_sr_str }
        # 调用操作数据库函数
        result = txxq_cdtx_csal_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_csal_del_view():
    """
    # 测试案例 删除 提交 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 删除列表
        ids = request.forms.ids
        # 测试案例名称列表
        ids_mc = request.forms.ids_mc
        # 组织调用函数字典
        data_dic = { 'id_lst': ids.split(','), 'ids_mc': ids_mc }
        # 调用操作数据库函数
        result = txxq_cdtx_csal_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def txxq_cdtx_jkjy_qyjy_sel_view():
    """
    # C端通讯 接口校验 启用禁用 页面初始化数据准备
    """
    # 反馈信息
    # 通讯ID
    cdtxid = request.GET.cdtxid
    data = {'cdtxid': cdtxid, 'ssyw': '', 'ssjk': '', 'zt': ''}
    try:
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid }
        # 调用操作数据库函数
        data = txxq_cdtx_jkjy_qyjy_sel_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_txgl/kf_txgl_001/kf_txgl_001_txxq_cdtx_jkjy.html", data)

@register_url('GET')
def txxq_cdtx_jkjy_qyjy_sel_data_view():
    """
    # C端通讯 接口校验 启用禁用 页面初始化数据准备 data 数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 通讯ID
        cdtxid = request.GET.cdtxid
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid }
        # 调用操作数据库函数
        data = txxq_cdtx_jkjy_qyjy_sel_data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def txxq_cdtx_jkjy_qyjy_view():
    """
    # C端通讯 接口校验 启用禁用 页面提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # C端通讯id
        cdtxid = request.forms.cdtxid
        # 接口启用状态
        jkqyzt = request.forms.jkqyzt
        # 组织调用函数字典
        data_dic = { 'cdtxid': cdtxid, 'jkqyzt': jkqyzt }
        # 调用操作数据库函数
        result = txxq_cdtx_jkjy_qyjy_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_jkjy_qyjy_jdys_sel_view():
    """
    # C端通讯 接口校验 节点要素编辑 页面初始化
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg':'','zddm': '', 'zdmc': '',
                'sfjkjy': '', 'jygzmc': 'zjcs', 'jygz_lst': {} }
    
    try:
        # C端通讯id
        jdysid = request.POST.jdysid
        # 组织调用函数字典
        data_dic = { 'jdysid': jdysid }
        result = txxq_cdtx_jkjy_qyjy_jdys_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def txxq_cdtx_jkjy_qyjy_jdys_view():
    """
    # C端通讯 接口校验 节点要素编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 节点要素id
        jdysid = request.forms.jdysid
        # 是否校验
        jkjy = request.forms.jkjy
        # 校验规则名称
        ssgzmc = request.forms.jygzmc
        if ssgzmc == '请选择':
            ssgzmc = ''
        # 追加参数
        zjcs = request.forms.zjcs
        # 组织调用函数字典
        data_dic = { 'jdysid': jdysid, 'jkjy': jkjy if jkjy else '0', 'ssgzmc': ssgzmc, 'zjcs': zjcs }
        # 调用操作数据库函数
        result = txxq_cdtx_jkjy_qyjy_jdys_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result


@register_url('GET')
def dr_data_view():
    """
    # 通讯管理-获取导入窗口中下拉框数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        data = dr_data_service( )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def txxq_cdtx_czpz_view():
    """
    # 获取所属业务对应的通讯子流程
    """
    # 反馈信息
    result = {'state':False, 'msg':'', 'czpz_lst': []}
    try:
        # 所属业务id
        ssywid = request.POST.ssywid
        # 子流程id
        zlcdyid = request.POST.zlcdyid
        # 组织调用函数字典
        data_dic = { 'ssywid': ssywid, 'zlcdyid': zlcdyid }
        # 调用操作数据库函数
        result = txxq_cdtx_czpz_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取业务下通讯子流程异常！异常错误提示信息[%s]' % error_msg
    
    return result

