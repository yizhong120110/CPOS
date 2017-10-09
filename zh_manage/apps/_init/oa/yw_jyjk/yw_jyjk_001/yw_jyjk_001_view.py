# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: zhangchl
# AddTime: 2015-04-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json, os
from sjzhtspj import logger, request, render_to_string, TMPDIR, response
from sjzhtspj.common import get_strftime2
from .yw_jyjk_001_service import ( index_service, data_service, workflow_service, lcrzck_service, check_jdlx_service, 
                                    jdrzck_service, lctlb_zlcrzck_service, yxxjyls_ck_service, dbjyls_ck_service )

@register_url('GET')
def index_view():
    """
    # 交易监控 主页面
    """
    # 平台
    pt = request.GET.pt
    # 初始化反馈前台信息
    data = { 'zt_lst': [], 'pt': pt, 'xtlx': '' }
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
    # 转到交易监控列表页面
    return render_to_string( "yw_jyjk/yw_jyjk_001/yw_jyjk_001.html", data )

@register_url('POST')
def data_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 平台
        pt = request.POST.pt
        # 交易日期
        jyrq = request.POST.jyrq
        jyrq = jyrq.replace('-','')
        # 交易名称
        jymc = request.POST.jymc
        # 交易码
        jym = request.POST.jym
        # 流水状态
        lszt = request.POST.lszt
        # 机构码
        jgdm = request.POST.jgdm
        # 流水号
        lsh = request.POST.lsh
        # 卡号/账号
        khzh = request.POST.khzh
        # 第三方账号
        shzh = request.POST.shzh
        # 柜员号
        gyh = request.POST.gyh
        # 业务编码
        ywbm = request.POST.ywbm
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'pt': pt, 'jyrq': jyrq, 'jymc': jymc, 'jym': jym, 'lszt': lszt, 'jgdm': jgdm, 'lsh': lsh, 'khzh': khzh, 'shzh': shzh, 'gyh': gyh, 'ywbm': ywbm, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('GET')
def rzck_view():
    """
    # 交易日志查看 主页面
    # 请求信息：交易日期、流水号、交易码、流程类型（交易）、流程层级（交易码）、交易名称
    """
    # 交易id
    jyid = request.GET.jyid
    # 交易日期
    jyrq = request.GET.jyrq
    # 流水号
    lsh = request.GET.lsh
    # 交易码
    jym = request.GET.jym
    # 流程类型
    lclx = request.GET.lclx
    # 流程层级
    lccj = request.GET.lccj
    lccj = lccj if lccj else ''
    # 交易名称
    jymc = request.GET.jymc
    # 流程日志
    sys_run_trace = request.GET.sys_run_trace
    # 初始化反馈前台信息
    data = { 'jyid': jyid, 'jyrq': jyrq, 'lsh': lsh, 'jym': jym, 'lclx': lclx, 'lccj': lccj, 'jymc': jymc, 'sys_run_trace': sys_run_trace }
    
    # 转到日志查看页面
    return render_to_string( "yw_jyjk/yw_jyjk_001/yw_jyjk_001_rzck.html", data )

@register_url('POST')
def workflow_view():
    """
    # 交易流水日志查看组织流程图书架 view
    """
    # 返回对象
    result = []
    try:
        # 交易id
        jyid = request.POST.jyid
        # 交易日期
        jyrq = request.POST.jyrq
        # 流水号
        lsh = request.POST.lsh
        # 交易码
        jym = request.POST.jym
        # 流程类型( lc: 交易， zlc：子流程 )
        lclx = request.POST.lclx
        # 流程层级
        lccj = request.POST.lccj
        # 交易名称
        jymc = request.POST.jymc
        # 流程日志
        sys_run_trace = request.POST.sys_run_trace
        # 请求信息
        sql_data = { 'jyid': jyid, 'jyrq': jyrq, 'lsh': lsh, 'jym': jym, 'lclx': lclx, 'lccj': lccj, 'jymc': jymc, 'sys_run_trace': sys_run_trace }
        # 查询数据库数据
        result = workflow_service( sql_data )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    return json.dumps(result)

@register_url('POST')
def lcrzck_view():
    """
    # 查看流程日志
    """
    # 初始化反馈信息
    # rznr： 日志内容
    result = { 'state':False, 'msg': '', 'rznr':'' }
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 流水号
        lsh = request.POST.lsh
        # 流程类型
        lclx = request.POST.lclx
        # 流程层级
        lccj = request.POST.lccj
        # 组织查询字典
        sql_data = { 'jyrq': jyrq, 'lsh': lsh, 'lclx': lclx, 'lccj': lccj }
        result = lcrzck_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取日志失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def lcrzck_down_view():
    """
    # 下载流程日志
    """
    # 初始化反馈信息
    # rznr： 日志内容
    result = { 'state':False, 'msg': '', 'rznr':'' }
    try:
        # 交易日期
        jyrq = request.GET.jyrq
        # 流水号
        lsh = request.GET.lsh
        # 流程类型
        lclx = request.GET.lclx
        # 流程层级
        lccj = request.GET.lccj
        # 组织查询字典
        sql_data = { 'jyrq': jyrq, 'lsh': lsh, 'lclx': lclx, 'lccj': lccj }
        # 获取log日志
        result = lcrzck_service( sql_data )
        # 根据反馈日志写文档
        timedate = get_strftime2()
        # 日志文件名称
        dow_fname = filename = '%s_%s.log' % ( timedate, lsh )
        # 日志全路径（ 放到临时文件中 ）
        filepath = os.path.join(TMPDIR,filename)
        # 创建文件对象，写文件
        fileobj = open(filepath, 'w')
        fileobj.write( result['rznr'] )
        fileobj.close()
        # 将文件反馈给前台进行下载
        # 下载文件名称（ filename ）
        # 下载文件路径
        root = TMPDIR
        import time ,datetime
        # 设置cookie名称fileDownload，值为true，路径是根目录/
        response.set_cookie("fileDownload", "true", path="/")
        # return "<script>window.parent.$.messager.alert('提示', '不允许下载', 'info');</script>"
        response.set_header('Content-Type','image/jpeg')
        root = os.path.abspath(root) + os.sep
        filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
        stats = os.stat(filename)
        response.set_header('Content-Length' ,stats.st_size)
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
        response.set_header('Last-Modified', lm)
        response.set_header('Date', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
        response.set_header("Accept-Ranges", "bytes")
        download = os.path.basename(filename)
        import urllib
        response.set_header('Content-Disposition', 'attachment; filename="%s"' % urllib.parse.quote(dow_fname))
        # 下载文件
        return open(filename, 'rb')
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        return render_string( "<script>alert('下载失败！%s');</script>" % error_msg )
    
    return render_string( "<script>alert('下载失败！');</script>" )

@register_url('POST')
def check_jdlx_view():
    """
    # 验证节点类型是否是系统预设节点
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '' }
    try:
        # 节点id
        jdid = request.POST.jdid
        # 组织请求字典
        sql_data = { 'jdid': jdid }
        # 调用数据库操作函数
        result = check_jdlx_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '验证节点是否是系统预设节点出现异常！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def jdrzck_view():
    """
    # 节点日志查看
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '', 'srys_lst': [], 'scys_lst': [], 'rznr': '' }
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 流水号
        lsh = request.POST.lsh
        # 节点id
        jdid = request.POST.jdid
        # 节点编码
        jdbm = request.POST.jdbm
        # 节点是否是开始节点类型
        jdlx_start = request.POST.jdlx_start
        # 流程走向
        lczx = json.loads( request.POST.lczx )
        # 子流程字典
        zlc_dic = json.loads( request.POST.zlc_dic )
        # 流程类型
        lclx = request.POST.lclx
        # 流程层级
        lccj = request.POST.lccj
        # 组织请求字典
        sql_data = {'jyrq': jyrq, 'lsh': lsh, 'jdid': jdid, 'jdbm': jdbm, 'jdlx_start': jdlx_start, 'lczx': lczx, 'zlc_dic': zlc_dic, 'lclx': lclx, 'lccj': lccj }
        
        # 调用数据库操作函数
        result = jdrzck_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取节点详情出现异常！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def lctlb_view():
    """
    # 流程图列表查看
    """
    data = { 'jyrq': '', 'lsh': '', 'lczx': '', 'zlc_dic': '', 'connector1': '', 
            'lclx': '', 'lccj': '' }
    try:
        # 交易日期、流水号、lczx结构、zlc_dic数据结构、connector1、流程类型、流程层级
        # 交易日期
        data['jyrq'] = request.GET.jyrq
        # 流水号
        data['lsh'] = request.GET.lsh
        # lczx结构
        data['lczx'] = request.GET.lczx
        # zlc_dic数据结构
        data['zlc_dic'] = request.GET.zlc_dic
        # connector1
        data['connector1'] = ''
        connector1 = request.GET.connector1
        if connector1:
            data['connector1'] = json.loads( connector1 )
        # connector1 str
        data['connector1_str'] = request.GET.connector1
        # 流程类型
        data['lclx'] = request.GET.lclx
        # 流程层级
        data['lccj'] = request.GET.lccj
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
    
    return render_to_string( "yw_jyjk/yw_jyjk_001/yw_jyjk_001_rzck_lctlb.html", data )

@register_url('GET')
def lctlb_jdrzck_view():
    """
    # 流程图列表 节点输入、输出、日志查看
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '', 'srys_lst': [], 'scys_lst': [], 'rznr': '' }
    try:
        # 交易日期
        jyrq = request.GET.jyrq
        # 流水号
        lsh = request.GET.lsh
        # 节点id
        jdid = request.GET.jdid
        # 节点编码
        jdbm = request.GET.jdbm
        # 节点是否是开始节点类型
        jdlx_start = request.GET.jdlx_start
        # 流程走向
        lczx = json.loads( request.GET.lczx )
        # 子流程字典
        zlc_dic = json.loads( request.GET.zlc_dic )
        # 流程类型
        lclx = request.GET.lclx
        # 流程层级
        lccj = request.GET.lccj
        # 组织请求字典
        sql_data = {'jyrq': jyrq, 'lsh': lsh, 'jdid': jdid, 'jdbm': jdbm, 'jdlx_start': jdlx_start, 'lczx': lczx, 'zlc_dic': zlc_dic, 'lclx': lclx, 'lccj': lccj }
        
        # 调用数据库操作函数
        result = jdrzck_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取节点详情出现异常！异常错误提示信息[%s]' % error_msg
    
    return render_to_string( "yw_jyjk/yw_jyjk_001/yw_jyjk_001_rzck_lctlb_jdxx.html", result )

@register_url('GET')
def lctlb_zlcrzck_view():
    """
    # 流程图列表 子流程输入、输出、日志查看
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '', 'srys_lst': [], 'scys_lst': [], 'rznr': '' }
    try:
        # 交易日期
        jyrq = request.GET.jyrq
        # 流水号
        lsh = request.GET.lsh
        # 节点id
        jdid = request.GET.jdid
        # 节点编码
        jdbm = request.GET.jdbm
        # 节点是否是开始节点类型
        jdlx_start = request.GET.jdlx_start
        # 流程走向
        lczx = json.loads( request.GET.lczx )
        # 子流程字典
        zlc_dic = json.loads( request.GET.zlc_dic )
        # 流程类型
        lclx = request.GET.lclx
        # 流程层级
        lccj = request.GET.lccj
        # 组织请求字典
        sql_data = {'jyrq': jyrq, 'lsh': lsh, 'jdid': jdid, 'jdbm': jdbm, 'jdlx_start': jdlx_start, 'lczx': lczx, 'zlc_dic': zlc_dic, 'lclx': lclx, 'lccj': lccj }
        
        # 调用数据库操作函数
        result = lctlb_zlcrzck_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取子流程详情出现异常！异常错误提示信息[%s]' % error_msg
    
    return render_to_string( "yw_jyjk/yw_jyjk_001/yw_jyjk_001_rzck_lctlb_jdxx.html", result )

@register_url('POST')
def yxxjyls_ck_view():
    """
    # 有效性校验流水查看data view
    """
    # 初始化反馈信息
    data = {'state': False, 'msg': '', 'total':0, 'rows':[]}
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 交易名称
        lsh = request.POST.lsh
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'jyrq': jyrq, 'lsh': lsh, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = yxxjyls_ck_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取数据出现异常！异常错误提示信息[%s]' % error_msg
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def dbjyls_ck_view():
    """
    # 挡板校验流水查看data view
    """
    # 初始化反馈信息
    data = {'state': False, 'msg': '', 'total':0, 'rows':[]}
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 交易名称
        lsh = request.POST.lsh
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'jyrq': jyrq, 'lsh': lsh, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = dbjyls_ck_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取数据出现异常！异常错误提示信息[%s]' % error_msg
    
    # 将组织的结果反馈给前台
    return data